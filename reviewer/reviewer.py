from agency_swarm import Agent

import os

# Explicitly read instructions with UTF-8
with open(os.path.join(os.path.dirname(__file__), "instructions.md"), "r", encoding="utf-8") as f:
    instructions_content = f.read()

reviewer = Agent(
    name="Reviewer",
    description="Quality assurance specialist who reviews GraphicDesigner outputs before delivery to users",
    instructions=instructions_content,
    model="gpt-5.2",
    reasoning_effort="low",
    tools_folder="./tools",
)
