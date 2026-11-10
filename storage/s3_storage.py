"""
S3 & Cloudflare R2 Storage Provider for Pod-Siksha.
Supports AWS S3 and Cloudflare R2 using standard S3 API.
"""

import logging
import os
from typing import Optional
from storage.base import BaseStorageProvider

log = logging.getLogger("pod_siksha.storage.s3")

class S3StorageProvider(BaseStorageProvider):
    def __init__(self):
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL") or os.getenv("R2_ENDPOINT_URL")
        self.bucket = os.getenv("S3_BUCKET_NAME") or os.getenv("R2_BUCKET_NAME")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("R2_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("R2_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_DEFAULT_REGION", "auto")

        if not (self.bucket and self.access_key and self.secret_key):
            raise ValueError("S3 credentials and bucket name are required for S3StorageProvider")

        try:
            import boto3
            self.client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        except ImportError:
            raise RuntimeError("boto3 is required for S3StorageProvider")

    def get_provider_name(self) -> str:
        return "s3_r2"

    def upload(self, key: str, data: bytes, content_type: str, user_id: str, filename: str) -> str:
        clean_key = f"{user_id}/{key.lstrip('/')}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=clean_key,
            Body=data,
            ContentType=content_type,
            Metadata={"user_id": user_id, "original_filename": filename}
        )
        if self.endpoint_url:
            return f"{self.endpoint_url.rstrip('/')}/{self.bucket}/{clean_key}"
        return f"https://{self.bucket}.s3.amazonaws.com/{clean_key}"

    def download(self, key: str) -> bytes:
        clean_key = key.split(f"/{self.bucket}/")[-1] if f"/{self.bucket}/" in key else key
        resp = self.client.get_object(Bucket=self.bucket, Key=clean_key)
        return resp["Body"].read()

    def delete(self, key: str) -> bool:
        clean_key = key.split(f"/{self.bucket}/")[-1] if f"/{self.bucket}/" in key else key
        self.client.delete_object(Bucket=self.bucket, Key=clean_key)
        return True
