"""
Publishing Orchestrator Agent Definition

Entry agent for the Athar publishing pipeline. Manages workflow orchestration,
gate enforcement, and routing to specialist agents.
"""

from agency_swarm import Agent


publishing_orchestrator = Agent(
    name="PublishingOrchestrator",
    description="""Entry agent for the Athar publishing pipeline. Orchestrates all stages 
    from manuscript ingestion to final release, enforcing gates and signatures. Routes 
    tasks to specialist agents and ensures security policies are followed.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-4o",
)
