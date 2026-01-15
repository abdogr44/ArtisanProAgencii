"""
Style Editor Agent Definition

Analyzes manuscripts and provides stylistic improvement suggestions.
"""

from agency_swarm import Agent


style_editor = Agent(
    name="StyleEditor",
    description="""Analyzes manuscripts and provides stylistic improvement suggestions. 
    Evaluates writing style, tone, consistency, and Arabic language quality.""",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-5.2",
    reasoning_effort="low",
)
