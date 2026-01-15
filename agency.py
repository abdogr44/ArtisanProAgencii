from dotenv import load_dotenv
from agency_swarm import Agency

# Legacy agents (preserved for social media workflows)
from graphic_designer import graphic_designer
from reviewer import reviewer
from social_media_writer import social_media_writer

# New publishing pipeline agents
from publishing_orchestrator import publishing_orchestrator
from manuscript_intake import manuscript_intake
from style_editor import style_editor
from proofreader import proofreader
from formatter import formatter
from reader_packbuilder import reader_packbuilder
from release_packager import release_packager

import asyncio

load_dotenv()


def create_publishing_agency(load_threads_callback=None):
    """
    Create the Athar Publishing Pipeline agency.
    
    Entry agent: PublishingOrchestrator
    Pipeline: Ingest → Style Edit → Proof Pass 1 → Format → Proof Pass 2 → Bundle → Release
    """
    agency = Agency(
        publishing_orchestrator,  # Entry agent - orchestrates publishing pipeline
        communication_flows=[
            # Publishing pipeline flows
            (publishing_orchestrator, manuscript_intake),   # Orchestrator → Intake
            (publishing_orchestrator, style_editor),        # Orchestrator → Style Editor
            (publishing_orchestrator, proofreader),         # Orchestrator → Proofreader
            (publishing_orchestrator, formatter),           # Orchestrator → Formatter
            (publishing_orchestrator, reader_packbuilder),  # Orchestrator → Pack Builder
            (publishing_orchestrator, release_packager),    # Orchestrator → Release
            (publishing_orchestrator, graphic_designer),    # Orchestrator → Designer (covers)
        ],
        name="AtharPublishingAgency",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )
    return agency


def create_marketing_agency(load_threads_callback=None):
    """
    Create the legacy social media marketing agency.
    
    Entry agent: SocialMediaWriter
    Focus: Social media content and brand marketing
    """
    agency = Agency(
        social_media_writer,  # Entry agent - receives user requests
        communication_flows=[
            (social_media_writer, graphic_designer),  # Writer can ask Designer for images
            (graphic_designer, reviewer),             # GraphicDesigner sends outputs to Reviewer
        ],
        name="ArtisanProAgency",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )
    return agency


# Default to publishing agency
def create_agency(load_threads_callback=None):
    """Default agency creation - uses publishing pipeline."""
    return create_publishing_agency(load_threads_callback)


if __name__ == "__main__":
    # Run publishing agency in terminal demo mode
    agency = create_agency()
    agency.terminal_demo()