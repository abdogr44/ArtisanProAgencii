"""
Gate State Schema

Defines pipeline stages and gating mechanisms for the publishing pipeline.
Enforces that Pass 1 must be signed before formatting, and Pass 2 before release.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PipelineStage(str, Enum):
    """Stages in the publishing pipeline."""
    DRAFT = "draft"           # Initial manuscript uploaded
    INGESTED = "ingested"     # Canonical JSON created
    STYLED = "styled"         # Style suggestions complete
    PROOFED_1 = "proofed_1"   # Pass 1 proofreading complete
    PASS1_SIGNED = "pass1_signed"  # Pass 1 signed off
    FORMATTED = "formatted"   # PDF/EPUB generated
    PROOFED_2 = "proofed_2"   # Pass 2 proofreading complete
    PASS2_SIGNED = "pass2_signed"  # Pass 2 signed off
    BUNDLED = "bundled"       # Reader bundle generated
    RELEASED = "released"     # Release manifest created, deployed


class IssueSeverity(str, Enum):
    """Severity of issues blocking gate progression."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Issue(BaseModel):
    """An issue that may block gate progression."""
    id: str = Field(..., description="Unique issue identifier")
    severity: IssueSeverity = Field(...)
    category: str = Field(..., description="Issue category (grammar, style, formatting, etc.)")
    message: str = Field(...)
    location: Optional[str] = Field(default=None, description="Chapter/section reference")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by: Optional[str] = Field(default=None)


class SignOff(BaseModel):
    """A sign-off record for a gate."""
    gate: str = Field(..., description="Gate identifier (PASS1, PASS2, FINAL)")
    signed_by: str = Field(..., description="User who signed off")
    signed_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)
    input_hash: str = Field(..., description="Hash of the canonical input at the time of sign-off")
    override_issues: bool = Field(default=False, description="Whether blocking issues were overridden")
    overridden_issue_ids: List[str] = Field(default_factory=list)


class GateRequirements(BaseModel):
    """Requirements for passing a gate."""
    gate: str = Field(...)
    required_stage: PipelineStage = Field(..., description="Stage that must be reached")
    max_critical_issues: int = Field(default=0, description="Max critical issues allowed")
    max_error_issues: int = Field(default=0, description="Max error issues allowed")
    requires_sign_off: bool = Field(default=True)


class GateState(BaseModel):
    """
    Current gate state for a manuscript in the publishing pipeline.
    
    Tracks the current stage, sign-offs, and blocking issues.
    """
    project_id: str = Field(..., description="Project/manuscript identifier")
    current_stage: PipelineStage = Field(default=PipelineStage.DRAFT)
    
    # History
    stage_history: List[dict] = Field(default_factory=list, description="Stage transition history")
    
    # Issues
    issues: List[Issue] = Field(default_factory=list)
    
    # Sign-offs
    sign_offs: List[SignOff] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def unresolved_critical(self) -> List[Issue]:
        """Get unresolved critical issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL and not i.resolved]
    
    @property
    def unresolved_errors(self) -> List[Issue]:
        """Get unresolved error issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR and not i.resolved]
    
    def has_sign_off(self, gate: str) -> bool:
        """Check if a gate has been signed off."""
        return any(s.gate == gate for s in self.sign_offs)
    
    def can_proceed_to(self, target_stage: PipelineStage) -> tuple[bool, List[str]]:
        """
        Check if we can proceed to a target stage.
        Returns (can_proceed, list of blocking reasons).
        """
        blocking_reasons = []
        
        # Define stage order
        stage_order = list(PipelineStage)
        current_idx = stage_order.index(self.current_stage)
        target_idx = stage_order.index(target_stage)
        
        if target_idx <= current_idx:
            return True, []  # Can go backwards or stay
        
        # Check gates
        if target_stage == PipelineStage.FORMATTED:
            if not self.has_sign_off("PASS1"):
                blocking_reasons.append("Pass 1 sign-off required before formatting")
        
        if target_stage == PipelineStage.RELEASED:
            if not self.has_sign_off("PASS2"):
                blocking_reasons.append("Pass 2 sign-off required before release")
            if not self.has_sign_off("FINAL"):
                blocking_reasons.append("Final sign-off required before release")
        
        # Check blocking issues
        if self.unresolved_critical:
            blocking_reasons.append(f"{len(self.unresolved_critical)} unresolved critical issues")
        
        return len(blocking_reasons) == 0, blocking_reasons
    
    def record_stage_transition(self, from_stage: PipelineStage, to_stage: PipelineStage) -> None:
        """Record a stage transition in history."""
        self.stage_history.append({
            "from": from_stage.value,
            "to": to_stage.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.current_stage = to_stage
        self.updated_at = datetime.utcnow()


# Gate requirements configuration
GATE_REQUIREMENTS = [
    GateRequirements(
        gate="PASS1",
        required_stage=PipelineStage.PROOFED_1,
        max_critical_issues=0,
        max_error_issues=0
    ),
    GateRequirements(
        gate="PASS2", 
        required_stage=PipelineStage.PROOFED_2,
        max_critical_issues=0,
        max_error_issues=0
    ),
    GateRequirements(
        gate="FINAL",
        required_stage=PipelineStage.BUNDLED,
        max_critical_issues=0,
        max_error_issues=0
    ),
]
