"""
Simple test script to verify GraphicDesigner agency is properly configured.
Tests agent loading and tool availability without requiring API keys.
"""

import sys
import os

def test_agency_structure():
    """Test that the agency structure is properly set up."""
    print("=" * 60)
    print("GraphicDesigner-A1 Agency - Structure Test")
    print("=" * 60)
    
    # Test 1: Import GraphicDesigner agent
    print("\n[OK] Test 1: Loading GraphicDesigner agent...")
    try:
        from graphic_designer import graphic_designer
        print(f"  [OK] Agent Name: {graphic_designer.name}")
        print(f"  [OK] Model: {graphic_designer.model}")
        print(f"  [OK] Description: {graphic_designer.description[:50]}...")
    except Exception as e:
        print(f"  [FAIL] Failed to load agent: {e}")
        return False
    
    # Test 2: Check tools folder
    print("\n[OK] Test 2: Verifying tools...")
    tools_dir = os.path.join("graphic_designer", "tools")
    if os.path.exists(tools_dir):
        tools = [f for f in os.listdir(tools_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"  [OK] Found {len(tools)} tool files")
        for tool in sorted(tools):
            print(f"     - {tool}")
    else:
        print(f"  [FAIL] Tools directory not found")
        return False
    
    # Test 3: Import and test a simple tool (BriefGeneratorTool)
    print("\n[OK] Test 3: Testing BriefGeneratorTool (no API required)...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'graphic_designer', 'tools'))
        from BriefGeneratorTool import BriefGeneratorTool
        
        tool = BriefGeneratorTool(
            extracted_text="Create engaging social media graphics for a product launch",
            user_prompt="Modern and bold style"
        )
        result = tool.run()
        print(f"  [OK] Tool executed successfully")
        print(f"  [OK] Result preview: {result[:100]}...")
    except Exception as e:
        print(f"  [FAIL] Tool test failed: {e}")
        return False
    
    # Test 4: Check agency configuration
    print("\n[OK] Test 4: Verifying agency configuration...")
    try:
        from agency import create_agency
        agency = create_agency()
        print(f"  [OK] Agency created: {agency.name}")
        # Agency structure can vary, just verify it exists
        print(f"  [OK] Agency initialized successfully")
    except Exception as e:
        print(f"  [FAIL] Agency configuration test failed: {e}")
        return False
    
    # Test 5: Check environment setup
    print("\n[OK] Test 5: Checking environment configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    kie_key = os.getenv('KIE_API_KEY')
    
    if not openai_key or 'your_' in openai_key:
        print("  [WARN] OPENAI_API_KEY not configured (create .env from .env.template)")
    else:
        print(f"  [OK] OPENAI_API_KEY configured")
    
    if not kie_key or 'your_' in kie_key:
        print("  [WARN] KIE_API_KEY not configured (required for image generation)")
    else:
        print(f"  [OK] KIE_API_KEY configured")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All structure tests passed!")
    print("=" * 60)
    print("\nTo run the full agency with real image generation:")
    print("1. Copy .env.template to .env")
    print("2. Add your OPENAI_API_KEY and KIE_API_KEY")
    print("3. Run: python agency.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_agency_structure()
    sys.exit(0 if success else 1)
