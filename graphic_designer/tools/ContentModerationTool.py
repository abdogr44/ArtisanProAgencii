from agency_swarm.tools import BaseTool
from pydantic import Field
from PIL import Image
import os
import json

class ContentModerationTool(BaseTool):
    """
    Runs basic content safety checks on generated images.
    Flags NSFW or potentially harmful content using simple heuristics.
    Note: Production systems should use dedicated moderation APIs.
    """
    image_path: str = Field(
        ..., description="Local file path to the image to moderate"
    )
    
    def run(self):
        """
        Performs basic content safety checks on the image.
        Returns moderation status and any flags.
        """
        # Step 1: Validate file exists
        if not os.path.exists(self.image_path):
            return json.dumps({
                'status': 'error',
                'message': f'File not found: {self.image_path}'
            }, indent=2)
        
        # Step 2: Load image
        try:
            img = Image.open(self.image_path)
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error loading image: {str(e)}'
            }, indent=2)
        
        # Step 3: Basic heuristic checks
        # Note: This is a simplified placeholder. Production systems should use
        # dedicated moderation APIs like Google Cloud Vision, AWS Rekognition, etc.
        
        results = {
            'status': 'safe',
            'flags': [],
            'confidence': 'low',  # Indicates this is basic heuristic checking
            'recommendations': []
        }
        
        # Check image dimensions (unusually small or large might indicate issues)
        width, height = img.size
        if width < 100 or height < 100:
            results['flags'].append('unusually_small_dimensions')
            results['recommendations'].append('Image dimensions are very small, verify quality')
        
        if width > 8000 or height > 8000:
            results['flags'].append('unusually_large_dimensions')
            results['recommendations'].append('Image dimensions are very large, consider resizing')
        
        # Check aspect ratio
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio > 5 or aspect_ratio < 0.2:
            results['flags'].append('unusual_aspect_ratio')
            results['recommendations'].append('Image has unusual aspect ratio')
        
        # Step 4: Return results
        # If there are any flags, mark as 'review_recommended'
        if results['flags']:
            results['status'] = 'review_recommended'
        else:
            results['status'] = 'safe'
        
        results['image_path'] = self.image_path
        results['dimensions'] = f"{width}x{height}"
        results['note'] = 'This is basic heuristic checking. For production, integrate dedicated moderation APIs.'
        
        return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Test case: Create and moderate a test image
    import tempfile
    from PIL import Image
    
    # Create test image
    img = Image.new('RGB', (1080, 1080), color='blue')
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name)
        test_file = f.name
    
    tool = ContentModerationTool(image_path=test_file)
    result = tool.run()
    print(result)
    
    # Cleanup
    os.unlink(test_file)
