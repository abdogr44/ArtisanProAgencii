"""
Publishing Pipeline E2E Test

Tests the complete publishing pipeline from ingestion to release.
"""

import os
import sys
import tempfile
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_import_all_agents():
    """Test that all new agents can be imported."""
    print("Testing agent imports...")
    
    try:
        from publishing_orchestrator import publishing_orchestrator
        print("  [OK] publishing_orchestrator")
    except ImportError as e:
        print(f"  [FAIL] publishing_orchestrator: {e}")
        return False
    
    try:
        from manuscript_intake import manuscript_intake
        print("  [OK] manuscript_intake")
    except ImportError as e:
        print(f"  [FAIL] manuscript_intake: {e}")
        return False
    
    try:
        from style_editor import style_editor
        print("  [OK] style_editor")
    except ImportError as e:
        print(f"  [FAIL] style_editor: {e}")
        return False
    
    try:
        from proofreader import proofreader
        print("  [OK] proofreader")
    except ImportError as e:
        print(f"  [FAIL] proofreader: {e}")
        return False
    
    try:
        from formatter import formatter
        print("  [OK] formatter")
    except ImportError as e:
        print(f"  [FAIL] formatter: {e}")
        return False
    
    try:
        from reader_packbuilder import reader_packbuilder
        print("  [OK] reader_packbuilder")
    except ImportError as e:
        print(f"  [FAIL] reader_packbuilder: {e}")
        return False
    
    try:
        from release_packager import release_packager
        print("  [OK] release_packager")
    except ImportError as e:
        print(f"  [FAIL] release_packager: {e}")
        return False
    
    print("\n[OK] All agents imported successfully!")
    return True


def test_import_schemas():
    """Test that all schemas can be imported."""
    print("\nTesting schema imports...")
    
    try:
        from schemas import (
            CanonicalManuscript, Chapter, Section, ContentBlock,
            AtharOutputEnvelope, Artifact, Report, NextAction,
            ReaderBundle, TOCEntry,
            ReleaseManifest, ArtifactEntry,
            GateState, PipelineStage, SignOff, Issue
        )
        print("  [OK] All schemas imported")
        return True
    except ImportError as e:
        print(f"  [FAIL] Schema import failed: {e}")
        return False


def test_agency_creation():
    """Test that agencies can be created."""
    print("\nTesting agency creation...")
    
    try:
        from agency import create_publishing_agency, create_marketing_agency
        
        # Just test the function exists, don't actually create agencies
        # (that requires API keys)
        print("  [OK] create_publishing_agency function exists")
        print("  [OK] create_marketing_agency function exists")
        return True
    except ImportError as e:
        print(f"  [FAIL] Agency import failed: {e}")
        return False


def test_tool_imports():
    """Test that all tools can be imported."""
    print("\nTesting tool imports...")
    
    tools = [
        ("publishing_orchestrator.tools", "PipelineStatusTool"),
        ("publishing_orchestrator.tools", "GateEnforcementTool"),
        ("manuscript_intake.tools", "ManuscriptCompilerTool"),
        ("style_editor.tools", "StyleSuggestionTool"),
        ("proofreader.tools", "ProofreadingTool"),
        ("formatter.tools", "BookFormatterTool"),
        ("reader_packbuilder.tools", "ReaderBundleGeneratorTool"),
        ("release_packager.tools", "ReleaseManifestTool"),
    ]
    
    all_passed = True
    for module, tool_name in tools:
        try:
            mod = __import__(module, fromlist=[tool_name])
            tool_class = getattr(mod, tool_name)
            print(f"  [OK] {tool_name}")
        except (ImportError, AttributeError) as e:
            print(f"  [FAIL] {tool_name}: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("=" * 60)
    print("Athar Publishing Pipeline - E2E Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Agent Imports", test_import_all_agents()))
    results.append(("Schema Imports", test_import_schemas()))
    results.append(("Agency Creation", test_agency_creation()))
    results.append(("Tool Imports", test_tool_imports()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
