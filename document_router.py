"""
Document Management API Router for Universal AI Educator.
Exposes endpoints for:
- POST /api/documents/upload: Secure multi-subject file upload and async job scheduling
- GET /api/documents: List user's documents
- GET /api/documents/{doc_id}: Fetch document metadata and parsed sections
- GET /api/documents/jobs/{job_id}: Poll job status and progress
- POST /api/documents/jobs/{job_id}/retry: Retry a failed extraction job
- DELETE /api/documents/{doc_id}: Soft delete and access invalidation
"""

import logging
from typing import Optional
import json
from pydantic import BaseModel
from db_adapter import get_db
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status

from document_service import DocumentService

log = logging.getLogger("pod_siksha.document_router")

router = APIRouter(prefix="/api/documents", tags=["Universal Document Engine"])


def get_auth_user(req: Request) -> dict:
    from server import get_current_user
    auth = req.headers.get("Authorization")
    cookie = req.cookies.get("auth_token")
    return get_current_user(authorization=auth, auth_token=cookie)


@router.post("/upload")
async def upload_document(
    req: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    user = get_auth_user(req)
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        file_bytes = await file.read()
        res = DocumentService.upload_and_create_job(
            user_id=user["id"],
            filename=file.filename,
            file_bytes=file_bytes,
            content_type=file.content_type or "application/pdf"
        )
        job_id = res["job_id"]

        # Enqueue background processing
        background_tasks.add_task(DocumentService.process_document_job, job_id)

        return {
            "status": "success",
            "message": "Document uploaded and processing job scheduled.",
            "document_id": res["document_id"],
            "job_id": res["job_id"],
            "filename": res["filename"],
            "file_size_bytes": res["file_size_bytes"],
            "storage_provider": res["storage_provider"],
            "job_status": res["status"],
            "progress_percent": res["progress_percent"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error("Document upload error: %s", e)
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.get("")
async def list_documents(req: Request):
    user = get_auth_user(req)
    try:
        docs = DocumentService.list_user_documents(user["id"])
        return {
            "status": "success",
            "count": len(docs),
            "documents": docs
        }
    except Exception as e:
        log.error("List documents error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}")
async def get_document(doc_id: str, req: Request):
    user = get_auth_user(req)
    try:
        doc = DocumentService.get_document(doc_id, user["id"])
        return {
            "status": "success",
            "document": doc
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        log.error("Get document error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, req: Request):
    user = get_auth_user(req)
    try:
        job = DocumentService.get_job_status(job_id, user["id"])
        return {
            "status": "success",
            "job": job
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        log.error("Get job status error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: str, background_tasks: BackgroundTasks, req: Request):
    user = get_auth_user(req)
    try:
        # Schedule retry
        background_tasks.add_task(DocumentService.retry_job, job_id, user["id"])
        return {
            "status": "success",
            "message": f"Job {job_id} scheduled for retry."
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error("Retry job error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, req: Request):
    user = get_auth_user(req)
    try:
        DocumentService.delete_document(doc_id, user["id"])
        return {
            "status": "success",
            "message": f"Document {doc_id} deleted successfully."
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        log.error("Delete document error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Phase 2 Multimodal Intelligence & Pedagogical Endpoints
# -------------------------------------------------------------

@router.get("/{doc_id}/concepts")
async def get_document_concepts(doc_id: str, req: Request):
    """Fetches extracted concepts and dependency graph for a document."""
    user = get_auth_user(req)
    doc = DocumentService.get_document(doc_id, user["id"])
    with get_db() as conn:
        concepts = conn.execute("""
            SELECT id, concept_name, concept_type, definition, summary,
                   prerequisites_json, learning_objectives_json, common_confusions_json,
                   examples_json, source_page, confidence
            FROM document_concepts
            WHERE document_id = ?
            ORDER BY source_page ASC, confidence DESC
        """, (doc_id,)).fetchall()

        relationships = conn.execute("""
            SELECT id, from_concept, to_concept, relationship_type, evidence_text, weight
            FROM concept_relationships
            WHERE document_id = ?
        """, (doc_id,)).fetchall()

    return {
        "status": "success",
        "document_id": doc_id,
        "subject": doc.get("subject_detected", "Universal Learning"),
        "concepts": [
            {
                "id": c["id"],
                "name": c["concept_name"],
                "type": c["concept_type"],
                "definition": c["definition"],
                "summary": c["summary"],
                "prerequisites": json.loads(c["prerequisites_json"] or "[]"),
                "learning_objectives": json.loads(c["learning_objectives_json"] or "[]"),
                "common_confusions": json.loads(c["common_confusions_json"] or "[]"),
                "examples": json.loads(c["examples_json"] or "[]"),
                "source_page": c["source_page"],
                "confidence": c["confidence"]
            }
            for c in concepts
        ],
        "relationships": [dict(r) for r in relationships]
    }


@router.get("/{doc_id}/figures")
async def get_document_figures(doc_id: str, req: Request):
    """Fetches multimodal visual diagram analyses."""
    user = get_auth_user(req)
    doc = DocumentService.get_document(doc_id, user["id"])
    with get_db() as conn:
        figures = conn.execute("""
            SELECT id, page_number, figure_index, figure_type, caption,
                   summary, detailed_explanation, visual_labels_json, educational_significance
            FROM document_figures
            WHERE document_id = ?
            ORDER BY page_number ASC, figure_index ASC
        """, (doc_id,)).fetchall()

    return {
        "status": "success",
        "document_id": doc_id,
        "figures": [
            {
                "id": f["id"],
                "page_number": f["page_number"],
                "figure_index": f["figure_index"],
                "type": f["figure_type"],
                "caption": f["caption"],
                "summary": f["summary"],
                "detailed_explanation": f["detailed_explanation"],
                "labels": json.loads(f["visual_labels_json"] or "[]"),
                "educational_significance": f["educational_significance"]
            }
            for f in figures
        ]
    }


@router.get("/{doc_id}/code")
async def get_document_code(doc_id: str, req: Request):
    """Fetches programming code blocks with preserved indentation and algorithm tags."""
    user = get_auth_user(req)
    doc = DocumentService.get_document(doc_id, user["id"])
    with get_db() as conn:
        code_blocks = conn.execute("""
            SELECT id, page_number, language, purpose, code_text, algorithm_name,
                   sample_inputs_json, sample_outputs_json, related_concepts_json
            FROM document_code_blocks
            WHERE document_id = ?
            ORDER BY page_number ASC
        """, (doc_id,)).fetchall()

    return {
        "status": "success",
        "document_id": doc_id,
        "code_blocks": [
            {
                "id": b["id"],
                "page_number": b["page_number"],
                "language": b["language"],
                "purpose": b["purpose"],
                "code_text": b["code_text"],
                "algorithm_name": b["algorithm_name"],
                "sample_inputs": json.loads(b["sample_inputs_json"] or "[]"),
                "sample_outputs": json.loads(b["sample_outputs_json"] or "[]"),
                "related_concepts": json.loads(b["related_concepts_json"] or "[]")
            }
            for b in code_blocks
        ]
    }


@router.get("/{doc_id}/math")
async def get_document_math(doc_id: str, req: Request):
    """Fetches mathematical expressions formatted in LaTeX for KaTeX rendering."""
    user = get_auth_user(req)
    doc = DocumentService.get_document(doc_id, user["id"])
    with get_db() as conn:
        math_exprs = conn.execute("""
            SELECT id, page_number, latex_expr, expression_type, context_text,
                   variables_json, derivation_step
            FROM document_math_expressions
            WHERE document_id = ?
            ORDER BY page_number ASC, derivation_step ASC
        """, (doc_id,)).fetchall()

    return {
        "status": "success",
        "document_id": doc_id,
        "math_expressions": [
            {
                "id": m["id"],
                "page_number": m["page_number"],
                "latex": m["latex_expr"],
                "type": m["expression_type"],
                "context": m["context_text"],
                "variables": json.loads(m["variables_json"] or "{}"),
                "derivation_step": m["derivation_step"]
            }
            for m in math_exprs
        ]
    }


@router.get("/{doc_id}/teaching-strategies")
async def get_document_teaching_strategies(doc_id: str, req: Request):
    """Fetches dynamic teaching strategy recommendations."""
    user = get_auth_user(req)
    doc = DocumentService.get_document(doc_id, user["id"])
    with get_db() as conn:
        strategies = conn.execute("""
            SELECT id, concept_name, recommended_method, rationale,
                   suggested_animation_type, priority, step_plan_json
            FROM teaching_strategies
            WHERE document_id = ?
            ORDER BY priority ASC
        """, (doc_id,)).fetchall()

    return {
        "status": "success",
        "document_id": doc_id,
        "teaching_strategies": [
            {
                "id": s["id"],
                "concept_name": s["concept_name"],
                "method": s["recommended_method"],
                "rationale": s["rationale"],
                "animation_type": s["suggested_animation_type"],
                "priority": s["priority"],
                "step_plan": json.loads(s["step_plan_json"] or "[]")
            }
            for s in strategies
        ]
    }


class LearnConceptRequest(BaseModel):
    concept_name: str
    learner_profile: Optional[str] = "teen"
    language: Optional[str] = "te"


@router.post("/{doc_id}/learn-concept")
async def learn_concept_with_ai(doc_id: str, payload: LearnConceptRequest, req: Request):
    """Generates an adaptive animated visual lesson specifically grounded in a selected concept."""
    user = get_auth_user(req)
    doc = DocumentService.get_document(doc_id, user["id"])

    # Load concept details & sections
    with get_db() as conn:
        c_row = conn.execute("""
            SELECT * FROM document_concepts WHERE document_id = ? AND concept_name = ?
        """, (doc_id, payload.concept_name)).fetchone()

        strat_row = conn.execute("""
            SELECT * FROM teaching_strategies WHERE document_id = ? AND concept_name = ?
        """, (doc_id, payload.concept_name)).fetchone()

        sections = conn.execute("""
            SELECT * FROM document_sections WHERE document_id = ? ORDER BY page_number ASC LIMIT 10
        """, (doc_id,)).fetchall()

    concept_def = c_row["definition"] if c_row else payload.concept_name
    concept_summary = c_row["summary"] if c_row else ""
    teaching_method = strat_row["recommended_method"] if strat_row else "step_by_step"
    anim_type = strat_row["suggested_animation_type"] if strat_row else "educational_2d"

    # Context compilation
    context_text = f"Subject: {doc.get('subject_detected')}. Concept: {payload.concept_name}. Definition: {concept_def}. Summary: {concept_summary}. Strategy: {teaching_method}."

    # Forward to animated lesson generator
    from animated_router import create_animated_project
    project = await create_animated_project(
        title=f"Mastering {payload.concept_name}",
        topic=context_text,
        learner_profile=payload.learner_profile,
        language=payload.language,
        animation_style=anim_type,
        source_type="document_concept",
        content_text=context_text,
        file=None,
        user=user
    )

    return {
        "status": "success",
        "document_id": doc_id,
        "concept_name": payload.concept_name,
        "project": project
    }
