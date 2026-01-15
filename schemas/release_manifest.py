"""
Release Manifest Schema

Defines the structure for release_manifest.json that tracks all artifacts
and their checksums for a book release.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class ArtifactVisibility(str, Enum):
    """Visibility classification for release artifacts."""
    PRIVATE = "private"
    PUBLIC = "public"


class ArtifactEntry(BaseModel):
    """An artifact included in the release."""
    id: str = Field(..., description="Unique artifact identifier")
    name: str = Field(..., description="Human-readable name")
    type: str = Field(..., description="Artifact type (pdf_full, epub_full, reader_bundle, etc.)")
    path: str = Field(..., description="Storage path relative to storage root")
    visibility: ArtifactVisibility = Field(...)
    checksum_sha256: str = Field(..., description="SHA-256 checksum")
    size_bytes: int = Field(...)
    mime_type: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FirebaseDeployment(BaseModel):
    """Firebase Hosting deployment configuration."""
    enabled: bool = Field(default=True)
    site_id: Optional[str] = Field(default=None)
    target_path: str = Field(default="/books", description="Path prefix on Hosting")
    artifacts_to_deploy: List[str] = Field(default_factory=list, description="Artifact IDs to deploy")


class ReleaseMetadata(BaseModel):
    """Metadata about the release."""
    title: str = Field(...)
    author: str = Field(...)
    version: str = Field(..., description="Release version (semver)")
    release_type: Literal["major", "minor", "patch"] = Field(default="minor")
    release_notes: Optional[str] = Field(default=None)
    released_by: Optional[str] = Field(default=None, description="User who authorized release")


class SignOffRecord(BaseModel):
    """Record of a sign-off."""
    gate: Literal["PASS1", "PASS2", "FINAL"] = Field(...)
    signed_by: str = Field(..., description="User who signed off")
    signed_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)


class ReleaseManifest(BaseModel):
    """
    Release manifest for a book publication.
    
    Tracks all artifacts, their checksums, and deployment configuration.
    This is the authoritative record of what was released.
    """
    manifest_version: str = Field(default="1.0.0", description="Manifest schema version")
    
    # Identifiers
    release_id: str = Field(..., description="Unique release identifier")
    project_id: str = Field(..., description="Project/manuscript identifier")
    manuscript_id: str = Field(..., description="Source manuscript identifier")
    
    # Release info
    metadata: ReleaseMetadata = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Artifacts
    artifacts: List[ArtifactEntry] = Field(default_factory=list)
    
    # Sign-offs
    sign_offs: List[SignOffRecord] = Field(default_factory=list)
    
    # Deployment
    firebase: Optional[FirebaseDeployment] = Field(default=None)
    
    # Verification
    manifest_checksum: Optional[str] = Field(default=None, description="Checksum of this manifest")
    
    @property
    def public_artifacts(self) -> List[ArtifactEntry]:
        """Get only public artifacts."""
        return [a for a in self.artifacts if a.visibility == ArtifactVisibility.PUBLIC]
    
    @property
    def private_artifacts(self) -> List[ArtifactEntry]:
        """Get only private artifacts."""
        return [a for a in self.artifacts if a.visibility == ArtifactVisibility.PRIVATE]
    
    def has_sign_off(self, gate: str) -> bool:
        """Check if a specific gate has been signed off."""
        return any(s.gate == gate for s in self.sign_offs)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "manifest_version": "1.0.0",
                "release_id": "rel-2026-01-15-001",
                "project_id": "athar-book-001",
                "manuscript_id": "ms-athar-book-001",
                "metadata": {
                    "title": "The Journey",
                    "author": "Aya El Badry",
                    "version": "1.0.0",
                    "release_type": "major"
                },
                "artifacts": [
                    {
                        "id": "art-pdf-full",
                        "name": "Full PDF",
                        "type": "pdf_full",
                        "path": "private/exports/the-journey-full.pdf",
                        "visibility": "private",
                        "checksum_sha256": "abc123...",
                        "size_bytes": 2048000,
                        "mime_type": "application/pdf"
                    },
                    {
                        "id": "art-reader-bundle",
                        "name": "Reader Bundle",
                        "type": "reader_bundle",
                        "path": "public/reader_bundles/the-journey-sample.json",
                        "visibility": "public",
                        "checksum_sha256": "def456...",
                        "size_bytes": 51200,
                        "mime_type": "application/json"
                    }
                ],
                "sign_offs": [
                    {"gate": "PASS1", "signed_by": "editor@athar.com"},
                    {"gate": "PASS2", "signed_by": "proofreader@athar.com"},
                    {"gate": "FINAL", "signed_by": "author@athar.com"}
                ]
            }
        }
    )
