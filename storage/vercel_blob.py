"""
Vercel Blob Storage Provider for Pod-Siksha.
Uses Vercel Blob REST API over HTTPS via httpx.
Requires BLOB_READ_WRITE_TOKEN environment variable.
"""

import logging
import os
from typing import Optional
import httpx
from storage.base import BaseStorageProvider

log = logging.getLogger("pod_siksha.storage.vercel_blob")

BLOB_API_BASE = "https://blob.vercel-storage.com"

class VercelBlobStorageProvider(BaseStorageProvider):
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("BLOB_READ_WRITE_TOKEN", "").strip()
        if not self.token:
            raise ValueError("BLOB_READ_WRITE_TOKEN is required for VercelBlobStorageProvider")

    def get_provider_name(self) -> str:
        return "vercel_blob"

    def upload(self, key: str, data: bytes, content_type: str, user_id: str, filename: str) -> str:
        clean_key = key.lstrip("/")
        url = f"{BLOB_API_BASE}/{clean_key}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-version": "7",
            "Content-Type": content_type or "application/octet-stream",
            "x-add-random-suffix": "0",
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.put(url, content=data, headers=headers)
            if resp.status_code not in (200, 201):
                log.error("Vercel Blob upload failed (%s): %s", resp.status_code, resp.text)
                raise RuntimeError(f"Vercel Blob upload failed: {resp.text}")
            result = resp.json()
            return result.get("url") or url

    def download(self, key: str) -> bytes:
        # If key is already a full URL, fetch it directly
        url = key if key.startswith("http://") or key.startswith("https://") else f"{BLOB_API_BASE}/{key.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.token}"}
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to download blob {key}: {resp.status_code}")
            return resp.content

    def delete(self, key: str) -> bool:
        delete_url = f"{BLOB_API_BASE}/delete"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-version": "7",
            "Content-Type": "application/json",
        }
        target_urls = [key] if (key.startswith("http://") or key.startswith("https://")) else [f"{BLOB_API_BASE}/{key.lstrip('/')}"]
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(delete_url, json={"urls": target_urls}, headers=headers)
            return resp.status_code in (200, 204)
