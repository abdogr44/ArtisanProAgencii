from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Dict
import os
import requests
import hashlib
import mimetypes
from datetime import datetime, timezone
import uuid
# Fix: Use direct import since package structure can be tricky in agency-swarm runtime
try:
    from ...schemas.athar_output_envelope import AtharOutputEnvelope
    from ...storage_backends import get_storage_backend
except ImportError:
    # Fallback for direct execution/testing
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from schemas.athar_output_envelope import AtharOutputEnvelope
    from storage_backends import get_storage_backend

class ProjectFileIngestTool(BaseTool):
    """
    Ingests a source file (DOCX/PDF) into the private storage backend.
    Calculates SHA256 hash and returns a stable storage URI.
    Must be called BEFORE delegating to ManuscriptIntake.
    """
    project_id: str = Field(
        ..., description="The unique project identifier (e.g. 'ms-123')"
    )
    file_url: str = Field(
        ..., description="The direct URL to download the file (signed URL or public)"
    )
    original_filename: str = Field(
        ..., description="Original filename of the source document"
    )

    def run(self) -> str:
        """
        Download file, save to storage/private/uploads/{project_id}/, return metadata.
        """
        backend = get_storage_backend()
        
        # 1. Download to temp
        try:
            response = requests.get(self.file_url, stream=True)
            response.raise_for_status()
        except Exception as e:
            return self._error_response(f"Download failed: {str(e)}")

        # 2. Compute Hash & Save
        sha256 = hashlib.sha256()
        file_size = 0
        temp_path = f"temp_{uuid.uuid4().hex}.tmp"
        
        try:
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        sha256.update(chunk)
                        file_size += len(chunk)
            
            file_hash = sha256.hexdigest()
            
            # 3. Upload to Backend
            # Structure: private/uploads/{project_id}/{filename}
            storage_path = f"private/uploads/{self.project_id}/{self.original_filename}"
            
            # Check if exists? (Idempotency - optional, we overwrite for now to be safe)
            storage_uri = backend.put_file(temp_path, storage_path)
            
        except Exception as e:
            return self._error_response(f"Processing failed: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # 4. Construct Output
        ext = os.path.splitext(self.original_filename)[1].lower()
        confidence = "high" if ext == ".docx" else "medium"
        
        output_data = {
            "project_id": self.project_id,
            "source": {
                "filename": self.original_filename,
                "sha256": file_hash,
                "size_bytes": file_size,
                "mime_type": mimetypes.guess_type(self.original_filename)[0],
                "storage_uri": storage_uri,
                "parsing_confidence_hint": confidence
            },
            "input_hash": file_hash
        }
        
        envelope = AtharOutputEnvelope(
            job_id=f"job-{uuid.uuid4().hex[:8]}",
            project_id=self.project_id,
            tool_name="ProjectFileIngestTool",
            stage="ingestion_prep",
            success=True,
            data=output_data,
            artifacts=[
                {
                    "id": f"src-{file_hash[:8]}",
                    "type": "other",
                    "path": storage_path, # internal path
                    "visibility": "private",
                    "checksum_sha256": file_hash
                }
            ]
        )
        
        return envelope.model_dump_json(indent=2)

    def _error_response(self, msg: str) -> str:
        return AtharOutputEnvelope(
             job_id=f"err-{uuid.uuid4().hex[:8]}",
             project_id=self.project_id,
             tool_name="ProjectFileIngestTool",
             stage="ingestion_prep",
             success=False,
             error=msg,
             data={}
        ).model_dump_json(indent=2)
