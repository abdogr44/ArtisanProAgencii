import unittest
import os
import json
import shutil
import time
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

# Tool imports
from manuscript_intake.tools.ManuscriptCompilerTool import ManuscriptCompilerTool
from publishing_orchestrator.tools.GateEnforcementTool import GateEnforcementTool
from reader_packbuilder.tools.ReaderBundleValidatorTool import ReaderBundleValidatorTool
from style_editor.tools.StyleSuggestionTool import StyleSuggestionTool

class TestProductionSuite(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "test_prod_suite"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.manuscripts_dir = os.path.join(self.test_dir, "private", "manuscripts")
        self.states_dir = os.path.join(self.test_dir, "private", "states")
        os.makedirs(self.manuscripts_dir)
        os.makedirs(self.states_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('manuscript_intake.tools.ManuscriptCompilerTool.ManuscriptCompilerTool._parse_docx')
    def test_parsing_confidence_docx(self, mock_parse):
        """Verify DOCX parsing sets high confidence."""
        mock_parse.return_value = {"headings": [], "paragraphs": ["Content"], "full_text": "Content"}
        
        # Create dummy file
        docx_path = os.path.join(self.test_dir, "test.docx")
        with open(docx_path, "w") as f:
            f.write("dummy")
            
        tool = ManuscriptCompilerTool(
            source_file=docx_path,
            title="Test Book",
            author="Tester",
            storage_root=self.test_dir
        )
        
        result = json.loads(tool.run())
        self.assertTrue(result["success"])
        
        # Check generated manuscript
        ms_path = result["storage_path"]
        with open(ms_path, "r") as f:
            data = json.load(f)
            
        self.assertEqual(data["parsing_confidence"], "high")
        print("\n[PASS] DOCX Parsing Confidence High")

    @patch('manuscript_intake.tools.ManuscriptCompilerTool.ManuscriptCompilerTool._parse_pdf')
    def test_parsing_confidence_pdf(self, mock_parse):
        """Verify PDF parsing sets medium confidence."""
        mock_parse.return_value = {"headings": [], "paragraphs": ["Content"], "full_text": "Content"}
        
        # Create dummy file
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "w") as f:
            f.write("dummy")
            
        tool = ManuscriptCompilerTool(
            source_file=pdf_path,
            title="Test Book",
            author="Tester",
            storage_root=self.test_dir
        )
        
        result = json.loads(tool.run())
        self.assertTrue(result["success"])
        
        # Check generated manuscript
        ms_path = result["storage_path"]
        with open(ms_path, "r") as f:
            data = json.load(f)
            
        self.assertEqual(data["parsing_confidence"], "medium")
        print("\n[PASS] PDF Parsing Confidence Medium")

    def test_gate_regression_hash_check(self):
        """Verify gate sign-off is invalidated by content change."""
        # Setup state
        project_id = "test-gate-project"
        
        # 1. Create Manuscript
        ms_path = os.path.join(self.manuscripts_dir, f"{project_id}.json")
        with open(ms_path, "w") as f:
            json.dump({"id": project_id, "content": "Version 1"}, f)
            
        # 2. Create State
        state_path = os.path.join(self.states_dir, f"{project_id}.json")
        with open(state_path, "w") as f:
            json.dump({
                "project_id": project_id,
                "current_stage": "proofed_1", # Ready for PASS1
                "issues": [],
                "sign_offs": []
            }, f)
            
        # 3. Sign Off
        tool = GateEnforcementTool(
            project_id=project_id,
            action="sign",
            gate="PASS1",
            signed_by="tester",
            storage_root=self.test_dir
        )
        res = json.loads(tool.run())
        self.assertTrue(res["success"])
        original_hash = res["input_hash"]
        
        # 4. Modify Manuscript
        with open(ms_path, "w") as f:
            json.dump({"id": project_id, "content": "Version 2"}, f)
            
        # 5. Check Gate
        tool.action = "check"
        res = json.loads(tool.run())
        
        # Should be 'is_signed': False or invalidation warning
        # My implementation sets is_signed = False if hash mismatches
        self.assertFalse(res["is_signed"])
        self.assertIn("invalidation_warning", res)
        print("\n[PASS] Gate Regression (Hash Invalidation)")

    def test_bundle_validator(self):
        """Verify Bundle Validator catches leaks."""
        project_id = "test-bundle-project"
        
        # 1. Canonical MS with whitelist
        ms_path = os.path.join(self.manuscripts_dir, f"{project_id}.json")
        with open(ms_path, "w") as f:
            json.dump({
                "version": "1.0.0",
                "manuscript_id": project_id,
                "source_file": "test.docx",
                "source_format": "docx",
                "parsing_confidence": "high",
                "metadata": {
                    "title": "Test Book",
                    "author": "Tester",
                    "language": "en"
                },
                "chapters": [],
                "sample_whitelist": {"chapter_ids": ["ch1"]}
            }, f)
            
        # 2. Create Bad Bundle (contains ch2 not in whitelist)
        bundle_path = os.path.join(self.test_dir, "bad_bundle.json")
        with open(bundle_path, "w") as f:
            json.dump({
                "bundle_version": "1.0.0",
                "bundle_type": "sample",
                "book_id": project_id,
                "metadata": {
                    "title": "Test Book",
                    "author": "Tester",
                    "total_chapters": 1,
                    "sample_chapters": 1
                },
                "toc": [],
                "sample_content": [{"id": "ch1", "title": "Ch1", "order": 1, "content_blocks": []}],
                "allowed_sample_ids": ["ch1", "ch2"], # ch2 unauthorized
                "integrity": {
                    "version": "1.0.0",
                    "checksum": "dummy",
                    "manuscript_id": project_id
                }
            }, f)
            
        tool = ReaderBundleValidatorTool(
            project_id=project_id,
            bundle_path=bundle_path,
            storage_root=self.test_dir
        )
        
        res = json.loads(tool.run())
        self.assertFalse(res["valid"])
        self.assertIn("unauthorized chapters", str(res["errors"]))
        print("\n[PASS] Bundle Validator (Unauthorized Chapter)")

    def test_idempotency_styling(self):
        """Verify running styling tool twice doesn't break state."""
        project_id = "test-style-project"
        
        # 1. Manuscript
        ms_path = os.path.join(self.manuscripts_dir, f"{project_id}.json")
        with open(ms_path, "w") as f:
            json.dump({"chapters": [{"title": "Ch1", "sections": []}]}, f)
            
        # 2. State
        state_path = os.path.join(self.states_dir, f"{project_id}.json")
        with open(state_path, "w") as f:
            json.dump({
                "project_id": project_id,
                "current_stage": "ingested",
                "artifacts": []
            }, f)
            
        tool = StyleSuggestionTool(
            project_id=project_id,
            storage_root=self.test_dir
        )
        
        # Run 1
        res1 = json.loads(tool.run())
        self.assertTrue(res1["success"])
        
        # Run 2
        res2 = json.loads(tool.run())
        self.assertTrue(res2["success"])
        
        # Check State
        with open(state_path, "r") as f:
            state = json.load(f)
            
        # Should have 2 reports, not crashed
        style_reports = [a for a in state["artifacts"] if a["type"] == "style_report"]
        self.assertEqual(len(style_reports), 2)
        print("\n[PASS] Idempotency (Style Tool)")

if __name__ == "__main__":
    unittest.main()
