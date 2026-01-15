try:
    from google.cloud import storage
except ImportError:
    storage = None

import os
from .base import StorageBackend

class GCSBackend(StorageBackend):
    """Google Cloud Storage implementation of StorageBackend."""
    
    def __init__(self, bucket_name: str):
        if not storage:
            raise ImportError("google-cloud-storage is strongly recommended for production but not installed.")
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.bucket_name = bucket_name
        
    def put_file(self, local_path: str, storage_path: str) -> str:
        blob = self.bucket.blob(storage_path)
        blob.upload_from_filename(local_path)
        return self.get_uri(storage_path)

    def get_to_local(self, storage_path: str, local_dest: str) -> str:
        blob = self.bucket.blob(storage_path)
        if not blob.exists():
             raise FileNotFoundError(f"File not found in GCS: {storage_path}")
             
        os.makedirs(os.path.dirname(local_dest), exist_ok=True)
        blob.download_to_filename(local_dest)
        return local_dest
        
    def exists(self, storage_path: str) -> bool:
        blob = self.bucket.blob(storage_path)
        return blob.exists()
        
    def get_uri(self, storage_path: str) -> str:
        return f"gs://{self.bucket_name}/{storage_path}"
