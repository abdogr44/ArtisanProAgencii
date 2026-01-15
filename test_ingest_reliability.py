import os
import sys
import unittest
import shutil
import json
import uuid
import tempfile
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "ArtisanProAgencii")))

from publishing_orchestrator.tools.ProjectFileIngestTool import ProjectFileIngestTool
from manuscript_intake.tools.ManuscriptCompilerTool import ManuscriptCompilerTool
from storage_backends import get_storage_backend, LocalFSBackend

class TestIngestionReliability(unittest.TestCase):
    
    def setUp(self):
        self.test_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_ingest_storage"))
        self.project_id = "test-proj-ingest"
        
        # Override env vars for local storage
        os.environ["ATHAR_PROJECT_ROOT"] = self.test_root
        os.environ["ATHAR_STORAGE_BACKEND"] = "local"
        
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        os.makedirs(self.test_root)
        
        # Create dummy DOCX fixture
        self.fixture_file = os.path.join(self.test_root, "test_manuscript.docx")
        self._create_dummy_docx(self.fixture_file)

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def _create_dummy_docx(self, path):
        # We'll create a text file but pretend it's docx for the ingest tool tests.
        # For compiler tests, we'll mock the parser or use a real python-docx if available.
        with open(path, "wb") as f:
            f.write(b"PKG\x03\x04" + b"dummy_content" * 100)

    @patch("requests.get")
    def test_project_file_ingest_tool(self, mock_get):
        """Test that Ingest Tool downloads file and saves to private storage."""
        print("\nTest: ProjectFileIngestTool")
        
        # Mock download response
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"PKG\x03\x04", b"dummy_content" * 100]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        tool = ProjectFileIngestTool(
            project_id=self.project_id,
            file_url="http://example.com/ms.docx",
            original_filename="manuscript.docx"
        )
        
        result_json = tool.run()
        print(f"Ingest Result: {result_json[:200]}...")
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        source_data = result["data"]["source"]
        self.assertEqual(source_data["filename"], "manuscript.docx")
        self.assertTrue(source_data["storage_uri"].startswith("file://"))
        
        # Verify file exists in private storage
        storage_path = source_data["storage_uri"].replace("file://", "")
        if os.name == 'nt' and storage_path.startswith("/") and ":" in storage_path:
             storage_path = storage_path.lstrip("/")
             
        self.assertTrue(os.path.exists(storage_path))
        print(f"  [OK] File ingested to: {storage_path}")
        return source_data

    @patch("manuscript_intake.tools.ManuscriptCompilerTool.ManuscriptCompilerTool._parse_docx")
    def test_manuscript_compiler_resolves_uri(self, mock_parse):
        """Test that Compiler Tool resolves storage URI and processes it."""
        print("\nTest: ManuscriptCompilerTool with Storage URI")
        
        # Pre-seed a file in storage
        backend = get_storage_backend()
        stored_uri = backend.put_file(self.fixture_file, f"private/uploads/{self.project_id}/manuscript.docx")
        
        # Mock parser output
        mock_parse.return_value = {
            "full_text": "Chapter 1\nHello World",
            "headings": [{"level": 1, "text": "Chapter 1"}],
            "paragraphs": ["Hello World"]
        }
        
        tool = ManuscriptCompilerTool(
            source_file="", # Should be ignored
            source_storage_uri=stored_uri,
            title="Test Book",
            author="Test Author",
            storage_root=self.test_root
        )
        
        result_json = tool.run()
        print(f"Compiler Result: {result_json[:200]}...")
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["title"], "Test Book")
        
        # Verify call to parser used a local temp file path, NOT the original URI
        args, _ = mock_parse.call_args
        resolved_path = args[0]
        print(f"  [OK] Resolved path passed to parser: {resolved_path}")
        self.assertTrue(os.path.exists(resolved_path))
        self.assertNotEqual(resolved_path, stored_uri)

if __name__ == "__main__":
    unittest.main()
