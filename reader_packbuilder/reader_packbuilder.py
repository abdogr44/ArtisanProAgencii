"""
Reader Pack Builder Agent Definition

Builds Firebase ReaderView bundles with sample content only.
"""

from agency_swarm import Agent


reader_packbuilder = Agent(
    name="ReaderPackBuilder",
    description="""Builds reader_bundle.sample.json for Firebase ReaderView. Ensures only 
    whitelisted sample chapters are included in the public bundle.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-4o-mini",
)
