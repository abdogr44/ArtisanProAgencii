from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class KieImageStatusTool(BaseTool):
    """
    Polls Kie.ai Nano Banana Pro generation status endpoint using task_id.
    Returns completion status and download URL when ready.
    """
    task_id: str = Field(
        ..., description="Task ID returned from Kie.ai Nano Banana Pro createTask request"
    )
    
    def run(self):
        """
        Checks the status of a Kie.ai Nano Banana Pro generation task.
        Returns task status and result URLs if complete.
        """
        # Step 1: Get API key from environment
        api_key = os.getenv("KIE_API_KEY")
        if not api_key:
            return json.dumps({
                'status': 'error',
                'message': 'KIE_API_KEY not found in environment variables. Please add it to .env file.'
            }, indent=2)
        
        # Step 2: Prepare API request for Nano Banana Pro recordInfo endpoint
        url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={self.task_id}"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # Step 3: Make API call
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                data = response_data.get('data', {})
                
                # Parse the state
                state = data.get('state', 'unknown')
                
                # Parse resultJson if generation is successful
                result_urls = []
                if state == 'success' and data.get('resultJson'):
                    try:
                        result_data = json.loads(data.get('resultJson'))
                        result_urls = result_data.get('resultUrls', [])
                    except:
                        pass
                
                return json.dumps({
                    'status': 'success',
                    'task_id': self.task_id,
                    'state': state,  # waiting, queuing, generating, success, fail
                    'result_urls': result_urls,
                    'fail_code': data.get('failCode', ''),
                    'fail_msg': data.get('failMsg', ''),
                    'complete_time': data.get('completeTime'),
                    'full_response': data
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
                'message': 'Request timeout after 30 seconds'
            }, indent=2)
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error during API call: {str(e)}'
            }, indent=2)

if __name__ == "__main__":
    # Test case: Check status (mock task_id for testing)
    tool = KieImageStatusTool(task_id="task_12345678")
    result = tool.run()
    print(result)
