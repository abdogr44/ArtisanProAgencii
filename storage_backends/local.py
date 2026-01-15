import os
import shutil
from .base import StorageBackend

class LocalFSBackend(StorageBackend):
    """Local filesystem implementation of StorageBackend."""
    
    def __init__(self, root_dir: str = "./storage"):
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)
        
    def _resolve(self, storage_path: str) -> str:
        # Prevent directory traversal
        clean_path = storage_path.lstrip("/").replace("\\", "/")
        full_path = os.path.abspath(os.path.join(self.root_dir, clean_path))
        if not full_path.startswith(self.root_dir):
            raise ValueError(f"Invalid storage path: {storage_path}")
        return full_path

    def put_file(self, local_path: str, storage_path: str) -> str:
        dest_path = self._resolve(storage_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(local_path, dest_path)
        return self.get_uri(storage_path)

    def get_to_local(self, storage_path: str, local_dest: str) -> str:
        src_path = self._resolve(storage_path)
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"File not found in storage: {storage_path}")
        
        os.makedirs(os.path.dirname(local_dest), exist_ok=True)
        shutil.copy2(src_path, local_dest)
        return local_dest
        
    def exists(self, storage_path: str) -> bool:
        return os.path.exists(self._resolve(storage_path))
        
    def get_uri(self, storage_path: str) -> str:
        return f"file://{self._resolve(storage_path)}"
