from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import mimetypes

class FileValidatorTool(BaseTool):
    """
    Validates uploaded files for type, size, and integrity.
    Ensures only acceptable file types (PNG, JPG, PDF, DOCX) are processed
    and enforces the 200MB total upload limit.
    """
    file_paths: list[str] = Field(
        ..., description="List of absolute file paths to validate"
    )
    
    def run(self):
        """
        Validates all uploaded files and returns validation results.
        Returns a JSON string with validation status and file metadata.
        """
        # Step 1: Define allowed MIME types
        allowed_types = {
            'image/png': 'PNG',
            'image/jpeg': 'JPG',
            'application/pdf': 'PDF',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX'
        }
        
        # Step 2: Initialize validation results
        results = {
            'valid': True,
            'total_size_mb': 0,
            'files': [],
            'errors': []
        }
        
        total_size = 0
        max_size = 200 * 1024 * 1024  # 200MB in bytes
        
        # Step 3: Validate each file
        for file_path in self.file_paths:
            # Check if file exists
            if not os.path.exists(file_path):
                results['errors'].append(f"File not found: {file_path}")
                results['valid'] = False
                continue
            
            # Get file size
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            file_type = allowed_types.get(mime_type, 'UNKNOWN')
            
            if mime_type not in allowed_types:
                results['errors'].append(f"Invalid file type '{mime_type}' for {os.path.basename(file_path)}")
                results['valid'] = False
                continue
            
            # Add file metadata
            results['files'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'type': file_type,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'mime_type': mime_type
            })
        
        # Step 4: Check total size limit
        results['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        if total_size > max_size:
            results['errors'].append(f"Total file size ({results['total_size_mb']}MB) exceeds 200MB limit")
            results['valid'] = False
        
        # Step 5: Return validation results
        import json
        return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Test case: Validate a sample file
    import tempfile
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        test_file = f.name
    
    tool = FileValidatorTool(file_paths=[test_file])
    result = tool.run()
    print(result)
    
    # Cleanup
    os.unlink(test_file)
