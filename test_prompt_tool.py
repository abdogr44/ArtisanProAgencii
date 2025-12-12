from graphic_designer.tools.PromptSynthesizerTool import PromptSynthesizerTool
import json

def test_athar_signature():
    print("Testing Athar Signature...")
    tool = PromptSynthesizerTool(
        brief="We need a visual for inner healing using a single lavender stem.",
        use_athar_signature=True
    )
    result = tool.run()
    data = json.loads(result)
    
    if 'athar_signature' in data:
        print("[PASS] key 'athar_signature' found.")
        prompt = data['athar_signature']['prompt']
        print(f"Generated Prompt: {prompt}")
        
        expected = ["sacred void", "Kintsugi Gold", "Abyssal Teal", "lavender stem"]
        if all(e in prompt for e in expected):
            print("[PASS] All expected Athar visual elements found.")
        else:
            print("[FAIL] Missing elements.")
    else:
        print("[FAIL] 'athar_signature' key not found.")

if __name__ == "__main__":
    test_athar_signature()
