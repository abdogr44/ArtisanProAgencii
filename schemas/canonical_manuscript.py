"""
Canonical Manuscript Schema

Defines the structured representation of a book manuscript after parsing
from DOCX/PDF source files.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Types of content blocks within a manuscript."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    QUOTE = "quote"
    LIST = "list"
    IMAGE = "image"
    FOOTNOTE = "footnote"
    EPIGRAPH = "epigraph"


class ContentBlock(BaseModel):
    """Individual content element within a section."""
    id: str = Field(..., description="Unique identifier for this content block")
    type: ContentType = Field(..., description="Type of content")
    content: str = Field(..., description="Text content or image reference")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata (e.g., image alt text, list style)")
    order: int = Field(..., description="Order within parent section")


class Section(BaseModel):
    """A section within a chapter (e.g., subheading with content)."""
    id: str = Field(..., description="Unique section identifier")
    title: Optional[str] = Field(default=None, description="Section heading if any")
    level: int = Field(default=1, description="Heading level (1-6)")
    content_blocks: List[ContentBlock] = Field(default_factory=list)
    order: int = Field(..., description="Order within parent chapter")


class Chapter(BaseModel):
    """A chapter in the manuscript."""
    id: str = Field(..., description="Unique chapter identifier")
    number: Optional[int] = Field(default=None, description="Chapter number if numbered")
    title: str = Field(..., description="Chapter title")
    sections: List[Section] = Field(default_factory=list)
    word_count: int = Field(default=0, description="Total words in chapter")
    is_sample_eligible: bool = Field(default=False, description="Whether this chapter can be included in samples")
    order: int = Field(..., description="Order in manuscript")


class BookMetadata(BaseModel):
    """Metadata about the book."""
    title: str = Field(..., description="Book title")
    subtitle: Optional[str] = Field(default=None)
    author: str = Field(..., description="Author name")
    author_ar: Optional[str] = Field(default=None, description="Author name in Arabic")
    title_ar: Optional[str] = Field(default=None, description="Title in Arabic")
    subtitle_ar: Optional[str] = Field(default=None, description="Subtitle in Arabic")
    isbn: Optional[str] = Field(default=None)
    language: str = Field(default="ar", description="Primary language code")
    genre: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    cover_image: Optional[str] = Field(default=None, description="Path to cover image")
    publication_date: Optional[datetime] = Field(default=None)


class SampleWhitelist(BaseModel):
    """Configuration for which chapters are included in samples."""
    chapter_ids: List[str] = Field(default_factory=list, description="IDs of chapters allowed in sample")
    max_percentage: float = Field(default=20.0, description="Maximum percentage of book in sample")
    include_toc: bool = Field(default=True, description="Include full TOC in sample")


class CanonicalManuscript(BaseModel):
    """
    The canonical representation of a book manuscript.
    
    This is the single source of truth for book content after parsing
    from source files. All downstream tools work from this format.
    """
    version: str = Field(default="1.0.0", description="Schema version")
    manuscript_id: str = Field(..., description="Unique manuscript identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source_file: str = Field(..., description="Original source file path")
    source_format: Literal["docx", "pdf", "txt"] = Field(..., description="Source file format")
    
    metadata: BookMetadata = Field(..., description="Book metadata")
    chapters: List[Chapter] = Field(default_factory=list)
    
    # Statistics
    total_word_count: int = Field(default=0)
    total_chapters: int = Field(default=0)
    total_sections: int = Field(default=0)
    
    # Sample configuration
    sample_whitelist: SampleWhitelist = Field(default_factory=SampleWhitelist)
    
    # Parsing Trust
    parsing_confidence: Literal["high", "medium", "low"] = Field(default="high", description="Trust level of the parsed content")
    parsing_notes: Optional[str] = Field(default=None)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": "1.0.0",
                "manuscript_id": "athar-book-001",
                "source_file": "/manuscripts/my_book.docx",
                "source_format": "docx",
                "metadata": {
                    "title": "The Journey",
                    "title_ar": "الرحلة",
                    "author": "Aya El Badry",
                    "author_ar": "آية البدري",
                    "language": "ar"
                },
                "chapters": [],
                "sample_whitelist": {
                    "chapter_ids": ["ch-1", "ch-2"],
                    "max_percentage": 20.0
                },
                "parsing_confidence": "high"
            }
        }
    )
