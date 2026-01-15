import os
import json
import shutil
from reader_packbuilder.tools.ReaderBundleValidatorTool import ReaderBundleValidatorTool

def setup_test_env():
    if os.path.exists("test_validator_storage"):
        shutil.rmtree("test_validator_storage")
    os.makedirs("test_validator_storage/private/manuscripts", exist_ok=True)
    
    # Canonical Manuscript
    manuscript = {
        "version": "1.0.0",
        "manuscript_id": "test-project",
        "source_file": "test.docx",
        "source_format": "docx",
        "metadata": {
            "title": "Test Book",
            "author": "Tester",
            "language": "en"
        },
        "chapters": [
            {"id": "ch1", "title": "Chapter 1", "order": 1},
            {"id": "ch2", "title": "Chapter 2", "order": 2},
            {"id": "ch3", "title": "Chapter 3 (Private)", "order": 3}
        ],
        "sample_whitelist": {
            "chapter_ids": ["ch1", "ch2"],
            "max_percentage": 20.0
        }
    }
    with open("test_validator_storage/private/manuscripts/test-project.json", "w") as f:
        json.dump(manuscript, f)

    return manuscript

def create_bundle(path, allowed_ids, content_ids, content_text="Safe content"):
    bundle = {
        "bundle_version": "1.0.0",
        "bundle_type": "sample",
        "book_id": "test-project",
        "metadata": {
            "title": "Test Book",
            "author": "Tester",
            "total_chapters": 3,
            "sample_chapters": len(content_ids)
        },
        "toc": [],
        "allowed_sample_ids": allowed_ids,
        "sample_content": [
            {
                "id": cid, 
                "title": f"Chapter {cid}", 
                "order": i, 
                "content_blocks": [
                    {"id": f"b{i}", "type": "paragraph", "content": content_text}
                ]
            } for i, cid in enumerate(content_ids)
        ],
        "integrity": {
            "version": "1.0.0",
            "checksum": "dummy",
            "manuscript_id": "test-project"
        }
    }
    with open(path, "w") as f:
        json.dump(bundle, f)

def test_validator():
    print("Setting up test environment...")
    setup_test_env()
    
    tool = ReaderBundleValidatorTool(
        project_id="test-project",
        bundle_path="test_validator_path.json",
        storage_root="./test_validator_storage"
    )
    
    print("\n1. Testing Valid Bundle...")
    create_bundle("test_validator_path.json", ["ch1"], ["ch1"])
    result = json.loads(tool.run())
    if result.get("success") and result.get("valid"):
        print("  [OK] Valid bundle passed")
    else:
        print(f"  [FAIL] Valid bundle failed: {result}")

    print("\n2. Testing Unauthorized Chapter ID (Whitelist Violation)...")
    create_bundle("test_validator_path.json", ["ch1", "ch3"], ["ch1", "ch3"]) # ch3 is not in whitelist
    result = json.loads(tool.run())
    if not result.get("valid") and "Bundle contains unauthorized chapters" in str(result.get("errors")):
        print("  [OK] Caught unauthorized chapter ID")
    else:
        print(f"  [FAIL] Failed to catch unauthorized ID: {result}")

    print("\n3. Testing Content Leak (Content not in allowed list)...")
    create_bundle("test_validator_path.json", ["ch1"], ["ch1", "ch2"]) # ch2 content present but not allowed
    result = json.loads(tool.run())
    if not result.get("valid") and "Content included for non-listed chapters" in str(result.get("errors")):
        print("  [OK] Caught content leak")
    else:
        print(f"  [FAIL] Failed to catch content leak: {result}")

    print("\n4. Testing Sensitive Keyword...")
    create_bundle("test_validator_path.json", ["ch1"], ["ch1"], content_text="This is strictly PRIVATE and CONFIDENTIAL")
    result = json.loads(tool.run())
    if result.get("warnings") and "CONFIDENTIAL" in str(result.get("warnings")):
        print("  [OK] Caught sensitive keyword")
    else:
        print(f"  [FAIL] Failed to catch keyword: {result}")

if __name__ == "__main__":
    test_validator()
