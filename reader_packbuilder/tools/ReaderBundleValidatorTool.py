"""
Reader Bundle Validator Tool

Validates generated reader bundles before public deployment.
Ensures only whitelisted content is included and no private data leaks.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field, ValidationError
import json
import os
from typing import List, Optional
from schemas import ReaderBundle, CanonicalManuscript

class ReaderBundleValidatorTool(BaseTool):
    """
    Validates a reader bundle against security and integrity rules.
    Must be run before any public deployment.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    bundle_path: str = Field(
        ..., description="Path to the reader_bundle.sample.json file"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Validate the reader bundle.
        Returns JSON with validation results.
        """
        # 1. Load Bundle
        if not os.path.exists(self.bundle_path):
            return json.dumps({
                "success": False,
                "error": f"Bundle file not found: {self.bundle_path}"
            }, indent=2)
            
        try:
            with open(self.bundle_path, "r", encoding="utf-8") as f:
                bundle_data = json.load(f)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to parse bundle JSON: {str(e)}"
            }, indent=2)

        # 2. Schema Validation
        try:
            bundle = ReaderBundle(**bundle_data)
        except ValidationError as e:
            return json.dumps({
                "success": False,
                "error": f"Schema validation failed: {str(e)}"
            }, indent=2)

        # 3. Load Canonical Manuscript (for whitelist verification)
        canonical_path = os.path.join(self.storage_root, "private", "manuscripts", f"{self.project_id}.json")
        if not os.path.exists(canonical_path):
            return json.dumps({
                "success": False,
                "error": f"Canonical manuscript not found: {canonical_path}"
            }, indent=2)
            
        try:
            with open(canonical_path, "r", encoding="utf-8") as f:
                manuscript_data = json.load(f)
                manuscript = CanonicalManuscript(**manuscript_data)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to load canonical manuscript: {str(e)}"
            }, indent=2)

        errors = []
        warnings = []

        # 4. Whitelist Verification
        # Check if bundle items match manuscript whitelist
        allowed_ids = set(manuscript.sample_whitelist.chapter_ids)
        bundle_ids = set(bundle.allowed_sample_ids)
        
        # Are there IDs in the bundle that are NOT in the whitelist?
        unauthorized_ids = bundle_ids - allowed_ids
        if unauthorized_ids:
            errors.append(f"Bundle contains unauthorized chapters: {list(unauthorized_ids)}")

        # Verify actual content matches allowed IDs (no data leak of non-listed chapters)
        content_ids = set(ch.id for ch in bundle.sample_content)
        leaked_content_ids = content_ids - bundle_ids
        if leaked_content_ids:
            errors.append(f"Content included for non-listed chapters: {list(leaked_content_ids)}")
            
        # 5. Security Scan (Keywords)
        # Check for "PRIVATE", "CONFIDENTIAL" in content (simple heuristic)
        sensitive_keywords = ["CONFIDENTIAL", "INTERNAL USE ONLY", "DRAFT DO NOT PUBLISH"]
        
        for chapter in bundle.sample_content:
            for block in chapter.content_blocks:
                text = block.content.upper()
                for kw in sensitive_keywords:
                    if kw in text:
                        warnings.append(f"Potential sensitive keyword '{kw}' found in chapter {chapter.id}")

        if errors:
            return json.dumps({
                "success": False,
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }, indent=2)
            
        return json.dumps({
            "success": True,
            "valid": True,
            "message": "Bundle validation passed",
            "checks": {
                "schema": "passed",
                "whitelist": "passed",
                "integrity": "passed",
                "security_scan": "passed" if not warnings else "warnings_found"
            },
            "warnings": warnings
        }, indent=2)

if __name__ == "__main__":
    # Test stub
    pass
