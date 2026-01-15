"""
Book Formatter Tool

Generates PDF and EPUB exports from canonical manuscripts.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Literal, List
import json
import os
import uuid
import hashlib
from datetime import datetime


class BookFormatterTool(BaseTool):
    """
    Generates PDF and EPUB exports from canonical manuscripts.
    Produces full book and sample versions.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    formats: List[Literal["pdf", "epub"]] = Field(
        default=["pdf", "epub"], description="Output formats to generate"
    )
    generate_samples: bool = Field(
        default=True, description="Whether to generate sample versions"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Generate PDF and EPUB exports.
        Returns JSON with artifact paths and checksums.
        """
        # Load state and check gate
        state_file = os.path.join(self.storage_root, "private", "states", f"{self.project_id}.json")
        
        if not os.path.exists(state_file):
            return json.dumps({
                "success": False,
                "error": f"Project not found: {self.project_id}"
            }, indent=2)
        
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # Check Pass 1 sign-off
        sign_offs = state.get("sign_offs", [])
        pass1_signed = any(s.get("gate") == "PASS1" for s in sign_offs)
        
        if not pass1_signed:
            return json.dumps({
                "success": False,
                "error": "Gate blocked: Pass 1 sign-off required before formatting",
                "current_stage": state.get("current_stage"),
                "sign_offs": [s.get("gate") for s in sign_offs]
            }, indent=2)
        
        # Load manuscript
        manuscript_path = os.path.join(
            self.storage_root, "private", "manuscripts", f"{self.project_id}.json"
        )
        
        with open(manuscript_path, "r", encoding="utf-8") as f:
            manuscript = json.load(f)
        
        # Create exports directory
        exports_path = os.path.join(self.storage_root, "private", "exports", self.project_id)
        os.makedirs(exports_path, exist_ok=True)
        
        artifacts = []
        
        # Generate full exports
        title = manuscript.get("metadata", {}).get("title", "Untitled")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip().replace(" ", "_")
        
        for fmt in self.formats:
            # Generate full version
            full_path = os.path.join(exports_path, f"{safe_title}_full.{fmt}")
            full_artifact = self._generate_export(manuscript, full_path, fmt, is_sample=False)
            artifacts.append(full_artifact)
            
            # Generate sample version
            if self.generate_samples:
                sample_path = os.path.join(exports_path, f"{safe_title}_sample.{fmt}")
                sample_artifact = self._generate_export(manuscript, sample_path, fmt, is_sample=True)
                artifacts.append(sample_artifact)
        
        # Update state
        old_stage = state.get("current_stage", "pass1_signed")
        state["current_stage"] = "formatted"
        state["updated_at"] = datetime.utcnow().isoformat()
        
        if "stage_history" not in state:
            state["stage_history"] = []
        state["stage_history"].append({
            "from": old_stage,
            "to": "formatted",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if "artifacts" not in state:
            state["artifacts"] = []
        state["artifacts"].extend(artifacts)
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        
        return json.dumps({
            "success": True,
            "manuscript_id": self.project_id,
            "artifacts_generated": len(artifacts),
            "artifacts": artifacts,
            "stage": "formatted",
            "next_action": "Run proofreader for Pass 2"
        }, indent=2)
    
    def _generate_export(self, manuscript: dict, output_path: str, format: str, is_sample: bool) -> dict:
        """Generate a single export file."""
        artifact_id = f"art-{uuid.uuid4().hex[:6]}"
        
        # Extract content
        chapters = manuscript.get("chapters", [])
        
        if is_sample:
            # Filter to sample chapters only
            sample_ids = manuscript.get("sample_whitelist", {}).get("chapter_ids", [])
            chapters = [ch for ch in chapters if ch.get("id") in sample_ids]
        
        # Build content
        content_lines = []
        metadata = manuscript.get("metadata", {})
        
        # Title page
        content_lines.append(f"# {metadata.get('title', 'Untitled')}")
        if metadata.get("title_ar"):
            content_lines.append(f"# {metadata.get('title_ar')}")
        content_lines.append(f"\nBy {metadata.get('author', 'Unknown')}")
        if metadata.get("author_ar"):
            content_lines.append(f"{metadata.get('author_ar')}")
        content_lines.append("\n---\n")
        
        # Table of contents
        content_lines.append("## Table of Contents\n")
        for ch in chapters:
            content_lines.append(f"- {ch.get('title', 'Untitled')}")
        content_lines.append("\n---\n")
        
        # Chapters
        for ch in chapters:
            content_lines.append(f"\n## {ch.get('title', 'Untitled')}\n")
            
            for section in ch.get("sections", []):
                if section.get("title"):
                    content_lines.append(f"\n### {section.get('title')}\n")
                
                for block in section.get("content_blocks", []):
                    if block.get("type") == "paragraph":
                        content_lines.append(block.get("content", ""))
                        content_lines.append("")  # Empty line between paragraphs
        
        # Write content (simplified - in production would use proper PDF/EPUB libs)
        full_content = "\n".join(content_lines)
        
        # For now, write as text file (would be PDF/EPUB in production)
        # In production: use reportlab for PDF, ebooklib for EPUB
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        # Calculate checksum
        with open(output_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        # Get file size
        size_bytes = os.path.getsize(output_path)
        
        artifact_type = f"{'epub' if format == 'epub' else 'pdf'}_{'sample' if is_sample else 'full'}"
        
        return {
            "id": artifact_id,
            "type": artifact_type,
            "name": os.path.basename(output_path),
            "path": output_path,
            "visibility": "private",  # All exports are private
            "checksum_sha256": checksum,
            "size_bytes": size_bytes,
            "mime_type": f"application/{format}",
            "is_sample": is_sample,
            "created_at": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    print("BookFormatterTool ready")
