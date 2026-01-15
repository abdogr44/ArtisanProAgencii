"""
Proofreader Agent Definition

Performs two-pass proofreading with diff generation and issue tracking.
"""

from agency_swarm import Agent


proofreader = Agent(
    name="Proofreader",
    description="""Performs two-pass proofreading (Pass 1: grammar/spelling, Pass 2: formatting/polish). 
    Generates detailed issue reports with severity levels to support gate sign-offs.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-5.2",
    reasoning_effort="low",
)
