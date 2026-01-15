"""
Athar Publishing Pipeline Schemas

Pydantic models for standardized data structures across the publishing pipeline.
"""

from .canonical_manuscript import CanonicalManuscript, Chapter, Section, ContentBlock
from .athar_output_envelope import AtharOutputEnvelope, Artifact, Report, NextAction
from .reader_bundle import ReaderBundle, TOCEntry, SampleChapter
from .release_manifest import ReleaseManifest, ArtifactEntry
from .gate_state import GateState, PipelineStage, SignOff, Issue

__all__ = [
    # Manuscript
    "CanonicalManuscript",
    "Chapter", 
    "Section",
    "ContentBlock",
    # Output Envelope
    "AtharOutputEnvelope",
    "Artifact",
    "Report",
    "NextAction",
    # Reader Bundle
    "ReaderBundle",
    "TOCEntry",
    "SampleChapter",
    # Release Manifest
    "ReleaseManifest",
    "ArtifactEntry",
    # Gate State
    "GateState",
    "PipelineStage",
    "SignOff",
    "Issue",
]

