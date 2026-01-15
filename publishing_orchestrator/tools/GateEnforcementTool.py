"""
Gate Enforcement Tool

Validates gate requirements and records sign-offs for pipeline progression.
Ensures Pass 1 is signed before formatting and Pass 2 before release.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Literal
import json
import os
from datetime import datetime, timezone


class GateEnforcementTool(BaseTool):
    """
    Validates gate requirements and records sign-offs.
    Critical for enforcing pipeline progression rules.
    """
    project_id: str = Field(
        ..., description="The project/manuscript identifier"
    )
    action: Literal["check", "sign"] = Field(
        ..., description="Action: 'check' to validate, 'sign' to record sign-off"
    )
    gate: Literal["PASS1", "PASS2", "FINAL"] = Field(
        ..., description="Gate to check or sign"
    )
    signed_by: Optional[str] = Field(
        default=None, description="User signing off (required for 'sign' action)"
    )
    notes: Optional[str] = Field(
        default=None, description="Optional notes for sign-off"
    )
    override_issues: bool = Field(
        default=False, description="Override blocking issues (use with caution)"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def _calculate_canonical_hash(self, project_id: str) -> Optional[str]:
        """Calculate SHA-256 hash of the canonical manuscript."""
        # Locate canonical manuscript
        # Assuming typical storage structure: storage/private/manuscripts/{project_id}.json
        canonical_path = os.path.join(self.storage_root, "private", "manuscripts", f"{project_id}.json")
        
        if not os.path.exists(canonical_path):
             return None
             
        try:
            import hashlib
            sha256_hash = hashlib.sha256()
            with open(canonical_path, "rb") as f:
                # Read and update hash string value in blocks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None

    def run(self) -> str:
        """
        Check gate requirements or record sign-off.
        Returns JSON with validation result or sign-off confirmation.
        """
        private_root = os.path.join(self.storage_root, "private")
        state_file = os.path.join(private_root, "states", f"{self.project_id}.json")
        
        # Load project state
        if not os.path.exists(state_file):
            return json.dumps({
                "success": False,
                "error": f"Project {self.project_id} not found"
            }, indent=2)
        
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read project state: {str(e)}"
            }, indent=2)
            
        # START HASH BINDING LOGIC
        current_hash = self._calculate_canonical_hash(self.project_id)
        if not current_hash:
             return json.dumps({
                "success": False,
                "error": f"Canonical manuscript not found for project {self.project_id}"
            }, indent=2)
        # END HASH BINDING LOGIC
        
        # Define gate requirements
        gate_requirements = {
            "PASS1": {
                "required_stages": ["proofed_1", "pass1_signed", "formatted", "proofed_2", "pass2_signed", "bundled", "released"],
                "blocks": "formatting",
                "description": "Pass 1 proofreading sign-off"
            },
            "PASS2": {
                "required_stages": ["proofed_2", "pass2_signed", "bundled", "released"],
                "blocks": "release",
                "description": "Pass 2 proofreading sign-off"
            },
            "FINAL": {
                "required_stages": ["bundled", "released"],
                "blocks": "deployment",
                "description": "Final release authorization"
            }
        }
        
        req = gate_requirements[self.gate]
        current_stage = state.get("current_stage", "draft")
        
        # Check for blocking issues
        issues = state.get("issues", [])
        critical = [i for i in issues if i.get("severity") == "critical" and not i.get("resolved")]
        errors = [i for i in issues if i.get("severity") == "error" and not i.get("resolved")]
        has_blocking = len(critical) > 0 or len(errors) > 0
        
        # Check if already signed AND valid
        sign_offs = state.get("sign_offs", [])
        valid_signature = False
        invalidation_reason = None
        
        existing_sign_off = next((s for s in sign_offs if s.get("gate") == self.gate), None)
        
        if existing_sign_off:
            stored_hash = existing_sign_off.get("input_hash")
            if stored_hash == current_hash:
                valid_signature = True
            else:
                valid_signature = False
                invalidation_reason = "Canonical manuscript has changed since sign-off (hash mismatch)"
        
        already_signed = valid_signature
        
        if self.action == "check":
            # Validation only
            can_sign = current_stage in req["required_stages"]
            
            result = {
                "success": True,
                "gate": self.gate,
                "description": req["description"],
                "current_stage": current_stage,
                "can_sign": can_sign and (not has_blocking or self.override_issues),
                "is_signed": already_signed,
                "input_hash": current_hash,
                "blocking_issues": {
                    "critical": len(critical),
                    "errors": len(errors),
                    "critical_details": [i.get("message") for i in critical[:3]],  # First 3
                    "error_details": [i.get("message") for i in errors[:3]]
                } if has_blocking else None,
                "requirements": {
                    "stage_met": can_sign,
                    "no_blocking_issues": not has_blocking,
                    "hash_valid": True if not existing_sign_off or (existing_sign_off and valid_signature) else False
                },
            }
            
            if invalidation_reason:
                result["invalidation_warning"] = invalidation_reason
            
            if not can_sign:
                result["reason"] = f"Current stage '{current_stage}' does not meet requirement for {self.gate}"
            elif has_blocking and not self.override_issues:
                result["reason"] = f"Blocking issues exist: {len(critical)} critical, {len(errors)} errors"
            
            return json.dumps(result, indent=2)
        
        elif self.action == "sign":
            # Record sign-off
            if not self.signed_by:
                return json.dumps({
                    "success": False,
                    "error": "signed_by is required for sign action"
                }, indent=2)
            
            if already_signed:
                return json.dumps({
                    "success": False,
                    "error": f"Gate {self.gate} is already signed and valid"
                }, indent=2)
            
            can_sign = current_stage in req["required_stages"]
            if not can_sign:
                return json.dumps({
                    "success": False,
                    "error": f"Cannot sign {self.gate}: current stage '{current_stage}' does not meet requirements"
                }, indent=2)
            
            if has_blocking and not self.override_issues:
                return json.dumps({
                    "success": False,
                    "error": f"Cannot sign {self.gate}: {len(critical)} critical and {len(errors)} error issues remain unresolved",
                    "blocking_issues": {
                        "critical": [i.get("message") for i in critical],
                        "errors": [i.get("message") for i in errors]
                    }
                }, indent=2)
            
            # Remove any existing invalid sign-off for this gate
            state["sign_offs"] = [s for s in state.get("sign_offs", []) if s.get("gate") != self.gate]
            
            # Record sign-off
            sign_off_record = {
                "gate": self.gate,
                "signed_by": self.signed_by,
                "signed_at": datetime.now(timezone.utc).isoformat(),
                "notes": self.notes,
                "input_hash": current_hash,
                "override_issues": self.override_issues,
                "overridden_issues": [i.get("id") for i in critical + errors] if self.override_issues else []
            }
            
            state["sign_offs"].append(sign_off_record)
            
            # Update stage based on gate
            new_stage = None
            if self.gate == "PASS1":
                new_stage = "pass1_signed"
            elif self.gate == "PASS2":
                new_stage = "pass2_signed"
            
            if new_stage:
                if "stage_history" not in state:
                    state["stage_history"] = []
                state["stage_history"].append({
                    "from": current_stage,
                    "to": new_stage,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": f"Gate {self.gate} signed by {self.signed_by}"
                })
                state["current_stage"] = new_stage
            
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Save state
            try:
                os.makedirs(os.path.dirname(state_file), exist_ok=True)
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to save state: {str(e)}"
                }, indent=2)
            
            return json.dumps({
                "success": True,
                "message": f"Gate {self.gate} signed successfully",
                "signed_by": self.signed_by,
                "input_hash": current_hash,
                "new_stage": new_stage or current_stage,
                "override_used": self.override_issues,
                "next_action": self._get_next_action(self.gate)
            }, indent=2)
    
    def _get_next_action(self, gate: str) -> str:
        if gate == "PASS1":
            return "Proceed to formatter to generate PDF/EPUB exports"
        elif gate == "PASS2":
            return "Proceed to reader_packbuilder to generate sample bundle"
        elif gate == "FINAL":
            return "Proceed to release_packager for final deployment"
        return "Unknown"


if __name__ == "__main__":
    # Test check
    tool = GateEnforcementTool(
        project_id="test-project",
        action="check",
        gate="PASS1"
    )
    print(tool.run())
