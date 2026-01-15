"""
Manuscript Compiler Tool

Converts parsed DOCX/PDF content into the canonical manuscript JSON format.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Literal
import json
import os
import re
import hashlib
import uuid
from datetime import datetime, timezone


class ManuscriptCompilerTool(BaseTool):
    """
    Compiles parsed document content into canonical manuscript JSON.
    Creates structured representation with chapters, sections, and content blocks.
    """
    source_file: str = Field(
        ..., description="Path to the source DOCX or PDF file"
    )
    title: str = Field(
        ..., description="Book title"
    )
    author: str = Field(
        ..., description="Author name"
    )
    title_ar: Optional[str] = Field(
        default=None, description="Arabic title"
    )
    author_ar: Optional[str] = Field(
        default=None, description="Arabic author name"
    )
    language: str = Field(
        default="ar", description="Primary language code"
    )
    sample_chapters: int = Field(
        default=2, description="Number of initial chapters to include in sample"
    )
    storage_root: str = Field(
        default="./storage", description="Root storage directory"
    )
    
    def run(self) -> str:
        """
        Parse source file and compile canonical manuscript JSON.
        Returns JSON with manuscript details and storage path.
        """
        # Validate source file
        if not os.path.exists(self.source_file):
            return json.dumps({
                "success": False,
                "error": f"Source file not found: {self.source_file}"
            }, indent=2)
        
        # Determine format
        ext = os.path.splitext(self.source_file)[1].lower()
        if ext not in [".docx", ".pdf"]:
            return json.dumps({
                "success": False,
                "error": f"Unsupported format: {ext}. Use .docx or .pdf"
            }, indent=2)
            
        # Determine parsing confidence
        parsing_confidence = "high" if ext == ".docx" else "medium"
        
        # Parse document
        try:
            if ext == ".docx":
                parsed = self._parse_docx()
            else:
                parsed = self._parse_pdf()
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to parse document: {str(e)}"
            }, indent=2)
        
        # Generate manuscript ID
        manuscript_id = f"ms-{uuid.uuid4().hex[:8]}"
        
        # Build canonical structure
        canonical = {
            "version": "1.0.0",
            "manuscript_id": manuscript_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source_file": os.path.basename(self.source_file),
            "source_format": ext[1:],  # Remove dot
            
            "metadata": {
                "title": self.title,
                "title_ar": self.title_ar,
                "author": self.author,
                "author_ar": self.author_ar,
                "language": self.language,
                "description": None,
                "cover_image": None
            },
            
            "chapters": [],
            "total_word_count": 0,
            "total_chapters": 0,
            "total_sections": 0,
            
            "sample_whitelist": {
                "chapter_ids": [],
                "max_percentage": 20.0,
                "include_toc": True
            },
            "parsing_confidence": parsing_confidence
        }
        
        # Process into chapters
        chapters = self._structure_chapters(parsed)
        canonical["chapters"] = chapters
        canonical["total_chapters"] = len(chapters)
        canonical["total_sections"] = sum(len(ch.get("sections", [])) for ch in chapters)
        canonical["total_word_count"] = sum(ch.get("word_count", 0) for ch in chapters)
        
        # Set sample whitelist
        sample_ids = [ch["id"] for ch in chapters[:self.sample_chapters]]
        canonical["sample_whitelist"]["chapter_ids"] = sample_ids
        for ch in chapters:
            ch["is_sample_eligible"] = ch["id"] in sample_ids
        
        # Save to private storage
        private_path = os.path.join(self.storage_root, "private", "manuscripts")
        os.makedirs(private_path, exist_ok=True)
        
        manuscript_file = os.path.join(private_path, f"{manuscript_id}.json")
        with open(manuscript_file, "w", encoding="utf-8") as f:
            json.dump(canonical, f, ensure_ascii=False, indent=2)
        
        # Create project state
        state_path = os.path.join(self.storage_root, "private", "states")
        os.makedirs(state_path, exist_ok=True)
        
        project_state = {
            "project_id": manuscript_id,
            "current_stage": "ingested",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "manuscript_path": manuscript_file,
            "issues": [],
            "sign_offs": [],
            "artifacts": [
                {
                    "id": f"art-{uuid.uuid4().hex[:6]}",
                    "type": "manuscript",
                    "path": manuscript_file,
                    "visibility": "private",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ],
            "stage_history": [
                {
                    "from": "draft",
                    "to": "ingested",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        }
        
        state_file = os.path.join(state_path, f"{manuscript_id}.json")
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(project_state, f, indent=2)
        
        # Calculate checksum
        with open(manuscript_file, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        return json.dumps({
            "success": True,
            "manuscript_id": manuscript_id,
            "title": self.title,
            "author": self.author,
            "chapters_count": len(chapters),
            "total_words": canonical["total_word_count"],
            "sample_chapters": sample_ids,
            "storage_path": manuscript_file,
            "checksum": checksum,
            "stage": "ingested",
            "next_action": "Run style_editor for style suggestions"
        }, indent=2)
    
    def _parse_docx(self) -> dict:
        """Parse DOCX file and return content."""
        from docx import Document
        
        doc = Document(self.source_file)
        result = {
            "headings": [],
            "paragraphs": [],
            "full_text": ""
        }
        
        all_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            if para.style and para.style.name.startswith("Heading"):
                level = 1
                match = re.search(r"Heading\s*(\d)", para.style.name)
                if match:
                    level = int(match.group(1))
                result["headings"].append({
                    "level": level,
                    "text": text
                })
            else:
                result["paragraphs"].append(text)
            
            all_text.append(text)
        
        result["full_text"] = "\n\n".join(all_text)
        return result
    
    def _parse_pdf(self) -> dict:
        """Parse PDF file and return content."""
        import fitz  # PyMuPDF
        
        pdf = fitz.open(self.source_file)
        result = {
            "headings": [],
            "paragraphs": [],
            "full_text": ""
        }
        
        all_text = []
        for page in pdf:
            text = page.get_text().strip()
            if text:
                # Simple heuristic: treat short lines as potential headings
                lines = text.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Detect potential chapter headings
                    if self._is_chapter_heading(line):
                        result["headings"].append({
                            "level": 1,
                            "text": line
                        })
                    else:
                        result["paragraphs"].append(line)
                    
                    all_text.append(line)
        
        pdf.close()
        result["full_text"] = "\n\n".join(all_text)
        return result
    
    def _is_chapter_heading(self, text: str) -> bool:
        """Detect if text is a chapter heading."""
        patterns = [
            r"^chapter\s+\d+",
            r"^الفصل\s+",
            r"^فصل\s+",
            r"^\d+\.\s+\w",
            r"^part\s+\d+",
            r"^section\s+\d+",
        ]
        return any(re.match(p, text.lower().strip()) for p in patterns)
    
    def _structure_chapters(self, parsed: dict) -> list:
        """Convert parsed content into chapter structure."""
        chapters = []
        current_chapter = None
        current_section = None
        block_order = 0
        
        # Process headings and paragraphs
        content_items = []
        
        # Interleave headings and paragraphs based on original order
        for h in parsed.get("headings", []):
            content_items.append(("heading", h))
        
        for p in parsed.get("paragraphs", []):
            content_items.append(("paragraph", p))
        
        # If no headings, create single chapter
        if not parsed.get("headings"):
            chapter = {
                "id": "ch-1",
                "number": 1,
                "title": "Main Content",
                "sections": [],
                "word_count": len(parsed.get("full_text", "").split()),
                "is_sample_eligible": False,
                "order": 1
            }
            
            # Add all paragraphs as content blocks
            section = {
                "id": "sec-1-1",
                "title": None,
                "level": 2,
                "content_blocks": [],
                "order": 1
            }
            
            for i, para in enumerate(parsed.get("paragraphs", [])):
                section["content_blocks"].append({
                    "id": f"blk-1-1-{i+1}",
                    "type": "paragraph",
                    "content": para,
                    "order": i + 1
                })
            
            chapter["sections"] = [section]
            return [chapter]
        
        # Process with headings
        chapter_num = 0
        section_num = 0
        para_idx = 0
        paragraphs = parsed.get("paragraphs", [])
        
        for heading in parsed.get("headings", []):
            if heading["level"] == 1:
                # New chapter
                chapter_num += 1
                section_num = 0
                
                current_chapter = {
                    "id": f"ch-{chapter_num}",
                    "number": chapter_num,
                    "title": heading["text"],
                    "sections": [],
                    "word_count": 0,
                    "is_sample_eligible": False,
                    "order": chapter_num
                }
                chapters.append(current_chapter)
                current_section = None
            else:
                # New section within chapter
                if not current_chapter:
                    # Create default chapter if section comes first
                    chapter_num += 1
                    current_chapter = {
                        "id": f"ch-{chapter_num}",
                        "number": chapter_num,
                        "title": "Introduction",
                        "sections": [],
                        "word_count": 0,
                        "is_sample_eligible": False,
                        "order": chapter_num
                    }
                    chapters.append(current_chapter)
                
                section_num += 1
                current_section = {
                    "id": f"sec-{chapter_num}-{section_num}",
                    "title": heading["text"],
                    "level": heading["level"],
                    "content_blocks": [],
                    "order": section_num
                }
                current_chapter["sections"].append(current_section)
        
        # Distribute paragraphs to chapters (simplified - in real impl, would track order)
        if chapters and paragraphs:
            paras_per_chapter = max(1, len(paragraphs) // len(chapters))
            
            for i, chapter in enumerate(chapters):
                start = i * paras_per_chapter
                end = start + paras_per_chapter if i < len(chapters) - 1 else len(paragraphs)
                chapter_paras = paragraphs[start:end]
                
                # If no sections, create default
                if not chapter["sections"]:
                    chapter["sections"] = [{
                        "id": f"sec-{chapter['number']}-1",
                        "title": None,
                        "level": 2,
                        "content_blocks": [],
                        "order": 1
                    }]
                
                # Add paragraphs to first section
                section = chapter["sections"][0]
                for j, para in enumerate(chapter_paras):
                    section["content_blocks"].append({
                        "id": f"blk-{chapter['number']}-1-{j+1}",
                        "type": "paragraph",
                        "content": para,
                        "order": j + 1
                    })
                    chapter["word_count"] += len(para.split())
        
        return chapters


if __name__ == "__main__":
    # Test with sample
    print("ManuscriptCompilerTool ready")
