"""
Test script to verify the complete image generation workflow.
Tests: KieImageGenerateTool → KieImageStatusTool → ImagePostProcessorTool
"""

import sys
import os
import time
import json
import io
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the tools
from graphic_designer.tools.KieImageGenerateTool import KieImageGenerateTool
from graphic_designer.tools.KieImageStatusTool import KieImageStatusTool
from graphic_designer.tools.ImagePostProcessorTool import ImagePostProcessorTool

load_dotenv()

def test_image_generation_workflow():
    """Test the complete workflow from prompt to downloaded PNG/JPG"""
    
    print("=" * 80)
    print("TESTING IMAGE GENERATION WORKFLOW")
    print("=" * 80)
    
    # Step 1: Generate image with KieImageGenerateTool
    print("\n[STEP 1] Generating image with Kie.ai API...")
    print("-" * 80)
    
    prompt = """Minimalist square Instagram post design for a spiritual Arabic publishing brand called "Athar أثر". 
Warm off-white background with subtle golden accent elements. Centered elegant Arabic text reading 
"ما هو 'Athar أثر' فعليًا؟" in modern Arabic display typography. Clean, sophisticated, calm aesthetic."""
    
    generate_tool = KieImageGenerateTool(
        prompt=prompt,
        aspect_ratio="1:1",
        resolution="1K",
        output_format="png"
    )
    
    result = generate_tool.run()
    print(f"Generation Result:\n{result}\n")
    
    # Parse the result
    result_data = json.loads(result)
    
    if result_data.get('status') != 'success':
        print("❌ FAILED: Image generation failed")
        print(f"Error: {result_data.get('message', 'Unknown error')}")
        return False
    
    task_id = result_data.get('task_id')
    print(f"✅ Task created successfully! Task ID: {task_id}")
    
    # Step 2: Poll for completion
    print("\n[STEP 2] Polling for image completion...")
    print("-" * 80)
    
    status_tool = KieImageStatusTool(task_id=task_id)
    max_attempts = 60  # 60 attempts with 2-second intervals = 120 seconds max
    attempt = 0
    image_url = None
    
    while attempt < max_attempts:
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts}...", end=" ")
        
        status_result = status_tool.run()
        status_data = json.loads(status_result)
        print(f"DEBUG DATA: {json.dumps(status_data, indent=2)}")
        
        current_status = status_data.get('state')
        print(f"Status: {current_status}")
        
        if current_status == 'success':
            # Extract image URL from the result_urls list
            result_urls = status_data.get('result_urls', [])
            if result_urls:
                image_url = result_urls[0]
            print(f"✅ Image generation completed!")
            print(f"Image URL: {image_url}")
            break
        elif current_status == 'fail':
            print(f"❌ FAILED: Image generation failed")
            print(f"Error: {status_data.get('error', 'Unknown error')}")
            return False
        
        time.sleep(2)  # Wait 2 seconds before next poll
    
    if not image_url:
        print(f"❌ FAILED: Timeout after {max_attempts * 2} seconds")
        return False
    
    # Step 3: Download and convert to PNG
    print("\n[STEP 3] Downloading and converting to PNG...")
    print("-" * 80)
    
    processor_tool = ImagePostProcessorTool(
        image_url=image_url,
        output_format="png",
        filename="athar_test_image"
    )
    
    process_result = processor_tool.run()
    print(f"Processing Result:\n{process_result}\n")
    
    process_data = json.loads(process_result)
    
    if process_data.get('status') != 'success':
        print("❌ FAILED: Image processing failed")
        print(f"Error: {process_data.get('message', 'Unknown error')}")
        return False
    
    file_path = process_data.get('file_path')
    print(f"✅ Image saved successfully!")
    print(f"File path: {file_path}")
    print(f"Format: {process_data.get('format')}")
    print(f"Dimensions: {process_data.get('dimensions')}")
    
    # Step 4: Also test JPG conversion
    print("\n[STEP 4] Converting to JPG...")
    print("-" * 80)
    
    jpg_processor = ImagePostProcessorTool(
        image_url=image_url,
        output_format="jpg",
        filename="athar_test_image_jpg"
    )
    
    jpg_result = jpg_processor.run()
    jpg_data = json.loads(jpg_result)
    
    if jpg_data.get('status') == 'success':
        print(f"✅ JPG conversion successful!")
        print(f"File path: {jpg_data.get('file_path')}")
    else:
        print(f"⚠️  JPG conversion failed: {jpg_data.get('message')}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("WORKFLOW TEST COMPLETE")
    print("=" * 80)
    print(f"✅ Image generation: SUCCESS")
    print(f"✅ Status polling: SUCCESS")
    print(f"✅ PNG conversion: SUCCESS")
    print(f"✅ JPG conversion: {'SUCCESS' if jpg_data.get('status') == 'success' else 'FAILED'}")
    print(f"\nGenerated files:")
    print(f"  - PNG: {file_path}")
    if jpg_data.get('status') == 'success':
        print(f"  - JPG: {jpg_data.get('file_path')}")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("KIE_API_KEY"):
        print("❌ ERROR: KIE_API_KEY not found in environment variables")
        print("Please add it to your .env file")
        sys.exit(1)
    
    try:
        success = test_image_generation_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
