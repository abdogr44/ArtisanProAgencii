"""
Pipeline Status Tool

Retrieves the current status of a publishing project including stage,
issues, sign-offs, and artifacts.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional
import json
import os
from datetime import datetime


class PipelineStatusTool(BaseTool):
    """
    Retrieves the current pipeline status for a publishing project.
    Returns stage, issues, sign-offs, and recent artifacts.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Get current pipeline status for the project.
        Returns JSON with stage, issues, sign-offs, and artifacts.
        """
        # Build paths
        private_root = os.path.join(self.storage_root, "private")
        state_file = os.path.join(private_root, "states", f"{self.project_id}.json")
        
        # Check if project exists
        if not os.path.exists(state_file):
            # Return initial state for new project
            return json.dumps({
                "success": True,
                "project_id": self.project_id,
                "exists": False,
                "message": "Project not found. Use manuscript_intake to create a new project.",
                "suggested_action": "ingest_manuscript"
            }, indent=2)
        
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read project state: {str(e)}"
            }, indent=2)
        
        # Build status response
        status = {
            "success": True,
            "project_id": self.project_id,
            "exists": True,
            "current_stage": state.get("current_stage", "draft"),
            "created_at": state.get("created_at"),
            "updated_at": state.get("updated_at"),
            
            # Issues summary
            "issues": {
                "total": len(state.get("issues", [])),
                "critical": sum(1 for i in state.get("issues", []) 
                               if i.get("severity") == "critical" and not i.get("resolved")),
                "errors": sum(1 for i in state.get("issues", []) 
                             if i.get("severity") == "error" and not i.get("resolved")),
                "warnings": sum(1 for i in state.get("issues", []) 
                               if i.get("severity") == "warning" and not i.get("resolved")),
            },
            
            # Sign-offs
            "sign_offs": {
                "PASS1": any(s.get("gate") == "PASS1" for s in state.get("sign_offs", [])),
                "PASS2": any(s.get("gate") == "PASS2" for s in state.get("sign_offs", [])),
                "FINAL": any(s.get("gate") == "FINAL" for s in state.get("sign_offs", [])),
            },
            
            # Recent artifacts
            "artifacts_count": len(state.get("artifacts", [])),
            "recent_artifacts": state.get("artifacts", [])[-5:],  # Last 5
            
            # Stage history
            "stage_history": state.get("stage_history", [])[-5:],  # Last 5 transitions
        }
        
        # Determine next action
        stage = status["current_stage"]
        if stage == "draft":
            status["next_action"] = "Run manuscript_intake to parse the source file"
        elif stage == "ingested":
            status["next_action"] = "Run style_editor for style suggestions"
        elif stage == "styled":
            status["next_action"] = "Run proofreader for Pass 1"
        elif stage == "proofed_1":
            if status["issues"]["critical"] == 0 and status["issues"]["errors"] == 0:
                status["next_action"] = "Sign off Pass 1 to proceed to formatting"
            else:
                status["next_action"] = "Resolve blocking issues before Pass 1 sign-off"
        elif stage == "pass1_signed":
            status["next_action"] = "Run formatter to generate PDF/EPUB"
        elif stage == "formatted":
            status["next_action"] = "Run proofreader for Pass 2"
        elif stage == "proofed_2":
            if status["issues"]["critical"] == 0 and status["issues"]["errors"] == 0:
                status["next_action"] = "Sign off Pass 2 to proceed to bundling"
            else:
                status["next_action"] = "Resolve blocking issues before Pass 2 sign-off"
        elif stage == "pass2_signed":
            status["next_action"] = "Run reader_packbuilder to generate sample bundle"
        elif stage == "bundled":
            status["next_action"] = "Get final sign-off and run release_packager"
        elif stage == "released":
            status["next_action"] = "Project is released. No further actions required."
        
        return json.dumps(status, indent=2)


if __name__ == "__main__":
    # Test
    tool = PipelineStatusTool(project_id="test-project")
    print(tool.run())
