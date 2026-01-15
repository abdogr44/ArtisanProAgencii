import os

def check_file_content(filepath, required_phrases):
    """Checks if a file contains all required phrases."""
    print(f"\nChecking {os.path.basename(filepath)}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        all_passed = True
        for phrase in required_phrases:
            if phrase in content:
                print(f"  [OK] Found: '{phrase}'")
            else:
                print(f"  [MISSING] '{phrase}'")
                all_passed = False
        return all_passed
    except Exception as e:
        print(f"  [FAIL] Error reading file: {e}")
        return False

def verify_instructions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Check Social Media Writer
    writer_file = os.path.join(base_dir, "social_media_writer", "instructions.md")
    writer_phrases = [
        "Poetic Strategist",
        "Monetize Silence",
        "Bridge Post",
        "Soft CTA",
        "BookKnowledgeTool"
    ]
    
    # 2. Check Graphic Designer
    designer_file = os.path.join(base_dir, "graphic_designer", "instructions.md")
    designer_phrases = [
        "Product Showcase",
        "Sacred Object",
        "Phone/Book is a Relic",
        "Kintsugi Gold" # Existing check
    ]
    
    # 3. Check Reviewer
    reviewer_file = os.path.join(base_dir, "reviewer", "instructions.md")
    reviewer_phrases = [
        "Marketing Validation",
        "Sanctuary vs. Bridge",
        "CTA Check",
        "Product Integration"
    ]
    
    print("=== STARTING STATIC VERIFICATION ===")
    
    results = [
        check_file_content(writer_file, writer_phrases),
        check_file_content(designer_file, designer_phrases),
        check_file_content(reviewer_file, reviewer_phrases)
    ]
    
    if all(results):
        print("\n[SUCCESS] ALL CHECKS PASSED: Instructions are correctly updated.")
    else:
        print("\n[WARNING] SOME CHECKS FAILED: Please review the missing phrases.")

if __name__ == "__main__":
    verify_instructions()
