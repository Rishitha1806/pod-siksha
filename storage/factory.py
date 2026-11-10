"""
Storage Provider Factory for Pod-Siksha.
Selects the active persistent storage provider based on environment configuration.
"""

import os
import logging
from storage.base import BaseStorageProvider
from storage.vercel_blob import VercelBlobStorageProvider
from storage.s3_storage import S3StorageProvider
from storage.db_blob import DbBlobStorageProvider

log = logging.getLogger("pod_siksha.storage.factory")

_cached_provider: BaseStorageProvider = None

def get_storage_provider() -> BaseStorageProvider:
    global _cached_provider
    if _cached_provider is not None:
        return _cached_provider

    # 1. Prefer Vercel Blob if token is configured
    vercel_blob_token = os.getenv("BLOB_READ_WRITE_TOKEN", "").strip()
    if vercel_blob_token:
        try:
            _cached_provider = VercelBlobStorageProvider(vercel_blob_token)
            log.info("Using Vercel Blob persistent storage provider.")
            return _cached_provider
        except Exception as e:
            log.warning("Vercel Blob initialization failed: %s. Checking alternatives...", e)

    # 2. Check S3 / Cloudflare R2 if configured
    if (os.getenv("S3_BUCKET_NAME") or os.getenv("R2_BUCKET_NAME")) and (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("R2_ACCESS_KEY_ID")):
        try:
            _cached_provider = S3StorageProvider()
            log.info("Using S3 / Cloudflare R2 persistent storage provider.")
            return _cached_provider
        except Exception as e:
            log.warning("S3 / R2 initialization failed: %s. Falling back to Neon DB blob storage...", e)

    # 3. Fallback to Neon PostgreSQL durable table storage
    _cached_provider = DbBlobStorageProvider()
    log.info("Using Neon PostgreSQL durable blob storage provider (guarantees persistence across serverless invocations).")
    return _cached_provider
