"""
Test script for GraphicDesigner Agency - Fixed encoding
"""

import asyncio
from agency import create_agency

async def test_agency():
    """Test the agency with a sample request"""
    print("=" * 60)
    print("Artisan Pro Agency - Test Run")
    print("=" * 60)
    
    # Create agency
    print("\n[1/3] Initializing agency...")
    agency = create_agency()
    print(f"[OK] Agency created: {agency.name}")
    
    # Test request
    test_prompt = """Create Instagram graphics for a productivity app launch. 
    Target audience: busy entrepreneurs. 
    Style: modern, vibrant, and professional.
    Include bold typography and minimal design elements."""
    
    print(f"\n[2/3] Sending request to GraphicDesigner...")
    print(f"Request: {test_prompt[:80]}...")
    
    try:
        # Send request asynchronously
        response = await agency.get_response(test_prompt)
        
        print(f"\n[3/3] Response received!")
        print("=" * 60)
        print("\nFinal Output:")
        print("-" * 60)
        
        # Write to file to avoid encoding issues
        with open("agency_response.txt", "w", encoding="utf-8") as f:
            f.write(response.final_output)
        
        print(f"\n[SUCCESS] Response saved to: agency_response.txt")
        print(f"[INFO] Response length: {len(response.final_output)} characters")
        
        # Print safe preview
        preview = response.final_output[:500].encode('ascii', 'replace').decode('ascii')
        print(f"\nPreview:\n{preview}...")
        
    except Exception as e:
        print(f"\n[ERROR] Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nStarting GraphicDesigner Agency test...")
    print("This will take a moment as the agent processes your request...\n")
    asyncio.run(test_agency())
