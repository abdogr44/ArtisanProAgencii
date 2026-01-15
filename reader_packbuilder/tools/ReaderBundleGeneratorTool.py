"""
Reader Bundle Generator Tool

Generates reader_bundle.sample.json for Firebase ReaderView.
Includes only whitelisted sample chapters.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional
import json
import os
import uuid
import hashlib
from datetime import datetime


class ReaderBundleGeneratorTool(BaseTool):
    """
    Generates reader_bundle.sample.json for Firebase ReaderView.
    Ensures only whitelisted chapters are included in the public bundle.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    purchase_url: Optional[str] = Field(
        default=None, description="URL for purchasing the full book"
    )
    app_store_url: Optional[str] = Field(
        default=None, description="iOS App Store URL"
    )
    play_store_url: Optional[str] = Field(
        default=None, description="Google Play Store URL"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Generate reader bundle with sample content only.
        Returns JSON with bundle path and checksum.
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
        
        # Check Pass 2 sign-off
        sign_offs = state.get("sign_offs", [])
        pass2_signed = any(s.get("gate") == "PASS2" for s in sign_offs)
        
        if not pass2_signed:
            return json.dumps({
                "success": False,
                "error": "Gate blocked: Pass 2 sign-off required before bundle generation",
                "current_stage": state.get("current_stage"),
                "sign_offs": [s.get("gate") for s in sign_offs]
            }, indent=2)
        
        # Load manuscript
        manuscript_path = os.path.join(
            self.storage_root, "private", "manuscripts", f"{self.project_id}.json"
        )
        
        with open(manuscript_path, "r", encoding="utf-8") as f:
            manuscript = json.load(f)
        
        # Get sample whitelist
        sample_whitelist = manuscript.get("sample_whitelist", {})
        sample_ids = sample_whitelist.get("chapter_ids", [])
        
        if not sample_ids:
            return json.dumps({
                "success": False,
                "error": "No sample chapters defined in whitelist"
            }, indent=2)
        
        # Build reader bundle
        metadata = manuscript.get("metadata", {})
        chapters = manuscript.get("chapters", [])
        
        bundle = {
            "bundle_version": "1.0.0",
            "bundle_type": "sample",
            "book_id": self.project_id,
            
            "metadata": {
                "title": metadata.get("title", "Untitled"),
                "title_ar": metadata.get("title_ar"),
                "subtitle": metadata.get("subtitle"),
                "subtitle_ar": metadata.get("subtitle_ar"),
                "author": metadata.get("author", "Unknown"),
                "author_ar": metadata.get("author_ar"),
                "cover_url": metadata.get("cover_image"),
                "description": metadata.get("description"),
                "description_ar": None,
                "language": metadata.get("language", "ar"),
                "genre": metadata.get("genre"),
                "publication_year": None,
                "total_chapters": len(chapters),
                "sample_chapters": len(sample_ids)
            },
            
            "toc": [],
            "sample_content": [],
            "allowed_sample_ids": sample_ids,
            
            "purchase_info": {
                "available": True,
                "price": None,
                "currency": "USD",
                "purchase_url": self.purchase_url,
                "app_store_url": self.app_store_url,
                "play_store_url": self.play_store_url
            },
            
            "integrity": {}
        }
        
        # Build TOC (all chapters, with sample flags)
        for i, ch in enumerate(chapters):
            bundle["toc"].append({
                "id": ch.get("id"),
                "title": ch.get("title", "Untitled"),
                "title_ar": None,
                "level": 1,
                "page": None,
                "is_sample": ch.get("id") in sample_ids,
                "order": i + 1
            })
        
        # Build sample content (ONLY whitelisted chapters)
        for ch in chapters:
            if ch.get("id") not in sample_ids:
                continue  # Skip non-sample chapters
            
            sample_chapter = {
                "id": ch.get("id"),
                "title": ch.get("title", "Untitled"),
                "title_ar": None,
                "order": ch.get("order", 0),
                "content_blocks": []
            }
            
            for section in ch.get("sections", []):
                for block in section.get("content_blocks", []):
                    sample_chapter["content_blocks"].append({
                        "id": block.get("id"),
                        "type": block.get("type", "paragraph"),
                        "content": block.get("content", ""),
                        "style": None
                    })
            
            bundle["sample_content"].append(sample_chapter)
        
        # Generate integrity info
        bundle_content = json.dumps(bundle, sort_keys=True, ensure_ascii=False)
        checksum = hashlib.sha256(bundle_content.encode()).hexdigest()
        
        bundle["integrity"] = {
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "checksum": f"sha256:{checksum}",
            "manuscript_id": self.project_id
        }
        
        # Save to PUBLIC storage
        public_path = os.path.join(self.storage_root, "public", "reader_bundles")
        os.makedirs(public_path, exist_ok=True)
        
        bundle_file = os.path.join(public_path, f"{self.project_id}_sample.json")
        with open(bundle_file, "w", encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False, indent=2)
        
        # Update state
        old_stage = state.get("current_stage", "pass2_signed")
        state["current_stage"] = "bundled"
        state["updated_at"] = datetime.utcnow().isoformat()
        
        if "stage_history" not in state:
            state["stage_history"] = []
        state["stage_history"].append({
            "from": old_stage,
            "to": "bundled",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        artifact = {
            "id": f"art-{uuid.uuid4().hex[:6]}",
            "type": "reader_bundle",
            "name": f"{self.project_id}_sample.json",
            "path": bundle_file,
            "visibility": "public",  # This is PUBLIC
            "checksum_sha256": checksum,
            "size_bytes": len(bundle_content.encode()),
            "mime_type": "application/json",
            "created_at": datetime.utcnow().isoformat()
        }
        
        if "artifacts" not in state:
            state["artifacts"] = []
        state["artifacts"].append(artifact)
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        
        return json.dumps({
            "success": True,
            "manuscript_id": self.project_id,
            "bundle_path": bundle_file,
            "visibility": "public",
            "sample_chapters_included": sample_ids,
            "total_chapters_in_book": len(chapters),
            "checksum": f"sha256:{checksum}",
            "stage": "bundled",
            "next_action": "Get final sign-off and run release_packager"
        }, indent=2)


if __name__ == "__main__":
    print("ReaderBundleGeneratorTool ready")
