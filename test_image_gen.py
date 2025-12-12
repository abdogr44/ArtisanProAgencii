"""
Test Kie.ai Image Generation Tools
Tests the actual image generation workflow
"""

import sys
import os
import time
import json

# Add tools directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'graphic_designer', 'tools'))

from KieImageGenerateTool import KieImageGenerateTool
from KieImageStatusTool import KieImageStatusTool

def test_image_generation():
    """Test the complete image generation workflow"""
    print("=" * 60)
    print("Kie.ai Image Generation Test")
    print("=" * 60)
    
    # Test 1: Generate an image
    print("\n[1/3] Creating image generation task...")
    
    gen_tool = KieImageGenerateTool(
        prompt="Modern Instagram post for productivity app: bold typography saying 'GET THINGS DONE' on vibrant gradient background, minimal design, professional",
        aspect_ratio="1:1",
        resolution="1K",
        output_format="png"
    )
    
    result = gen_tool.run()
    result_data = json.loads(result)
    
    print(f"Status: {result_data.get('status')}")
    
    if result_data.get('status') == 'success':
        task_id = result_data.get('task_id')
        print(f"Task ID: {task_id}")
        print(f"Prompt: {result_data.get('prompt_used')}")
        print(f"Aspect Ratio: {result_data.get('aspect_ratio')}")
        
        # Test 2: Poll for status
        print("\n[2/3] Polling for generation status...")
        
        max_attempts = 20
        for attempt in range(max_attempts):
            status_tool = KieImageStatusTool(task_id=task_id)
            status_result = status_tool.run()
            status_data = json.loads(status_result)
            
            state = status_data.get('state', 'unknown')
            print(f"  Attempt {attempt + 1}: {state}")
            
            if state == 'success':
                print("\n[3/3] Image generated successfully!")
                result_urls = status_data.get('result_urls', [])
                print(f"\nGenerated {len(result_urls)} image(s):")
                for i, url in enumerate(result_urls, 1):
                    print(f"  {i}. {url}")
                
                print("\n" + "=" * 60)
                print("[SUCCESS] Image generation test completed!")
                print("=" * 60)
                return True
                
            elif state == 'fail':
                print(f"\n[FAIL] Generation failed:")
                print(f"  Error code: {status_data.get('fail_code')}")
                print(f"  Error message: {status_data.get('fail_msg')}")
                return False
                
            elif state in ['waiting', 'queuing', 'generating']:
                time.sleep(3)  # Wait 3 seconds before next poll
                
            else:
                print(f"\n[UNKNOWN] Unexpected state: {state}")
                return False
        
        print("\n[TIMEOUT] Generation took too long (>60 seconds)")
        return False
        
    else:
        print(f"\n[ERROR] Failed to create generation task:")
        print(json.dumps(result_data, indent=2))
        return False

if __name__ == "__main__":
    print("\nTesting Kie.ai image generation workflow...")
    print("This will create a task, poll for status, and retrieve the result.\n")
    
    success = test_image_generation()
    
    if not success:
        print("\nTest failed. Check your KIE_API_KEY in .env file.")
        sys.exit(1)
