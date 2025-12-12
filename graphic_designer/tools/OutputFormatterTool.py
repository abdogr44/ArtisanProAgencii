from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import uuid

class OutputFormatterTool(BaseTool):
    """
    Formats the final JSON response according to the specified schema.
    Returns structured output with request_id, images, caption, PDF URL, and metadata.
    """
    images_data: list[dict] = Field(
        ..., description="List of image objects with size, variant, prompt, url, metadata"
    )
    caption: str = Field(
        ..., description="Suggested social media caption (150 characters max)"
    )
    slides_pdf_path: str = Field(
        default="", description="Path to generated PDF slide deck"
    )
    zipped_assets_path: str = Field(
        default="", description="Path to ZIP archive with all assets"
    )
    brief: str = Field(
        default="", description="Original creative brief"
    )
    brand: str = Field(
        default="", description="Brand name or identifier"
    )
    style: str = Field(
        default="", description="Style theme used"
    )
    iterations: int = Field(
        default=1, description="Number of generation iterations performed"
    )
    
    def run(self):
        """
        Creates the final formatted JSON output matching the required schema.
        Returns a complete response object.
        """
        # Step 1: Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Step 2: Truncate caption if needed
        caption_truncated = self.caption[:150] if len(self.caption) > 150 else self.caption
        
        # Step 3: Build response object
        response = {
            "request_id": request_id,
            "status": "done",
            "brief": self.brief,
            "images": self.images_data,
            "caption": caption_truncated,
            "slides_pdf": self.slides_pdf_path,
            "zipped_assets": self.zipped_assets_path,
            "metadata": {
                "brand": self.brand,
                "style": self.style,
                "iterations": self.iterations,
                "total_images": len(self.images_data)
            },
            "audit_log": []  # Populated by AuditLoggerTool
        }
        
        # Step 4: Return formatted JSON
        return json.dumps(response, indent=2)

if __name__ == "__main__":
    # Test case: Format sample output
    sample_images = [
        {
            "id": "img1",
            "size": "1080x1080",
            "variant": "bold",
            "prompt": "Eye-catching social media graphic...",
            "url": "https://example.com/img1.png",
            "meta": {"seed": 12345, "steps": 28}
        },
        {
            "id": "img2",
            "size": "1200x628",
            "variant": "conservative",
            "prompt": "Professional social media graphic...",
            "url": "https://example.com/img2.png",
            "meta": {"seed": 67890, "steps": 28}
        }
    ]
    
    tool = OutputFormatterTool(
        images_data=sample_images,
        caption="Transform your workflow with our new productivity app! 🚀 #ProductivityTips #WorkSmarter",
        slides_pdf_path="./files/slide_deck.pdf",
        zipped_assets_path="./files/graphics_package.zip",
        brief="Create engaging graphics for app launch",
        brand="ProductivityApp",
        style="bold and modern",
        iterations=1
    )
    result = tool.run()
    print(result)
