"""
Document Management & Asynchronous Job Processing Service for Universal AI Educator.
Manages secure upload, persistent storage, incremental Neon metadata tracking,
idempotent async extraction jobs, stage-by-stage progress updates, and strict user isolation.
"""

import os
import re
import json
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from db_adapter import get_db
from storage.factory import get_storage_provider
from extractors.factory import get_extractor
from extractors.base import ExtractionResult

log = logging.getLogger("pod_siksha.document_service")

# Validation limits
MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(25 * 1024 * 1024)))  # 25 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".ppt", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "text/plain",
    "text/markdown",
    "application/octet-stream"  # Browser generic upload fallback
}

MAGIC_BYTES = {
    "pdf": b"%PDF-",
    "zip": b"PK\x03\x04"  # DOCX and PPTX are zip archives
}

def sanitize_filename(filename: str) -> str:
    """Strips path traversal sequences and dangerous characters."""
    base = os.path.basename(filename.strip())
    clean = re.sub(r"[^\w\.\-\s]", "_", base)
    return clean[:200] or "document.pdf"

def validate_file(filename: str, file_bytes: bytes, content_type: Optional[str] = None) -> Tuple[bool, str]:
    """Validates file extension, size, and magic bytes."""
    clean_fn = sanitize_filename(filename)
    ext = os.path.splitext(clean_fn)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    if len(file_bytes) == 0:
        return False, "File is empty (0 bytes)."

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        mb = round(MAX_FILE_SIZE_BYTES / (1024 * 1024))
        return False, f"File exceeds maximum upload size limit of {mb}MB."

    # Validate magic bytes
    if ext == ".pdf":
        if not file_bytes.startswith(MAGIC_BYTES["pdf"]):
            return False, "Corrupted PDF file (missing %PDF- header)."
    elif ext in (".docx", ".pptx"):
        if not file_bytes.startswith(MAGIC_BYTES["zip"]):
            return False, f"Corrupted Office file (invalid archive header for {ext})."

    return True, ""


class DocumentService:
    @staticmethod
    def upload_and_create_job(
        user_id: str,
        filename: str,
        file_bytes: bytes,
        content_type: str = "application/pdf"
    ) -> Dict[str, Any]:
        """
        Validates file, writes to persistent storage, creates Neon records for document and job.
        Returns document_id and job_id.
        """
        is_valid, err = validate_file(filename, file_bytes, content_type)
        if not is_valid:
            raise ValueError(err)

        clean_fn = sanitize_filename(filename)
        doc_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # 1. Upload to persistent storage
        storage = get_storage_provider()
        storage_key = f"{doc_id}_{clean_fn}"
        storage_url = storage.upload(
            key=storage_key,
            data=file_bytes,
            content_type=content_type,
            user_id=user_id,
            filename=clean_fn
        )
        provider_name = storage.get_provider_name()

        # 2. Persist metadata in Neon PostgreSQL
        with get_db() as conn:
            conn.execute("""
                INSERT INTO documents (
                    id, user_id, filename, file_type, file_size_bytes,
                    storage_provider, storage_key, storage_url, sha256_hash,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'uploaded', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                doc_id, user_id, clean_fn, content_type or "application/pdf",
                file_size, provider_name, storage_key, storage_url, sha256
            ))

            conn.execute("""
                INSERT INTO document_jobs (
                    id, document_id, user_id, job_type, status,
                    progress_percent, current_stage, retry_count, idempotency_key,
                    created_at, updated_at
                ) VALUES (?, ?, ?, 'extract_and_analyze', 'queued', 10, 'queued', 0, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (job_id, doc_id, user_id, sha256))

        return {
            "document_id": doc_id,
            "job_id": job_id,
            "filename": clean_fn,
            "file_size_bytes": file_size,
            "storage_provider": provider_name,
            "status": "queued",
            "progress_percent": 10
        }

    @staticmethod
    def process_document_job(job_id: str) -> Dict[str, Any]:
        """
        Executes the extraction and analysis pipeline asynchronously.
        Idempotent: updates stages in Neon document_jobs and documents.
        """
        with get_db() as conn:
            cur = conn.execute("SELECT id, document_id, user_id, retry_count, status FROM document_jobs WHERE id = ?", (job_id,))
            job = cur.fetchone()
            if not job:
                raise ValueError(f"Job {job_id} not found")

            doc_id = job["document_id"]
            user_id = job["user_id"]

            cur_doc = conn.execute("SELECT storage_key, filename, file_type FROM documents WHERE id = ?", (doc_id,))
            doc = cur_doc.fetchone()
            if not doc:
                raise ValueError(f"Document {doc_id} not found")

            storage_key = doc["storage_key"]
            filename = doc["filename"]

        def update_stage(stage: str, progress: int, status: str = "in_progress", err: Optional[str] = None, summary: Optional[str] = None):
            with get_db() as conn:
                conn.execute("""
                    UPDATE document_jobs SET
                        status = ?,
                        current_stage = ?,
                        progress_percent = ?,
                        error_message = ?,
                        result_summary = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, stage, progress, err, summary, job_id))

        try:
            # Stage 1: Download from persistent storage
            update_stage("downloading_storage", 15)
            storage = get_storage_provider()
            file_bytes = storage.download(f"{user_id}/{storage_key}")

            # Stage 2: Extract text and structure
            update_stage("extracting_structure", 35)
            extractor = get_extractor(filename)
            result: ExtractionResult = extractor.extract(file_bytes, filename, document_id=doc_id)

            # Save sections to Neon
            with get_db() as conn:
                conn.execute("DELETE FROM document_sections WHERE document_id = ?", (doc_id,))
                for sec in result.sections:
                    sec_id = str(uuid.uuid4())
                    conn.execute("""
                        INSERT INTO document_sections (
                            id, document_id, page_number, section_index,
                            section_title, content_type, content, char_count, metadata_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sec_id, doc_id, sec.page_number, sec.section_index,
                        sec.section_title, sec.content_type, sec.content,
                        len(sec.content), json.dumps(sec.metadata)
                    ))

            # Stage 3: Multimodal Analysis (Diagrams, Code, Math)
            update_stage("analyzing_multimodal", 55)
            from extractors.multimodal_extractor import MultimodalDocumentExtractor
            from extractors.code_extractor import ProgrammingCodeExtractor
            from extractors.math_extractor import MathematicalIntelligenceExtractor

            figures = []
            if filename.lower().endswith(".pdf"):
                try:
                    multi_ext = MultimodalDocumentExtractor()
                    multi_res = multi_ext.extract(file_bytes, filename, document_id=doc_id)
                    figures = [s.metadata for s in multi_res.sections if s.content_type == "figure"]
                except Exception as m_err:
                    log.warning("Multimodal analysis note: %s", m_err)

            code_extractor = ProgrammingCodeExtractor()
            code_blocks = code_extractor.process_document(result.sections, document_id=doc_id)

            math_extractor = MathematicalIntelligenceExtractor()
            math_exprs = math_extractor.process_document(result.sections, document_id=doc_id)

            # Stage 4: Pedagogical Concept Extraction & Dependency Graph
            update_stage("extracting_pedagogy", 75)
            from pedagogy.concept_extractor import PedagogicalConceptExtractor
            concept_ext = PedagogicalConceptExtractor()
            concept_graph = concept_ext.extract_concepts_and_graph(
                document_id=doc_id,
                filename=filename,
                sections=result.sections,
                code_blocks=code_blocks,
                math_expressions=math_exprs,
                figures=figures
            )

            # Stage 5: Adaptive Teaching Strategies
            update_stage("generating_teaching_strategies", 90)
            from pedagogy.teaching_strategy_engine import AdaptiveTeachingStrategyEngine
            strategy_engine = AdaptiveTeachingStrategyEngine()
            strategies = strategy_engine.recommend_strategies(
                document_id=doc_id,
                subject=concept_graph.subject,
                concepts=concept_graph.concepts,
                has_code=len(code_blocks) > 0,
                has_math=len(math_exprs) > 0,
                has_figures=len(figures) > 0
            )

            # Stage 6: Update Document Metadata & Mark Completed
            with get_db() as conn:
                conn.execute("""
                    UPDATE documents SET
                        page_count = ?,
                        subject_detected = ?,
                        status = 'completed',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (result.total_pages, concept_graph.subject, doc_id))

            summary_dict = {
                "document_id": doc_id,
                "filename": filename,
                "total_pages": result.total_pages,
                "subject": concept_graph.subject,
                "topic": concept_graph.topic,
                "chapter_title": concept_graph.chapter_title,
                "section_count": len(result.sections),
                "concept_count": len(concept_graph.concepts),
                "relationship_count": len(concept_graph.relationships),
                "code_blocks_count": len(code_blocks),
                "math_expressions_count": len(math_exprs),
                "figures_count": len(figures),
                "strategies_count": len(strategies)
            }
            update_stage("completed", 100, status="completed", summary=json.dumps(summary_dict))

            return {
                "status": "completed",
                "document_id": doc_id,
                "job_id": job_id,
                "total_pages": result.total_pages,
                "subject_detected": concept_graph.subject,
                "summary": summary_dict
            }

        except Exception as e:
            log.error("Job execution failed for job %s: %s", job_id, e)
            err_msg = str(e)
            update_stage("failed", 100, status="failed", err=err_msg)
            with get_db() as conn:
                conn.execute("UPDATE documents SET status = 'failed', error_message = ? WHERE id = ?", (err_msg, doc_id))
            raise

    @staticmethod
    def get_job_status(job_id: str, user_id: str) -> Dict[str, Any]:
        """Fetches job status with user authorization enforcement."""
        with get_db() as conn:
            cur = conn.execute("""
                SELECT id, document_id, user_id, status, progress_percent,
                       current_stage, retry_count, max_retries, result_summary,
                       error_message, created_at, updated_at
                FROM document_jobs WHERE id = ?
            """, (job_id,))
            job = cur.fetchone()
            if not job:
                raise FileNotFoundError(f"Job {job_id} not found")
            if job["user_id"] != user_id:
                raise PermissionError("Access forbidden: you do not own this job")

            cur_doc = conn.execute("SELECT filename, file_size_bytes, status, subject_detected FROM documents WHERE id = ?", (job["document_id"],))
            doc = cur_doc.fetchone()

            summary = json.loads(job["result_summary"]) if job["result_summary"] else None

            return {
                "job_id": job["id"],
                "document_id": job["document_id"],
                "status": job["status"],
                "progress_percent": job["progress_percent"],
                "current_stage": job["current_stage"],
                "retry_count": job["retry_count"],
                "max_retries": job["max_retries"],
                "error_message": job["error_message"],
                "result_summary": summary,
                "filename": doc["filename"] if doc else None,
                "document_status": doc["status"] if doc else None,
                "subject_detected": doc["subject_detected"] if doc else None,
                "updated_at": str(job["updated_at"])
            }

    @staticmethod
    def retry_job(job_id: str, user_id: str) -> Dict[str, Any]:
        """Retries a failed job if under max_retries."""
        with get_db() as conn:
            cur = conn.execute("SELECT id, user_id, retry_count, max_retries, status FROM document_jobs WHERE id = ?", (job_id,))
            job = cur.fetchone()
            if not job:
                raise FileNotFoundError(f"Job {job_id} not found")
            if job["user_id"] != user_id:
                raise PermissionError("Access forbidden: you do not own this job")

            if job["retry_count"] >= job["max_retries"]:
                raise ValueError(f"Job exceeded maximum retry attempts ({job['max_retries']})")

            conn.execute("""
                UPDATE document_jobs SET
                    status = 'queued',
                    current_stage = 'retry_queued',
                    progress_percent = 15,
                    retry_count = retry_count + 1,
                    error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (job_id,))

        return DocumentService.process_document_job(job_id)

    @staticmethod
    def list_user_documents(user_id: str) -> List[Dict[str, Any]]:
        """Returns all active documents owned by the user."""
        with get_db() as conn:
            cur = conn.execute("""
                SELECT d.id, d.filename, d.file_type, d.file_size_bytes,
                       d.page_count, d.subject_detected, d.status, d.error_message,
                       d.created_at, d.updated_at,
                       (SELECT j.id FROM document_jobs j WHERE j.document_id = d.id ORDER BY j.created_at DESC LIMIT 1) as latest_job_id,
                       (SELECT j.status FROM document_jobs j WHERE j.document_id = d.id ORDER BY j.created_at DESC LIMIT 1) as job_status,
                       (SELECT j.progress_percent FROM document_jobs j WHERE j.document_id = d.id ORDER BY j.created_at DESC LIMIT 1) as job_progress
                FROM documents d
                WHERE d.user_id = ? AND d.deleted_at IS NULL
                ORDER BY d.created_at DESC
            """, (user_id,))
            rows = cur.fetchall()

            docs = []
            for r in rows:
                docs.append({
                    "id": r["id"],
                    "filename": r["filename"],
                    "file_type": r["file_type"],
                    "file_size_bytes": r["file_size_bytes"],
                    "page_count": r["page_count"] or 0,
                    "subject_detected": r["subject_detected"] or "General",
                    "status": r["status"],
                    "error_message": r["error_message"],
                    "created_at": str(r["created_at"]),
                    "latest_job_id": r["latest_job_id"],
                    "job_status": r["job_status"],
                    "job_progress": r["job_progress"] or 0
                })
            return docs

    @staticmethod
    def get_document(doc_id: str, user_id: str) -> Dict[str, Any]:
        """Returns document details and extracted sections with user ownership enforcement."""
        with get_db() as conn:
            cur = conn.execute("""
                SELECT id, user_id, filename, file_type, file_size_bytes,
                       storage_provider, storage_key, storage_url,
                       page_count, subject_detected, status, error_message,
                       created_at, updated_at
                FROM documents
                WHERE id = ? AND deleted_at IS NULL
            """, (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise FileNotFoundError(f"Document {doc_id} not found")
            if doc["user_id"] != user_id:
                raise PermissionError("Access forbidden: you do not own this document")

            # Fetch sections
            cur_sec = conn.execute("""
                SELECT id, page_number, section_index, section_title, content_type, content, char_count, metadata_json
                FROM document_sections
                WHERE document_id = ?
                ORDER BY page_number ASC, section_index ASC
            """, (doc_id,))
            sections = []
            for s in cur_sec.fetchall():
                sections.append({
                    "id": s["id"],
                    "page_number": s["page_number"],
                    "section_index": s["section_index"],
                    "section_title": s["section_title"],
                    "content_type": s["content_type"],
                    "content": s["content"],
                    "char_count": s["char_count"],
                    "metadata": json.loads(s["metadata_json"]) if s["metadata_json"] else {}
                })

            return {
                "id": doc["id"],
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "file_size_bytes": doc["file_size_bytes"],
                "storage_provider": doc["storage_provider"],
                "page_count": doc["page_count"] or 0,
                "subject_detected": doc["subject_detected"] or "General",
                "status": doc["status"],
                "error_message": doc["error_message"],
                "created_at": str(doc["created_at"]),
                "sections": sections
            }

    @staticmethod
    def delete_document(doc_id: str, user_id: str) -> bool:
        """Soft-deletes document and invalidates access with user ownership enforcement."""
        with get_db() as conn:
            cur = conn.execute("SELECT id, user_id, storage_key FROM documents WHERE id = ?", (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise FileNotFoundError(f"Document {doc_id} not found")
            if doc["user_id"] != user_id:
                raise PermissionError("Access forbidden: you do not own this document")

            # Soft-delete record
            conn.execute("""
                UPDATE documents SET
                    deleted_at = CURRENT_TIMESTAMP,
                    status = 'deleted',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (doc_id,))

            # Also delete blob from storage provider
            try:
                storage = get_storage_provider()
                storage.delete(f"{user_id}/{doc['storage_key']}")
            except Exception as e:
                log.warning("Storage deletion notice for %s: %s", doc_id, e)

        return True
