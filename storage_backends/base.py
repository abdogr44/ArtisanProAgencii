from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
import os

class StorageBackend(ABC):
    """Abstract base class for storage backends (Local vs GCS)."""
    
    @abstractmethod
    def put_file(self, local_path: str, storage_path: str) -> str:
        """Upload a local file to storage. Returns the storage URI."""
        pass

    @abstractmethod
    def get_to_local(self, storage_path: str, local_dest: str) -> str:
        """Download a file from storage to local path. Returns local path."""
        pass
        
    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Check if file exists in storage."""
        pass
        
    @abstractmethod
    def get_uri(self, storage_path: str) -> str:
        """Get the URI for a storage path."""
        pass
