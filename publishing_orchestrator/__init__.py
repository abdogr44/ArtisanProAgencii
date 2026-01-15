"""
Publishing Orchestrator Agent

Entry agent for the Athar publishing pipeline. Orchestrates all stages
from ingestion through release, enforcing gates and signatures.
"""

from .publishing_orchestrator import publishing_orchestrator

__all__ = ["publishing_orchestrator"]
