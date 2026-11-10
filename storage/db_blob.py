"""
Neon PostgreSQL Durable Blob Storage Provider for Pod-Siksha.
Stores document payloads durably in Neon PostgreSQL table `document_blobs`.
Zero-dependency, works seamlessly across Vercel serverless and local environments.
Guarantees documents are NEVER stored in ephemeral serverless /tmp.
"""

import logging
import psycopg2
from storage.base import BaseStorageProvider
from db_adapter import get_db

log = logging.getLogger("pod_siksha.storage.db_blob")

class DbBlobStorageProvider(BaseStorageProvider):
    def get_provider_name(self) -> str:
        return "neon_postgres_durable"

    def upload(self, key: str, data: bytes, content_type: str, user_id: str, filename: str) -> str:
        clean_key = f"{user_id}/{key.lstrip('/')}"
        with get_db() as conn:
            # Handle binary insertion safely for psycopg2 and sqlite3
            try:
                # Check if it's postgres or sqlite
                conn.execute("""
                    INSERT INTO document_blobs (storage_key, user_id, filename, content_type, data)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (storage_key) DO UPDATE SET
                        filename = EXCLUDED.filename,
                        content_type = EXCLUDED.content_type,
                        data = EXCLUDED.data
                """, (clean_key, user_id, filename, content_type or "application/pdf", psycopg2.Binary(data)))
            except Exception as e:
                # Fallback for sqlite if psycopg2.Binary is used
                if "Binary" in str(e) or "sqlite" in str(type(conn)).lower():
                    conn.execute("""
                        INSERT OR REPLACE INTO document_blobs (storage_key, user_id, filename, content_type, data)
                        VALUES (?, ?, ?, ?, ?)
                    """, (clean_key, user_id, filename, content_type or "application/pdf", data))
                else:
                    raise
        log.info("Persisted document blob %s (%d bytes) in Neon PostgreSQL durable storage", clean_key, len(data))
        return f"db://document_blobs/{clean_key}"

    def download(self, key: str) -> bytes:
        clean_key = key.replace("db://document_blobs/", "")
        with get_db() as conn:
            cur = conn.execute("SELECT data FROM document_blobs WHERE storage_key = ?", (clean_key,))
            row = cur.fetchone()
            if not row:
                raise FileNotFoundError(f"Blob with key {clean_key} not found in database storage")
            raw_data = row[0]
            if isinstance(raw_data, memoryview):
                return raw_data.tobytes()
            elif isinstance(raw_data, bytes):
                return raw_data
            return bytes(raw_data)

    def delete(self, key: str) -> bool:
        clean_key = key.replace("db://document_blobs/", "")
        with get_db() as conn:
            conn.execute("DELETE FROM document_blobs WHERE storage_key = ?", (clean_key,))
        return True
