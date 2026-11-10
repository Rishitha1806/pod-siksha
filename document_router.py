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
