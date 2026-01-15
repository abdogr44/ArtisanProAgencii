"""
Style Suggestion Tool

Analyzes manuscript content and generates style improvement suggestions.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, List
import json
import os
import uuid
from datetime import datetime, timezone


class StyleSuggestionTool(BaseTool):
    """
    Analyzes manuscript and generates style improvement suggestions.
    Returns structured suggestions categorized by type and severity.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    focus_areas: Optional[List[str]] = Field(
        default=None, 
        description="Specific areas to focus on: voice_tone, structure_flow, language_quality, consistency"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Analyze manuscript and generate style suggestions.
        Returns JSON with categorized suggestions.
        """
        # Load manuscript
        manuscript_path = os.path.join(
            self.storage_root, "private", "manuscripts", f"{self.project_id}.json"
        )
        
        if not os.path.exists(manuscript_path):
            return json.dumps({
                "success": False,
                "error": f"Manuscript not found: {self.project_id}"
            }, indent=2)
        
        try:
            with open(manuscript_path, "r", encoding="utf-8") as f:
                manuscript = json.load(f)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to load manuscript: {str(e)}"
            }, indent=2)
        
        # Analyze and generate suggestions
        suggestions = []
        categories = {
            "voice_tone": 0,
            "structure_flow": 0,
            "language_quality": 0,
            "consistency": 0
        }
        
        # Analyze each chapter
        for chapter in manuscript.get("chapters", []):
            chapter_suggestions = self._analyze_chapter(chapter)
            for sugg in chapter_suggestions:
                suggestions.append(sugg)
                categories[sugg["category"]] += 1
        
        # Create suggestions report
        report_id = f"style-{uuid.uuid4().hex[:6]}"
        report = {
            "report_id": report_id,
            "type": "style_suggestions",
            "manuscript_id": self.project_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_suggestions": len(suggestions),
            "by_category": categories,
            "suggestions": suggestions
        }
        
        # Save report
        reports_path = os.path.join(self.storage_root, "private", "reports")
        os.makedirs(reports_path, exist_ok=True)
        
        report_file = os.path.join(reports_path, f"{self.project_id}_style.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Update project state
        state_file = os.path.join(self.storage_root, "private", "states", f"{self.project_id}.json")
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            # Update stage
            old_stage = state.get("current_stage", "ingested")
            state["current_stage"] = "styled"
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Add stage transition
            if "stage_history" not in state:
                state["stage_history"] = []
            state["stage_history"].append({
                "from": old_stage,
                "to": "styled",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Add report artifact
            if "artifacts" not in state:
                state["artifacts"] = []
            state["artifacts"].append({
                "id": report_id,
                "type": "style_report",
                "path": report_file,
                "visibility": "private",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        
        return json.dumps({
            "success": True,
            "manuscript_id": self.project_id,
            "report_id": report_id,
            "total_suggestions": len(suggestions),
            "categories": categories,
            "report_path": report_file,
            "stage": "styled",
            "next_action": "Run proofreader for Pass 1",
            "note": "Style suggestions are advisory and do not block pipeline progression"
        }, indent=2)
    
    def _analyze_chapter(self, chapter: dict) -> List[dict]:
        """Analyze a chapter and return suggestions."""
        suggestions = []
        chapter_id = chapter.get("id", "unknown")
        chapter_title = chapter.get("title", "Untitled")
        
        # Get all text from sections
        all_text = []
        for section in chapter.get("sections", []):
            for block in section.get("content_blocks", []):
                if block.get("type") == "paragraph":
                    all_text.append(block.get("content", ""))
        
        full_text = " ".join(all_text)
        
        # Check for common style issues
        
        # 1. Repetitive sentence starts
        sentences = [s.strip() for s in full_text.split(".") if s.strip()]
        if len(sentences) >= 3:
            starts = [s.split()[0] if s.split() else "" for s in sentences]
            for i in range(len(starts) - 2):
                if starts[i] and starts[i] == starts[i+1] == starts[i+2]:
                    suggestions.append({
                        "id": f"sugg-{uuid.uuid4().hex[:6]}",
                        "category": "structure_flow",
                        "severity": "warning",
                        "location": f"{chapter_title} ({chapter_id})",
                        "message": f"Three consecutive sentences start with '{starts[i]}'",
                        "suggestion": "Vary sentence beginnings for better flow"
                    })
                    break
        
        # 2. Very long paragraphs
        for section in chapter.get("sections", []):
            for block in section.get("content_blocks", []):
                if block.get("type") == "paragraph":
                    content = block.get("content", "")
                    word_count = len(content.split())
                    if word_count > 150:
                        suggestions.append({
                            "id": f"sugg-{uuid.uuid4().hex[:6]}",
                            "category": "structure_flow",
                            "severity": "info",
                            "location": f"{chapter_title}, block {block.get('id')}",
                            "message": f"Long paragraph ({word_count} words)",
                            "suggestion": "Consider breaking into smaller paragraphs for readability"
                        })
        
        # 3. Check for passive voice patterns (simplified)
        passive_indicators = ["تم ", "يتم ", "قد تم "]
        for indicator in passive_indicators:
            if indicator in full_text:
                suggestions.append({
                    "id": f"sugg-{uuid.uuid4().hex[:6]}",
                    "category": "voice_tone",
                    "severity": "info",
                    "location": f"{chapter_title}",
                    "message": f"Passive voice detected ('{indicator.strip()}')",
                    "suggestion": "Consider using active voice for stronger impact"
                })
                break
        
        # 4. Consistency check - quotation marks
        if '"' in full_text and '«' in full_text:
            suggestions.append({
                "id": f"sugg-{uuid.uuid4().hex[:6]}",
                "category": "consistency",
                "severity": "warning",
                "location": f"{chapter_title}",
                "message": "Mixed quotation mark styles (\" and «)",
                "suggestion": "Use consistent quotation style throughout"
            })
        
        return suggestions


if __name__ == "__main__":
    print("StyleSuggestionTool ready")
