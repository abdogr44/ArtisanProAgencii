from agency_swarm import Agent

import os

# Explicitly read instructions with UTF-8
with open(os.path.join(os.path.dirname(__file__), "instructions.md"), "r", encoding="utf-8") as f:
    instructions_content = f.read()

graphic_designer = Agent(
    name="GraphicDesigner",
    description="Artisan Pro production agent for social media content creation using Kie.ai APIs",
    instructions=instructions_content,
    model="gpt-5.2",
    reasoning_effort="low",
    tools_folder="./tools",
)
