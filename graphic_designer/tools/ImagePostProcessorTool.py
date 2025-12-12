from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
from PIL import Image
from io import BytesIO
import json

class ImagePostProcessorTool(BaseTool):
    """
    Downloads generated images, performs format conversion (JPG/PNG/WebP),
    and optionally upscales images. Returns local file paths.
    """
    image_url: str = Field(
        ..., description="URL of the generated image to download and process"
    )
    output_format: str = Field(
        default="png", description="Output format: 'jpg', 'png', or 'webp'"
    )
    output_dir: str = Field(
        default="./graphic_designer/files", description="Directory to save processed images"
    )
    filename: str = Field(
        default="", description="Optional custom filename (without extension)"
    )
    upscale: bool = Field(
        default=False, description="Whether to upscale the image (2x)"
    )
    
    def run(self):
        """
        Downloads image from URL, converts format, and optionally upscales.
        Returns the local file path.
        """
        # Step 1: Download image
        try:
            response = requests.get(self.image_url, timeout=30)
            if response.status_code != 200:
                return json.dumps({
                    'status': 'error',
                    'message': f'Failed to download image: HTTP {response.status_code}'
                }, indent=2)
            
            # Step 2: Load image with PIL
            img = Image.open(BytesIO(response.content))
            
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error downloading or loading image: {str(e)}'
            }, indent=2)
        
        # Step 3: Optionally upscale (simple 2x resize)
        if self.upscale:
            new_size = (img.width * 2, img.height * 2)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Step 4: Prepare output path
        os.makedirs(self.output_dir, exist_ok=True)
        
        if self.filename:
            base_filename = self.filename
        else:
            # Generate filename from URL or timestamp
            import time
            base_filename = f"image_{int(time.time())}"
        
        output_format = self.output_format.lower()
        if output_format not in ['jpg', 'jpeg', 'png', 'webp']:
            output_format = 'png'
        
        extension = 'jpg' if output_format in ['jpg', 'jpeg'] else output_format
        output_path = os.path.join(self.output_dir, f"{base_filename}.{extension}")
        
        # Step 5: Save image
        try:
            if output_format == 'jpg' or output_format == 'jpeg':
                # Convert RGBA to RGB for JPG
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                img.save(output_path, 'JPEG', quality=95)
            elif output_format == 'png':
                img.save(output_path, 'PNG')
            elif output_format == 'webp':
                img.save(output_path, 'WEBP', quality=95)
            
            return json.dumps({
                'status': 'success',
                'file_path': output_path,
                'format': output_format,
                'dimensions': f"{img.width}x{img.height}",
                'upscaled': self.upscale
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error saving image: {str(e)}'
            }, indent=2)

if __name__ == "__main__":
    # Test case: Process a sample image URL
    # This will fail without a real image URL, but demonstrates the structure
    tool = ImagePostProcessorTool(
        image_url="https://via.placeholder.com/1080x1080",
        output_format="png",
        filename="test_output"
    )
    result = tool.run()
    print(result)
