from social_media_writer.tools.BookKnowledgeTool import BookKnowledgeTool
import os

def test_book_tool():
    print("Testing BookKnowledgeTool...")
    
    # Test 1: Random Passage
    print("\n--- Test 1: Random Passage ---")
    tool = BookKnowledgeTool(query="")
    result = tool.run()
    print(f"Result (Random):\n{result}")
    
    if "Error" in result:
        print("[FAIL] Tool returned error.")
    else:
        print("[PASS] Retrieved random passage.")

    # Test 2: Specific Query
    print("\n--- Test 2: Query for 'lavender' ---")
    tool_q = BookKnowledgeTool(query="lavender")
    result_q = tool_q.run()
    print(f"Result (Query):\n{result_q}")
    
    if "lavender" in result_q.lower() and "scent" in result_q.lower():
        print("[PASS] Retrieved relevant quote.")
    else:
        print("[FAIL] Content mismtach.")

    # Test 3: New Book 'Watini' (Pulse)
    print("\n--- Test 3: Query for 'نبضة' (Pulse) from Watini ---")
    tool_w = BookKnowledgeTool(query="نبضة")
    result_w = tool_w.run()
    print(f"Result (Watini):\n{result_w}")
    
    # Test 4: New Book 'Amwaj' (Confidence)
    print("\n--- Test 4: Query for 'الثقة' (Confidence) from Amwaj ---")
    tool_a = BookKnowledgeTool(query="الثقة")
    result_a = tool_a.run()
    print(f"Result (Amwaj):\n{result_a}")

if __name__ == "__main__":
    test_book_tool()
