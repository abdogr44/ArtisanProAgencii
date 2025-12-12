from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

class KieImageGenerateTool(BaseTool):
    """
    Calls Kie.ai Nano Banana Pro text-to-image generation API endpoint.
    Creates a task and returns the task_id for status polling.
    Implements automatic retry logic for 5xx server errors.
    """
    prompt: str = Field(
        ..., description="Text prompt describing the image to generate"
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
    image_input: list = Field(
        default=[], description="Optional list of input image URLs for image-to-image"
    )
    callback_url: str = Field(
        default="", description="Optional callback URL for async notifications"
    )
    
    def run(self):
        """
        Creates an image generation task using Kie.ai Nano Banana Pro API.
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
        
        # Build input payload according to Nano Banana Pro spec
        payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": self.prompt,
                "image_input": self.image_input,
                "aspect_ratio": self.aspect_ratio,
                "resolution": self.resolution,
                "output_format": self.output_format
            }
        }
        
        # Add callback URL if provided
        if self.callback_url:
            payload["callBackUrl"] = self.callback_url
        
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
                    
                    # Check for API-level error codes (e.g. code != 0)
                    api_code = response_data.get('code')
                    if api_code is not None and api_code != 0:
                         return json.dumps({
                            'status': 'error',
                            'message': f"API Error: {response_data.get('msg', 'Unknown error')} (Code {api_code})",
                            'response': response_data
                        }, indent=2)

                    # Extract task_id from response
                    task_id = response_data.get('data', {}).get('taskId', '')
                    
                    if not task_id:
                         return json.dumps({
                            'status': 'error',
                            'message': "No taskId returned in response data",
                            'response': response_data
                        }, indent=2)

                    return json.dumps({
                        'status': 'success',
                        'task_id': task_id,
                        'response': response_data,
                        'prompt_used': self.prompt,
                        'aspect_ratio': self.aspect_ratio,
                        'resolution': self.resolution,
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
    # Test case: Generate a simple image with Nano Banana Pro
    tool = KieImageGenerateTool(
        prompt="Comic poster: cool banana hero in shades leaps from sci-fi pad. Modern, vibrant, professional social media graphic.",
        aspect_ratio="1:1",
        resolution="1K",
        output_format="png"
    )
    result = tool.run()
    print(result)
