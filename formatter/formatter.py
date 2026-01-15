"""
Formatter Agent Definition

Generates PDF and EPUB exports for books and samples.
"""

from agency_swarm import Agent


formatter = Agent(
    name="Formatter",
    description="""Generates final PDF and EPUB exports, including sample versions. 
    Handles Arabic typography and ensures consistent formatting across outputs.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-4o-mini",
)
