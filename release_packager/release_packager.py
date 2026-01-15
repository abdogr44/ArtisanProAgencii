"""
Release Packager Agent Definition

Creates release manifests and coordinates deployment.
"""

from agency_swarm import Agent


release_packager = Agent(
    name="ReleasePackager",
    description="""Creates final release manifests with artifact checksums and version numbers. 
    Coordinates Firebase Hosting deployment configuration for public artifacts.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-5.2",
    reasoning_effort="low",
)
