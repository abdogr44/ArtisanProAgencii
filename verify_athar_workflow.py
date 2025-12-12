from agency import create_agency
import time
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def verify_athar_workflow():
    print("Initializing Athar Agency...")
    agency = create_agency()
    
    # 1. Test SocialMediaWriter Tone & "Spirit"
    print("\n--- TEST 1: SocialMediaWriter Tone ---")
    post_request = "Write a post for Athar about 'Inner Healing'."
    print(f"User Request: {post_request}")
    
    response_text = agency.get_completion(post_request, yield_messages=False)
    print("Response:")
    print(response_text)
    
    # Simple checks
    response_str = str(response_text).lower()
    if "healing" in response_str and "advice" not in response_str:
        print("[PASS] Tone seems appropriate (mentions healing, avoids direct advice).")
    else:
        print("[WARNING] check tone manually.")

    # 2. Test Designer Integration (Simulated via prompting the writer to get an image)
    # Note: In a real chat, the writer would call the designer. Here we check if the writer *tries* to call it or if we can invoke designer directly to test the tool.
    
    print("\n--- TEST 2: GraphicDesigner Athar Signature ---")
    # We will manually invoke the designer to check if it respects the "Athar Style" command
    # But strictly speaking, we want to see if the writer asks for it. 
    # Let's ask the agency to do both.
    
    complex_request = "Write a post about 'Silence' and generate an image for it in the Athar style."
    print(f"\nUser Request: {complex_request}")
    
    # This might take longer as it involves image generation
    try:
        response_complex = agency.get_completion(complex_request, yield_messages=False)
        print("Response:")
        print(response_complex)
        
        # Check if "Athar Signature" was likely used in the tool call (we can't see tool calls strictly here without logs, but we can infer from output if it describes the image)
        if "athar signature" in str(response_complex).lower() or "sacred void" in str(response_complex).lower():
             print("[PASS] Writer likely requested Athar style.")
        else:
             print("[NOTE] Check audit logs or output to confirm image style.")
             
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    verify_athar_workflow()
