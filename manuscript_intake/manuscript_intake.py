"""
Manuscript Intake Agent Definition

Handles DOCX/PDF ingestion and canonical manuscript generation.
"""

from agency_swarm import Agent


manuscript_intake = Agent(
    name="ManuscriptIntake",
    description="""Handles document parsing and canonical manuscript generation. Converts 
    DOCX and PDF files into structured JSON format for the publishing pipeline.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-4o-mini",
)
