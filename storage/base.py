"""
Abstract Base Storage Provider for Pod-Siksha.
Defines standard interface for persistent document storage across
Vercel Blob, S3/Cloudflare R2, and Neon PostgreSQL database blobs.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

class BaseStorageProvider(ABC):
    @abstractmethod
    def upload(self, key: str, data: bytes, content_type: str, user_id: str, filename: str) -> str:
        """
        Uploads binary file data to persistent storage.
        Returns the persistent public or signed access URL / resource key.
        """
        pass

    @abstractmethod
    def download(self, key: str) -> bytes:
        """
        Downloads binary file data by key.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Deletes the file from persistent storage.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Returns string identifier of the storage provider.
        """
        pass
