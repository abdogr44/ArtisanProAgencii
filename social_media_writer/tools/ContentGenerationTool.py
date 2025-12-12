from agency_swarm.tools import BaseTool
from pydantic import Field
import os

class ContentGenerationTool(BaseTool):
    """
    Use this tool to format and validate social media content for specific platforms.
    This does not use an external AI, but structures the output and checks for constraints (length, hashtags, etc.).
    """
    
    platform: str = Field(
        ...,
        description="The target platform (e.g., 'LinkedIn', 'Twitter', 'Instagram')."
    )
    
    content: str = Field(
        ...,
        description="The drafted content to be formatted/validated."
    )
    
    def run(self) -> str:
        """
        Validates and formats the content. Returns a success message with analysis or an error if constraints are violated.
        """
        platform = self.platform.lower()
        length = len(self.content)
        
        analysis = f"Content Analysis for {self.platform}:\n"
        analysis += f"- Length: {length} characters\n"
        
        # Simple validation logic
        if platform == 'twitter' or platform == 'x':
            limit = 280
            if length > limit:
                return f"Error: Content exceeds Twitter limit of {limit} characters. Current length: {length}. Please shorten it."
            else:
                analysis += "- Status: Within limit.\n"
                
        elif platform == 'linkedin':
             if length > 3000:
                analysis += "- Warning: Content is quite long for LinkedIn. Consider breaking it up or ensuring the hook is very strong.\n"
             else:
                analysis += "- Status: Good length for LinkedIn.\n"
                
        elif platform == 'instagram':
            if len(self.content.split('#')) > 30:
                 return "Error: Too many hashtags (max 30)."
            analysis += "- Status: formatted for Instagram.\n"
            
        return f"Content successfully validated for {self.platform}.\n\n{analysis}\n\nFinal Output:\n{self.content}"
