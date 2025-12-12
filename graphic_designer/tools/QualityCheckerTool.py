from agency_swarm.tools import BaseTool
from pydantic import Field
from PIL import Image
import os
import json

class QualityCheckerTool(BaseTool):
    """
    Validates visual quality of generated images using basic metrics.
    Checks resolution, file size, and format integrity.
    Returns pass/fail status and triggers regeneration if needed.
    """
    image_path: str = Field(
        ..., description="Local file path to the image to check"
    )
    min_width: int = Field(
        default=800, description="Minimum acceptable width in pixels"
    )
    min_height: int = Field(
        default=800, description="Minimum acceptable height in pixels"
    )
    min_file_size_kb: int = Field(
        default=50, description="Minimum acceptable file size in KB"
    )
    max_file_size_mb: int = Field(
        default=10, description="Maximum acceptable file size in MB"
    )
    
    def run(self):
        """
        Performs quality checks on the generated image.
        Returns quality assessment with pass/fail and recommendations.
        """
        # Step 1: Validate file exists
        if not os.path.exists(self.image_path):
            return json.dumps({
                'status': 'error',
                'message': f'File not found: {self.image_path}'
            }, indent=2)
        
        # Step 2: Get file size
        file_size_bytes = os.path.getsize(self.image_path)
        file_size_kb = file_size_bytes / 1024
        file_size_mb = file_size_kb / 1024
        
        # Step 3: Load and check image
        try:
            img = Image.open(self.image_path)
            width, height = img.size
            img_format = img.format
            img_mode = img.mode
        except Exception as e:
            return json.dumps({
                'status': 'fail',
                'quality': 'invalid',
                'message': f'Error loading image: {str(e)}',
                'needs_regeneration': True
            }, indent=2)
        
        # Step 4: Run quality checks
        checks = {
            'resolution': 'pass',
            'file_size': 'pass',
            'format_integrity': 'pass',
            'color_mode': 'pass'
        }
        issues = []
        
        # Check resolution
        if width < self.min_width or height < self.min_height:
            checks['resolution'] = 'fail'
            issues.append(f'Resolution {width}x{height} below minimum {self.min_width}x{self.min_height}')
        
        # Check file size
        if file_size_kb < self.min_file_size_kb:
            checks['file_size'] = 'warning'
            issues.append(f'File size {file_size_kb:.1f}KB unusually small (min {self.min_file_size_kb}KB)')
        
        if file_size_mb > self.max_file_size_mb:
            checks['file_size'] = 'fail'
            issues.append(f'File size {file_size_mb:.2f}MB exceeds maximum {self.max_file_size_mb}MB')
        
        # Check format
        if img_format not in ['PNG', 'JPEG', 'JPG', 'WEBP']:
            checks['format_integrity'] = 'warning'
            issues.append(f'Unusual format: {img_format}')
        
        # Check color mode
        if img_mode not in ['RGB', 'RGBA', 'L']:
            checks['color_mode'] = 'warning'
            issues.append(f'Unusual color mode: {img_mode}')
        
        # Step 5: Determine overall quality
        if 'fail' in checks.values():
            quality = 'fail'
            needs_regeneration = True
        elif 'warning' in checks.values():
            quality = 'warning'
            needs_regeneration = False
        else:
            quality = 'pass'
            needs_regeneration = False
        
        # Step 6: Return results
        results = {
            'status': 'success',
            'quality': quality,
            'needs_regeneration': needs_regeneration,
            'checks': checks,
            'issues': issues,
            'image_info': {
                'path': self.image_path,
                'dimensions': f"{width}x{height}",
                'format': img_format,
                'mode': img_mode,
                'file_size_kb': round(file_size_kb, 2),
                'file_size_mb': round(file_size_mb, 3)
            }
        }
        
        return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Test case: Check quality of a test image
    import tempfile
    from PIL import Image
    
    # Create test image
    img = Image.new('RGB', (1080, 1080), color='red')
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name)
        test_file = f.name
    
    tool = QualityCheckerTool(
        image_path=test_file,
        min_width=800,
        min_height=800
    )
    result = tool.run()
    print(result)
    
    # Cleanup
    os.unlink(test_file)
