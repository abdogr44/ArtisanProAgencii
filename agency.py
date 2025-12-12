from dotenv import load_dotenv
from agency_swarm import Agency

# Agent imports
from graphic_designer import graphic_designer
from reviewer import reviewer
from social_media_writer import social_media_writer

import asyncio

load_dotenv()

# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        social_media_writer,  # Entry agent - receives user requests
        communication_flows=[
            (social_media_writer, graphic_designer), # Writer can ask Designer for images
            (graphic_designer, reviewer),  # GraphicDesigner sends outputs to Reviewer
        ],
        name="ArtisanProAgency",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )
    return agency

if __name__ == "__main__":
    agency = create_agency()

    # test 1 message
    # async def main():
    #     response = await agency.get_response("Hello, how are you?")
    #     print(response)
    # asyncio.run(main())

    # run in terminal
    agency.terminal_demo()