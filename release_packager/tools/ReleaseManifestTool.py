"""
Release Manifest Tool

Creates release manifest with artifact checksums and deployment configuration.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Literal
import json
import os
import uuid
import hashlib
from datetime import datetime


class ReleaseManifestTool(BaseTool):
    """
    Creates release manifest with all artifacts, checksums, and deployment config.
    Finalizes the publishing pipeline.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    version: str = Field(
        ..., description="Release version (semver, e.g., 1.0.0)"
    )
    release_type: Literal["major", "minor", "patch"] = Field(
        default="major", description="Type of release"
    )
    release_notes: Optional[str] = Field(
        default=None, description="Optional release notes"
    )
    firebase_site_id: Optional[str] = Field(
        default="athar-reader", description="Firebase Hosting site ID"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Create release manifest and configure deployment.
        Returns JSON with manifest and deployment instructions.
        """
        # Load state
        state_file = os.path.join(self.storage_root, "private", "states", f"{self.project_id}.json")
        
        if not os.path.exists(state_file):
            return json.dumps({
                "success": False,
                "error": f"Project not found: {self.project_id}"
            }, indent=2)
        
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # Verify all gates
        sign_offs = state.get("sign_offs", [])
        gates = {s.get("gate") for s in sign_offs}
        
        required_gates = {"PASS1", "PASS2", "FINAL"}
        missing = required_gates - gates
        
        if missing:
            return json.dumps({
                "success": False,
                "error": f"Missing required sign-offs: {', '.join(missing)}",
                "current_sign_offs": list(gates)
            }, indent=2)
        
        # Load manuscript for metadata
        manuscript_path = os.path.join(
            self.storage_root, "private", "manuscripts", f"{self.project_id}.json"
        )
        
        with open(manuscript_path, "r", encoding="utf-8") as f:
            manuscript = json.load(f)
        
        metadata = manuscript.get("metadata", {})
        
        # Generate release ID
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        release_id = f"rel-{timestamp}-{uuid.uuid4().hex[:4]}"
        
        # Build manifest
        manifest = {
            "manifest_version": "1.0.0",
            "release_id": release_id,
            "project_id": self.project_id,
            "manuscript_id": manuscript.get("manuscript_id", self.project_id),
            "created_at": datetime.utcnow().isoformat(),
            
            "metadata": {
                "title": metadata.get("title", "Untitled"),
                "title_ar": metadata.get("title_ar"),
                "author": metadata.get("author", "Unknown"),
                "author_ar": metadata.get("author_ar"),
                "version": self.version,
                "release_type": self.release_type,
                "release_notes": self.release_notes
            },
            
            "artifacts": [],
            "sign_offs": sign_offs,
            
            "firebase": {
                "enabled": True,
                "site_id": self.firebase_site_id,
                "target_path": f"/books/{self.project_id}/",
                "artifacts_to_deploy": []
            }
        }
        
        # Process artifacts
        public_artifacts = []
        for artifact in state.get("artifacts", []):
            # Verify file exists
            path = artifact.get("path", "")
            if not os.path.exists(path):
                continue
            
            # Calculate checksum if not present
            checksum = artifact.get("checksum_sha256")
            if not checksum:
                with open(path, "rb") as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()
            
            # Get file size
            size_bytes = artifact.get("size_bytes")
            if not size_bytes:
                size_bytes = os.path.getsize(path)
            
            artifact_entry = {
                "id": artifact.get("id"),
                "name": os.path.basename(path),
                "type": artifact.get("type"),
                "path": path,
                "visibility": artifact.get("visibility", "private"),
                "checksum_sha256": checksum,
                "size_bytes": size_bytes,
                "mime_type": artifact.get("mime_type", "application/octet-stream"),
                "created_at": artifact.get("created_at")
            }
            
            manifest["artifacts"].append(artifact_entry)
            
            # Track public artifacts for deployment
            if artifact.get("visibility") == "public":
                public_artifacts.append(artifact.get("id"))
        
        manifest["firebase"]["artifacts_to_deploy"] = public_artifacts
        
        # Calculate manifest checksum
        manifest_content = json.dumps(manifest, sort_keys=True)
        manifest["manifest_checksum"] = hashlib.sha256(manifest_content.encode()).hexdigest()
        
        # Save manifest
        manifests_path = os.path.join(self.storage_root, "private", "manifests")
        os.makedirs(manifests_path, exist_ok=True)
        
        manifest_file = os.path.join(manifests_path, f"{release_id}.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        
        # Update state
        old_stage = state.get("current_stage", "bundled")
        state["current_stage"] = "released"
        state["updated_at"] = datetime.utcnow().isoformat()
        state["latest_release_id"] = release_id
        
        if "stage_history" not in state:
            state["stage_history"] = []
        state["stage_history"].append({
            "from": old_stage,
            "to": "released",
            "timestamp": datetime.utcnow().isoformat(),
            "release_id": release_id
        })
        
        state["artifacts"].append({
            "id": f"art-{uuid.uuid4().hex[:6]}",
            "type": "release_manifest",
            "path": manifest_file,
            "visibility": "private",
            "created_at": datetime.utcnow().isoformat()
        })
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        
        # Build deployment instructions
        deployment = {
            "command": f"firebase deploy --only hosting:{self.firebase_site_id}",
            "public_artifacts": len(public_artifacts),
            "private_artifacts": len(manifest["artifacts"]) - len(public_artifacts)
        }
        
        return json.dumps({
            "success": True,
            "release_id": release_id,
            "version": self.version,
            "manifest_path": manifest_file,
            "total_artifacts": len(manifest["artifacts"]),
            "public_artifacts": public_artifacts,
            "stage": "released",
            "deployment": deployment,
            "message": f"Release {self.version} created successfully. Run 'firebase deploy' to publish public artifacts."
        }, indent=2)


if __name__ == "__main__":
    print("ReleaseManifestTool ready")
