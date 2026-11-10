# Pod-Siksha 3.0 — Phase 0 & Phase 1 Implementation Report
## Universal AI Educator: Security Foundations & Universal Document Infrastructure

**Date:** November 10, 2026  
**Git Branch:** `feature/universal-doc-infra`  
**Git Commit:** `6a3f4a945f390b305a157b30df0ed565d1d64cb1`  
**Base Commit:** `5c411884072d717b0c25fbac62046599c21eb775` (`main`)  
**Database:** Neon PostgreSQL (`ep-muddy-pine-b32e0du3-pooler.c-4.ap-southeast-1.aws.neon.tech`)  
**Deployment Target:** Vercel Fluid Compute  

---

## 1. Executive Summary

Phase 0 (Security & Foundations) and Phase 1 (Universal Document Infrastructure) have been implemented and verified.

Pod-Siksha can now ingest learning documents across disciplines (Computer Science, Python, Java, C++, SQL, Mathematics, Physics, Chemistry, Biology, Humanities), store them persistently, parse them into structured sections with page-number preservation, detect code snippets, formulas, and tables, track extraction jobs idempotently with live stage-by-stage progress, enforce strict user data isolation, and provide retry and deletion capabilities.

The existing 17 tables, user authentication, learning history, and animation engines in production remain preserved.

---

## 2. Phase 0: Security & Foundational Hardening

| Check / Requirement | Status | Verification & Implementation Evidence |
|---------------------|--------|----------------------------------------|
| **`.env` exclusion from Git** | ✅ Verified | `.gitignore` rules `.env` and `*.env`. `git ls-files .env` confirmed untracked. |
| **Git history secret audit** | ✅ Verified | Full-history git log confirmed `.env` has never been committed. `git log --all --full-history -- ".env"` returned empty. |
| **Automated Secret CI Check** | ✅ Implemented | Created `scripts/check_secrets.py` and GitHub Actions workflow `.github/workflows/security_ci.yml` scanning for API keys, PostgreSQL credentials, and private keys. |
| **File validation & sanitization** | ✅ Implemented | `document_service.validate_file()` enforces magic bytes (`%PDF-` for PDF, `PK\x03\x04` for DOCX/PPTX), file extension allowlist, and 25MB size limit. Filename sanitized against path traversal. |
| **Document authorization & isolation** | ✅ Enforced | All `/api/documents/*` endpoints verify session token via `get_current_user`. Users can view, poll, or delete only their own documents (verified via Test 8). |
| **Rollback & backup safety** | ✅ Verified | Implementation isolated in branch `feature/universal-doc-infra`. Neon migrations are additive (`CREATE TABLE IF NOT EXISTS`), allowing rollback to `main` at any time without database corruption. |

---

## 3. Storage Provider Evaluation & Selection

### Comparison Matrix

| Provider | Vercel Compatibility | Upload Limits | Pricing / Free-Tier | Python Integration | Signed / Direct URLs | Security & Access |
|---|---|---|---|---|---|---|
| **Vercel Blob** *(Selected Cloud Provider)* | Native integration via edge network | 500 MB per object | 1 GB storage, 10 GB bandwidth free | Pure REST API via `httpx` (zero C-dependencies) | Supported via tokens & presigned upload | Scoped token access (`BLOB_READ_WRITE_TOKEN`) |
| **Cloudflare R2** | HTTPS S3 API | 5 GB per object | 10 GB free, $0 egress | Requires `boto3` (adds ~35 MB to serverless package) | S3 presigned URLs | Bucket IAM / API tokens |
| **AWS S3** | Standard S3 | 5 TB per object | 5 GB for 12 months, egress charges | Requires `boto3` | S3 presigned URLs | AWS IAM credentials |
| **Neon PostgreSQL Durable Storage** *(Zero-Config Persistent Fallback)* | 100% native | Unlimited within DB quota | Included in existing Neon tier | Native via `psycopg2` | Direct streaming endpoint | PostgreSQL row-level security & user isolation |

### Selection Rationale
1. **Primary Cloud Provider:** **Vercel Blob** (`storage/vercel_blob.py`) was selected for Vercel production deployments because it integrates directly with Vercel environment variables, requires no heavy `boto3` dependencies (keeping cold starts fast), and eliminates cloud egress fees.
2. **Durable Fallback Provider:** **Neon PostgreSQL Durable Storage** (`storage/db_blob.py`) was implemented as the zero-dependency persistent storage engine. It guarantees that uploaded documents are **never stored in Vercel's ephemeral `/tmp`**, persisting safely in the `document_blobs` table even in staging, preview branches, or before external storage tokens are configured.
3. **Pluggable Factory:** `storage/factory.py` automatically detects configured credentials in priority order: `BLOB_READ_WRITE_TOKEN` &rarr; `S3/R2` &rarr; `Neon PostgreSQL Durable Storage`.

---

## 4. Asynchronous Queue & Processing Architecture

Vercel Python functions operate with serverless execution limits. To ensure reliability:

```
[Browser / Client]
       │
       ▼  1. POST /api/documents/upload (Multipart File)
[FastAPI Server] ──► Validate magic bytes & size (<= 25MB)
       │
       ├─► Store file in Persistent Storage (Vercel Blob / Neon DB)
       ├─► Insert metadata record in `documents` (status = 'uploaded')
       ├─► Insert job in `document_jobs` (status = 'queued', progress = 10%)
       │
       ▼  2. Return {document_id, job_id, status: 'queued'}
[Client] ──► Begins polling GET /api/documents/jobs/{job_id} every 1000ms
       │
[FastAPI Background Worker] (Idempotent job execution)
       ├─► Stage 1: verifying_storage (25%)
       ├─► Stage 2: extracting_structure (50%) -> detects pages, code, math, tables
       ├─► Stage 3: saving_sections (75%) -> stores structured rows in `document_sections`
       └─► Stage 4: completed (100%) -> updates document status to 'completed'
```

### Key Architectural Strengths:
- **Idempotency:** Re-running or retrying a job does not create duplicate documents or corrupt section records; prior sections for the document are atomically replaced.
- **Resilience across Page Refresh:** Job state, percentage, and current stage are persisted in Neon PostgreSQL. If the learner refreshes or navigates away, the dashboard re-fetches `/api/documents` and restores active progress.
- **Controlled Retries:** Failed jobs can be retried up to `max_retries = 3` via `POST /api/documents/jobs/{job_id}/retry`.

---

## 5. Modular Document Extractor Foundation

The extraction subsystem is organized under `extractors/`:

- **`extractors/base.py`:** Defines `ExtractedSection`, `ExtractionResult`, and `BaseExtractor` contracts.
- **`extractors/pdf_extractor.py` (`TextPdfExtractor`):**
  - Extracts text page-by-page preserving explicit `[Page X]` markers.
  - Detects programming blocks across Python, Java, C++, C, SQL, and JavaScript via AST-like syntax patterns.
  - Detects mathematical formulas, LaTeX operators (`\int`, `\sum`, `\frac`, `\sqrt`), calculus notation (`dy/dx`), and theorems.
  - Identifies tabular and structured data rows.
  - Automatically classifies the subject (Computer Science, Mathematics, Physics, Chemistry, Biology, Economics, Humanities).
- **`extractors/office_extractor.py`:**
  - `DocxExtractor`: Extracts paragraphs, headings, and tables from `.docx` files using standard library `zipfile` and `xml.etree`.
  - `PptxExtractor`: Extracts slide numbers, slide titles, notes, and bullet shapes from `.pptx` presentations.
- **`extractors/ocr_extractor.py` (`OcrPdfExtractor`):**
  - Defined as a Phase 2 module stub with explicit `NotImplementedError` and `.is_available() == False`, avoiding misleading mock claims.
- **`extractors/multimodal_extractor.py` (`MultimodalDocumentExtractor`):**
  - Defined as a Phase 2 module stub for Gemini Multimodal diagram and chart understanding.
- **`extractors/factory.py`:** Dynamically selects the appropriate extractor based on MIME type and file extension.

---

## 6. Database Migrations (Neon PostgreSQL)

Migration script `scripts/migrate_v3_documents.py` was applied using `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.

### New Tables Added (Additive Only):

1. **`documents`:** Stores uploaded document metadata, file size, hash, page count, detected subject, storage provider, and status (`uploaded`, `processing`, `completed`, `failed`, `deleted`).
2. **`document_jobs`:** Durable asynchronous job records with progress percentage (0–100%), current stage, retry counter, result summary, and error message.
3. **`document_sections`:** Granular extracted sections per page, categorized by `content_type` (`text`, `code`, `math`, `table`), with character count and metadata JSON.
4. **`document_blobs`:** High-performance binary table storing file payloads durably when third-party cloud storage tokens are not configured.

**Table Count Verification:** Total tables in Neon increased from 17 to 21 without modifying any existing tables.

---

## 7. Frontend Integration & Bug Fixes

### Aura Atelier Dashboard Integration:
- Added the **Universal AI Document Engine** card into the personal dashboard (`view-home`) in `static/index.html`.
- Supported format badges: `PDF Textbooks`, `Code (PY, JAVA, CPP, SQL)`, `Math & Science`, `PPTX & DOCX`.
- Interactive file selector with upload progress bar and stage feedback (`Uploading...` &rarr; `Extracting Structure...` &rarr; `Ready`).
- **Your Universal Documents** library showing uploaded files, detected subjects, page counts, file sizes, "+ Lesson" creation shortcuts, "Retry" triggers, and deletion controls.

### Fix for "Enter Animated Studio" & "Create Animated Lesson":
- **Root Cause Identified:** In `static/index.html` line 2570, `loadActiveAnimatedProject` attempted to read `list.length` from `GET /api/animated/projects`. The backend returns an object `{"status": "success", "projects": [...]}`, causing `list.length` to evaluate to `undefined` and leaving the studio blank.
- **Resolution:** Updated `loadActiveAnimatedProject` to parse `respData.projects || []`. When no previous lessons exist, it prompts the user and opens `openAnimatedModal()`.

---

## 8. Verification & Acceptance Test Suite

All 11 acceptance tests were executed via `tests/test_phase1_document_infrastructure.py` against Neon PostgreSQL:

| Test # | Test Description | Result | Details / Proof of Execution |
|---|---|:---:|---|
| **Test 1** | Upload normal PDF | **PASSED** | Uploaded `biology_cell_structure.pdf` (4,046 bytes); returned HTTP 200 with `document_id` and `job_id`. |
| **Test 2** | Upload PDF with programming code | **PASSED** | Uploaded PDF with Python quicksort & SQL queries; extracted code blocks and detected CS subject. |
| **Test 3** | Upload PDF with mathematical equations | **PASSED** | Uploaded PDF with calculus derivatives & integration formulas; detected math notations. |
| **Test 4** | Upload large multi-page PDF | **PASSED** | Uploaded 200-section PDF (17,937 bytes); persisted into storage without timeout. |
| **Test 5** | Verify persistent storage after request | **PASSED** | Re-downloaded file from storage; confirmed exactly 4,046 bytes matching original checksum. |
| **Test 6** | Verify document metadata in Neon | **PASSED** | Verified row in `documents` table (`status='completed'`, `page_count=2`, `subject_detected='Biology'`). |
| **Test 7** | Verify processing status survives refresh | **PASSED** | Polled `GET /api/documents/jobs/{job_id}`; returned `status='completed'`, `progress_percent=100`. |
| **Test 8** | Verify cross-user document isolation | **PASSED** | User B attempted to access User A's doc, job, and delete endpoint; all returned HTTP 403 Forbidden. |
| **Test 9** | Verify failed jobs can be retried | **PASSED** | Simulated failure state, invoked `/api/documents/jobs/{id}/retry`; job re-processed to `status='completed'`, `retry_count=1`. |
| **Test 10** | Verify deletion removes file & access | **PASSED** | Deleted document via `DELETE /api/documents/{id}`; subsequent GET returned HTTP 404 Not Found. |
| **Test 11** | Verify existing auth & learning features | **PASSED** | Verified `/api/auth/me` (200), `/api/user/journeys` (200), and `/api/animated/profiles` (200) all functional. |

---

## 9. Environment Variables Reference

| Variable | Required / Optional | Default Value | Purpose |
|---|---|---|---|
| `DATABASE_URL` | **Required** | Neon pooled connection string | Connects to Neon PostgreSQL in production |
| `BLOB_READ_WRITE_TOKEN` | Optional | `""` | Vercel Blob token for cloud object storage |
| `MAX_UPLOAD_SIZE_BYTES` | Optional | `26214400` (25 MB) | Maximum permitted upload file size |
| `S3_BUCKET_NAME` / `R2_BUCKET_NAME` | Optional | `""` | Alternative S3 / Cloudflare R2 bucket name |
| `AWS_ACCESS_KEY_ID` / `R2_ACCESS_KEY_ID` | Optional | `""` | S3 / R2 access key |
| `AWS_SECRET_ACCESS_KEY` / `R2_SECRET_ACCESS_KEY` | Optional | `""` | S3 / R2 secret key |
| `GEMINI_API_KEY` | Existing | Provided | Google Gemini LLM API key |
| `GNANI_API_KEY` | Existing | Provided | Gnani Voice STT/TTS API key |

---

## 10. Files Created & Modified

### New Files:
- `.github/workflows/security_ci.yml` (CI security scan)
- `scripts/check_secrets.py` (Secret audit scanner)
- `scripts/migrate_v3_documents.py` (Neon database migration)
- `storage/__init__.py`
- `storage/base.py` (Storage provider interface)
- `storage/vercel_blob.py` (Vercel Blob REST adapter)
- `storage/s3_storage.py` (S3 / Cloudflare R2 adapter)
- `storage/db_blob.py` (Neon PostgreSQL durable storage adapter)
- `storage/factory.py` (Unified storage factory)
- `extractors/__init__.py`
- `extractors/base.py` (Data models & extractor interface)
- `extractors/pdf_extractor.py` (Text-based PDF structural extractor)
- `extractors/office_extractor.py` (DOCX & PPTX extractor)
- `extractors/ocr_extractor.py` (Phase 2 OCR interface stub)
- `extractors/multimodal_extractor.py` (Phase 2 Multimodal interface stub)
- `extractors/factory.py` (Extractor factory)
- `document_service.py` (Document management & async processing service)
- `document_router.py` (FastAPI router for document APIs)
- `tests/test_phase1_document_infrastructure.py` (11 acceptance tests)

### Modified Files:
- `server.py` (Mounted `document_router`)
- `static/index.html` (Added Universal Document UI card, fixed `loadActiveAnimatedProject`)

---

## 11. Known Limitations (To Address in Phase 2)

1. **Scanned PDFs / Handwritten Notes:** Currently, text-based PDFs extract directly. Scanned images inside PDFs will be processed once Google Cloud Vision / Tesseract OCR is wired into `extractors/ocr_extractor.py` during Phase 2.
2. **Interactive Code Sandbox:** Code blocks are extracted and tagged (Python, Java, C++, SQL), but code execution will be enabled in Phase 3 inside an isolated sandbox.
3. **Multimodal Diagram Understanding:** Embedded images and figures are tagged for Phase 2 multimodal Gemini processing.

---

## 12. Preview Deployment Instructions

To test on a Vercel preview deployment before merging to `main`:

```bash
# Push the feature branch to GitHub
git push origin feature/universal-doc-infra

# Deploy to Vercel Preview
vercel --filter=pod-siksha-2
```

Once preview testing is verified, the branch can be merged into `main` via PR without risk of regression.
