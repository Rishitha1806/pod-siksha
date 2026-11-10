#!/usr/bin/env python3
"""
Database Migration: Universal Document Infrastructure (Phase 1).
Adds additive tables for:
- document_blobs: persistent file byte storage
- documents: document metadata and ownership
- document_jobs: asynchronous idempotent job queue and progress tracking
- document_sections: structured extracted sections (text, code, math, tables)

Idempotent: Uses CREATE TABLE IF NOT EXISTS and CREATE INDEX IF NOT EXISTS.
Safe: Never deletes or modifies existing tables.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

from db_adapter import get_db

def run_migration():
    print("Connecting to database via db_adapter...")
    with get_db() as conn:
        print("Creating table: document_blobs...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_blobs (
                storage_key VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                content_type VARCHAR(64) NOT NULL,
                data BYTEA,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("Creating table: documents...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(64) NOT NULL,
                file_size_bytes BIGINT NOT NULL,
                storage_provider VARCHAR(32) NOT NULL DEFAULT 'neon_postgres_durable',
                storage_key TEXT NOT NULL,
                storage_url TEXT,
                sha256_hash VARCHAR(64),
                page_count INTEGER DEFAULT 0,
                subject_detected VARCHAR(100) DEFAULT 'General',
                status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP
            );
        """)

        print("Creating table: document_jobs...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_jobs (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                user_id VARCHAR(64) NOT NULL,
                job_type VARCHAR(64) NOT NULL DEFAULT 'extract_and_analyze',
                status VARCHAR(32) NOT NULL DEFAULT 'queued',
                progress_percent INTEGER DEFAULT 0,
                current_stage VARCHAR(64) DEFAULT 'queued',
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                result_summary TEXT,
                error_message TEXT,
                idempotency_key VARCHAR(128),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("Creating table: document_sections...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_sections (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                page_number INTEGER NOT NULL DEFAULT 1,
                section_index INTEGER NOT NULL DEFAULT 0,
                section_title VARCHAR(255),
                content_type VARCHAR(32) DEFAULT 'text',
                content TEXT NOT NULL,
                char_count INTEGER DEFAULT 0,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Indexes for fast lookup by user and document
        print("Creating performance indexes...")
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents (user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents (status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_jobs_doc ON document_jobs (document_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_jobs_user ON document_jobs (user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_sections_doc ON document_sections (document_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_sections_page ON document_sections (document_id, page_number);")
        except Exception as e:
            print(f"Notice during index creation: {e}")

    print("Migration successfully applied!")

if __name__ == "__main__":
    run_migration()
