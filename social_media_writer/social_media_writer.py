from agency_swarm import Agent

import os

# Explicitly read instructions with UTF-8 to handle Arabic characters on Windows
with open(os.path.join(os.path.dirname(__file__), "instructions.md"), "r", encoding="utf-8") as f:
    instructions_content = f.read()

social_media_writer = Agent(
    name="SocialMediaWriter",
    description="A viral content creator and brand strategist who writes engaging social media content and coordinates with designers.",
    instructions=instructions_content,
    tools_folder="./tools",
    model="gpt-5.2",
    reasoning_effort="low",
)
