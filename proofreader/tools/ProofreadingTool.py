"""
Proofreading Tool

Performs grammar, spelling, and formatting checks on manuscripts.
Supports Pass 1 (post-edit) and Pass 2 (pre-release) reviews.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Literal, List
import json
import os
import uuid
import re
from datetime import datetime, timezone


class ProofreadingTool(BaseTool):
    """
    Performs proofreading on manuscript content.
    Generates issue reports with severity levels for gate decisions.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    pass_number: Literal[1, 2] = Field(
        ..., description="Proofreading pass: 1 (grammar/spelling) or 2 (formatting/polish)"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Perform proofreading and generate issue report.
        Returns JSON with issues categorized by severity.
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
        
        # Load current state
        state_file = os.path.join(self.storage_root, "private", "states", f"{self.project_id}.json")
        state = {}
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        
        # Perform proofreading
        issues = []
        
        if self.pass_number == 1:
            issues = self._pass1_proofread(manuscript)
            new_stage = "proofed_1"
            report_type = "proof_pass_1"
        else:
            issues = self._pass2_proofread(manuscript)
            new_stage = "proofed_2"
            report_type = "proof_pass_2"
        
        # Categorize by severity
        by_severity = {
            "critical": 0,
            "error": 0,
            "warning": 0,
            "info": 0
        }
        for issue in issues:
            severity = issue.get("severity", "info")
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Determine if can sign off
        blocking = [i for i in issues if i["severity"] in ["critical", "error"] and not i.get("resolved")]
        can_sign_off = len(blocking) == 0
        
        # Create report
        report_id = f"proof{self.pass_number}-{uuid.uuid4().hex[:6]}"
        report = {
            "report_id": report_id,
            "type": report_type,
            "pass": self.pass_number,
            "manuscript_id": self.project_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_issues": len(issues),
            "by_severity": by_severity,
            "can_sign_off": can_sign_off,
            "blocking_issues": blocking,
            "issues": issues
        }
        
        # Save report
        reports_path = os.path.join(self.storage_root, "private", "reports")
        os.makedirs(reports_path, exist_ok=True)
        
        report_file = os.path.join(reports_path, f"{self.project_id}_{report_type}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Update state
        old_stage = state.get("current_stage", "styled")
        state["current_stage"] = new_stage
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Add issues to state
        if "issues" not in state:
            state["issues"] = []
        
        # Add new issues (mark existing as from this pass)
        for issue in issues:
            issue["pass"] = self.pass_number
            state["issues"].append(issue)
        
        # Add stage transition
        if "stage_history" not in state:
            state["stage_history"] = []
        state["stage_history"].append({
            "from": old_stage,
            "to": new_stage,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Add artifact
        if "artifacts" not in state:
            state["artifacts"] = []
        state["artifacts"].append({
            "id": report_id,
            "type": report_type,
            "path": report_file,
            "visibility": "private",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        
        # Determine next action
        if self.pass_number == 1:
            if can_sign_off:
                next_action = "Sign off Pass 1 to proceed to formatting"
            else:
                next_action = f"Resolve {len(blocking)} blocking issues before Pass 1 sign-off"
        else:
            if can_sign_off:
                next_action = "Sign off Pass 2 to proceed to reader bundle generation"
            else:
                next_action = f"Resolve {len(blocking)} blocking issues before Pass 2 sign-off"
        
        return json.dumps({
            "success": True,
            "manuscript_id": self.project_id,
            "pass": self.pass_number,
            "report_id": report_id,
            "total_issues": len(issues),
            "by_severity": by_severity,
            "can_sign_off": can_sign_off,
            "blocking_count": len(blocking),
            "report_path": report_file,
            "stage": new_stage,
            "next_action": next_action
        }, indent=2)
    
    def _pass1_proofread(self, manuscript: dict) -> List[dict]:
        """Pass 1: Grammar, spelling, punctuation."""
        issues = []
        
        for chapter in manuscript.get("chapters", []):
            chapter_id = chapter.get("id", "unknown")
            chapter_title = chapter.get("title", "Untitled")
            
            for section in chapter.get("sections", []):
                for block in section.get("content_blocks", []):
                    if block.get("type") != "paragraph":
                        continue
                    
                    content = block.get("content", "")
                    block_id = block.get("id", "unknown")
                    
                    # Check for common issues
                    block_issues = self._check_grammar_spelling(content, chapter_title, block_id)
                    issues.extend(block_issues)
        
        return issues
    
    def _pass2_proofread(self, manuscript: dict) -> List[dict]:
        """Pass 2: Formatting, consistency, final polish."""
        issues = []
        
        # Check for formatting consistency
        chapters = manuscript.get("chapters", [])
        
        # Check chapter numbering consistency
        expected_num = 1
        for chapter in chapters:
            num = chapter.get("number")
            if num and num != expected_num:
                issues.append({
                    "id": f"issue-{uuid.uuid4().hex[:6]}",
                    "severity": "error",
                    "category": "formatting",
                    "message": f"Chapter numbering gap: expected {expected_num}, found {num}",
                    "location": chapter.get("title", "Unknown"),
                    "suggestion": "Ensure consecutive chapter numbering",
                    "resolved": False
                })
            expected_num = (num or expected_num) + 1
        
        # Check for empty sections
        for chapter in chapters:
            chapter_title = chapter.get("title", "Untitled")
            for section in chapter.get("sections", []):
                if not section.get("content_blocks"):
                    issues.append({
                        "id": f"issue-{uuid.uuid4().hex[:6]}",
                        "severity": "warning",
                        "category": "formatting",
                        "message": "Empty section with no content",
                        "location": f"{chapter_title}, section {section.get('id')}",
                        "suggestion": "Add content or remove empty section",
                        "resolved": False
                    })
        
        # Check TOC presence (sample whitelist)
        sample = manuscript.get("sample_whitelist", {})
        if not sample.get("chapter_ids"):
            issues.append({
                "id": f"issue-{uuid.uuid4().hex[:6]}",
                "severity": "error",
                "category": "formatting",
                "message": "No sample chapters defined",
                "location": "sample_whitelist",
                "suggestion": "Define sample chapters for reader bundle",
                "resolved": False
            })
        
        return issues
    
    def _check_grammar_spelling(self, content: str, location: str, block_id: str) -> List[dict]:
        """Check for grammar and spelling issues."""
        issues = []
        
        # Common Arabic spelling issues
        spelling_patterns = [
            (r"ة\s+ال", "warning", "Space between ta-marbuta and alif-lam"),
            (r"\bان\b(?!\s)", "info", "Possible missing hamza on 'إن' or 'أن'"),
            (r"\s{2,}", "error", "Multiple consecutive spaces"),
            (r"،\s*،", "error", "Double comma"),
            (r"\.\s*\.", "error", "Double period"),
        ]
        
        for pattern, severity, message in spelling_patterns:
            if re.search(pattern, content):
                issues.append({
                    "id": f"issue-{uuid.uuid4().hex[:6]}",
                    "severity": severity,
                    "category": "spelling",
                    "message": message,
                    "location": f"{location}, block {block_id}",
                    "suggestion": "Review and correct",
                    "resolved": False
                })
        
        # Check for unmatched brackets/quotes
        brackets = [("(", ")"), ("[", "]"), ("«", "»"), ("\"", "\"")]
        for open_b, close_b in brackets:
            if content.count(open_b) != content.count(close_b):
                issues.append({
                    "id": f"issue-{uuid.uuid4().hex[:6]}",
                    "severity": "error",
                    "category": "punctuation",
                    "message": f"Unmatched brackets: {open_b} {close_b}",
                    "location": f"{location}, block {block_id}",
                    "suggestion": "Add missing bracket",
                    "resolved": False
                })
        
        return issues


if __name__ == "__main__":
    print("ProofreadingTool ready")
