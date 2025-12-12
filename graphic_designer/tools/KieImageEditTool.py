from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

class KieImageEditTool(BaseTool):
    """
    Calls Kie.ai Nano Banana Pro image-to-image editing using createTask API.
    Accepts input images and prompt for editing operations.
    """
    init_image_url: str = Field(
        ..., description="URL of the source image to edit"
    )
    prompt: str = Field(
        ..., description="Text prompt describing the desired edits"
    )
    aspect_ratio: str = Field(
        default="1:1", description="Aspect ratio: '1:1', '16:9', '9:16', '4:3', '3:4'"
    )
    resolution: str = Field(
        default="1K", description="Resolution: '1K', '2K', '4K'"
    )
    output_format: str = Field(
        default="png", description="Output format: 'png', 'jpg', 'webp'"
    )
    
    def run(self):
        """
        Edits an existing image using Kie.ai Nano Banana Pro API.
        Returns task_id for status polling.
        """
        # Step 1: Get API key from environment
        api_key = os.getenv("KIE_API_KEY")
        if not api_key:
            return json.dumps({
                'status': 'error',
                'message': 'KIE_API_KEY not found in environment variables. Please add it to .env file.'
            }, indent=2)
        
        # Step 2: Prepare API request for Nano Banana Pro
        url = "https://api.kie.ai/api/v1/jobs/createTask"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build payload with image_input for image-to-image
        payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": self.prompt,
                "image_input": [self.init_image_url],  # Input images as array
                "aspect_ratio": self.aspect_ratio,
                "resolution": self.resolution,
                "output_format": self.output_format
            }
        }
        
        # Step 3: Make API call with retry logic
        max_retries = 2
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                # Check for 5xx server errors
                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return json.dumps({
                            'status': 'error',
                            'message': f'Server error after {max_retries} attempts: {response.status_code}',
                            'response': response.text
                        }, indent=2)
                
                # Handle successful response
                if response.status_code == 200:
                    response_data = response.json()
                    task_id = response_data.get('data', {}).get('taskId', '')
                    
                    return json.dumps({
                        'status': 'success',
                        'task_id': task_id,
                        'response': response_data,
                        'prompt_used': self.prompt,
                        'source_image': self.init_image_url,
                        'note': 'Use KieImageStatusTool with this task_id to check generation progress'
                    }, indent=2)
                else:
                    return json.dumps({
                        'status': 'error',
                        'status_code': response.status_code,
                        'message': response.text
                    }, indent=2)
                    
            except requests.exceptions.Timeout:
                return json.dumps({
                    'status': 'error',
                    'message': 'Request timeout after 60 seconds'
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    'status': 'error',
                    'message': f'Error during API call: {str(e)}'
                }, indent=2)
        
        return json.dumps({'status': 'error', 'message': 'Unexpected error in retry loop'}, indent=2)

if __name__ == "__main__":
    # Test case: Edit an image (mock URL for testing)
    tool = KieImageEditTool(
        init_image_url="https://example.com/sample-photo.jpg",
        prompt="Replace background with clean white studio background; enhance contrast",
        aspect_ratio="1:1",
        resolution="1K"
    )
    result = tool.run()
    print(result)
