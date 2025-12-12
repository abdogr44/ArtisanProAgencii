from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import json
import zipfile
import shutil

class ZipExportTool(BaseTool):
    """
    Packages all generated images and a metadata JSON file into a ZIP archive.
    Returns ZIP file path for easy download and distribution.
    """
    image_paths: list[str] = Field(
        ..., description="List of local file paths to images to include in ZIP"
    )
    metadata: dict = Field(
        ..., description="Metadata dictionary to save as JSON (prompts, settings, etc.)"
    )
    output_dir: str = Field(
        default="./graphic_designer/files", description="Directory to save the ZIP file"
    )
    zip_filename: str = Field(
        default="graphics_package.zip", description="Output ZIP filename"
    )
    
    def run(self):
        """
        Creates a ZIP archive containing all images and metadata.json.
        Returns the path to the ZIP file.
        """
        # Step 1: Validate inputs
        if not self.image_paths:
            return json.dumps({
                'status': 'error',
                'message': 'No image paths provided'
            }, indent=2)
        
        # Step 2: Prepare output directory
        os.makedirs(self.output_dir, exist_ok=True)
        zip_path = os.path.join(self.output_dir, self.zip_filename)
        
        # Step 3: Create ZIP file
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all images
                images_added = 0
                for img_path in self.image_paths:
                    if os.path.exists(img_path):
                        # Add to ZIP with just the filename (no directory structure)
                        arcname = os.path.basename(img_path)
                        zipf.write(img_path, arcname)
                        images_added += 1
                
                # Add metadata JSON
                metadata_json = json.dumps(self.metadata, indent=2)
                zipf.writestr('metadata.json', metadata_json)
                
            return json.dumps({
                'status': 'success',
                'zip_path': zip_path,
                'images_included': images_added,
                'total_items': images_added + 1,  # +1 for metadata.json
                'zip_size_mb': round(os.path.getsize(zip_path) / (1024 * 1024), 2)
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error creating ZIP file: {str(e)}'
            }, indent=2)

if __name__ == "__main__":
    # Test case: Create a ZIP with sample files
    import tempfile
    
    # Create temp test files
    test_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f"Test image {i}")
            test_files.append(f.name)
    
    metadata = {
        'project': 'Test Project',
        'date': '2025-12-08',
        'variants': ['bold', 'conservative', 'minimal']
    }
    
    tool = ZipExportTool(
        image_paths=test_files,
        metadata=metadata,
        zip_filename="test_package.zip"
    )
    result = tool.run()
    print(result)
    
    # Cleanup
    for f in test_files:
        os.unlink(f)
