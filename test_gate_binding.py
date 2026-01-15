import os
import json
import shutil
import time
from publishing_orchestrator.tools.GateEnforcementTool import GateEnforcementTool

def setup_test_env():
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    os.makedirs("test_storage/private/manuscripts", exist_ok=True)
    os.makedirs("test_storage/private/states", exist_ok=True)

    # Create dummy manuscript
    manuscript = {
        "id": "test-project",
        "content": "Original Content"
    }
    with open("test_storage/private/manuscripts/test-project.json", "w") as f:
        json.dump(manuscript, f)

    # Create dummy state
    state = {
        "project_id": "test-project",
        "current_stage": "proofed_1",
        "issues": [],
        "sign_offs": []
    }
    with open("test_storage/private/states/test-project.json", "w") as f:
        json.dump(state, f)

def test_gate_binding():
    print("Setting up test environment...")
    setup_test_env()
    
    tool = GateEnforcementTool(
        project_id="test-project",
        action="sign",
        gate="PASS1",
        signed_by="tester",
        storage_root="./test_storage"
    )
    
    print("\n1. Signing Gate PASS1...")
    result = json.loads(tool.run())
    if result.get("success"):
        print(f"  [OK] Signed successfully. Hash: {result.get('input_hash')}")
    else:
        print(f"  [FAIL] Failed to sign: {result.get('error')}")
        return

    # Check validity
    tool.action = "check"
    result = json.loads(tool.run())
    if result.get("requirements", {}).get("hash_valid"):
        print("  [OK] Gate check confirms hash valid")
    else:
        print("  [FAIL] Gate check says hash invalid")

    print("\n2. Modifying manuscript...")
    time.sleep(1)
    modified_manuscript = {
        "id": "test-project",
        "content": "Modified Content"
    }
    with open("test_storage/private/manuscripts/test-project.json", "w") as f:
        json.dump(modified_manuscript, f)

    print("\n3. Checking Gate PASS1 again...")
    result = json.loads(tool.run())
    
    if not result.get("requirements", {}).get("hash_valid"):
        print("  [OK] Gate check correctly identifies hash mismatch (invalid)")
        print(f"  Warning: {result.get('invalidation_warning')}")
    else:
        print("  [FAIL] Gate check failed to detect change!")

    print("\n4. Re-signing Gate PASS1...")
    tool.action = "sign"
    result = json.loads(tool.run())
    if result.get("success"):
        print(f"  [OK] Re-signed successfully. New Hash: {result.get('input_hash')}")
        # Verify old sign-off is gone/replaced
        with open("test_storage/private/states/test-project.json", "r") as f:
            state = json.load(f)
            if len(state["sign_offs"]) == 1:
                print("  [OK] Old sign-off replaced")
            else:
                print(f"  [FAIL] Sign-off list count incorrect: {len(state['sign_offs'])}")
    else:
        print(f"  [FAIL] Failed to re-sign: {result.get('error')}")

if __name__ == "__main__":
    test_gate_binding()
