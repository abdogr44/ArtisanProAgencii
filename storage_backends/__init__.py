import os
from .base import StorageBackend
from .local import LocalFSBackend

# Lazy import GCS to avoid hard crash without deps
def get_storage_backend() -> StorageBackend:
    """
    Factory to retrieve the configured storage backend.
    Defaults to LocalFSBackend unless ATHAR_STORAGE_BACKEND='gcs'.
    """
    backend_type = os.getenv("ATHAR_STORAGE_BACKEND", "local").lower()
    
    if backend_type == "gcs":
        from .gcs import GCSBackend
        bucket = os.getenv("ATHAR_GCS_BUCKET")
        if not bucket:
            raise ValueError("ATHAR_GCS_BUCKET env var required for GCS backend")
        return GCSBackend(bucket)
    
    # Default to local
    root = os.getenv("ATHAR_PROJECT_ROOT", "./storage")
    return LocalFSBackend(root)
