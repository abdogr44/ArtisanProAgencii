"""
Reader Bundle Schema

Defines the structure for reader_bundle.sample.json that is deployed
to Firebase Hosting for the Athar ReaderView app.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime


class TOCEntry(BaseModel):
    """Table of contents entry."""
    id: str = Field(..., description="Chapter/section ID")
    title: str = Field(..., description="Display title")
    title_ar: Optional[str] = Field(default=None, description="Arabic title")
    level: int = Field(default=1, description="Nesting level (1=chapter, 2=section)")
    page: Optional[int] = Field(default=None, description="Page number if applicable")
    is_sample: bool = Field(default=False, description="Whether this is in the sample")
    order: int = Field(..., description="Display order")


class ContentBlock(BaseModel):
    """Content block for reader display."""
    id: str = Field(..., description="Unique block ID")
    type: Literal["paragraph", "heading", "quote", "image", "list"] = Field(...)
    content: str = Field(..., description="Text or image URL")
    style: Optional[dict] = Field(default=None, description="Optional styling hints")


class SampleChapter(BaseModel):
    """Chapter content included in the sample bundle."""
    id: str = Field(..., description="Chapter ID")
    title: str = Field(..., description="Chapter title")
    title_ar: Optional[str] = Field(default=None)
    order: int = Field(...)
    content_blocks: List[ContentBlock] = Field(default_factory=list)


class BookMetadataPublic(BaseModel):
    """Public book metadata for reader display."""
    title: str = Field(...)
    title_ar: Optional[str] = Field(default=None)
    subtitle: Optional[str] = Field(default=None)
    subtitle_ar: Optional[str] = Field(default=None)
    author: str = Field(...)
    author_ar: Optional[str] = Field(default=None)
    cover_url: Optional[str] = Field(default=None, description="Public URL to cover image")
    description: Optional[str] = Field(default=None)
    description_ar: Optional[str] = Field(default=None)
    language: str = Field(default="ar")
    genre: Optional[str] = Field(default=None)
    publication_year: Optional[int] = Field(default=None)
    total_chapters: int = Field(default=0, description="Total chapters in full book")
    sample_chapters: int = Field(default=0, description="Chapters in this sample")


class PurchaseInfo(BaseModel):
    """Information for purchasing the full book."""
    available: bool = Field(default=True)
    price: Optional[str] = Field(default=None, description="Formatted price string")
    currency: Optional[str] = Field(default="USD")
    purchase_url: Optional[str] = Field(default=None)
    app_store_url: Optional[str] = Field(default=None)
    play_store_url: Optional[str] = Field(default=None)


class IntegrityInfo(BaseModel):
    """Bundle integrity verification data."""
    version: str = Field(..., description="Bundle version")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    checksum: str = Field(..., description="SHA-256 of content")
    manuscript_id: str = Field(..., description="Source manuscript ID")


class ReaderBundle(BaseModel):
    """
    Reader bundle for Firebase ReaderView.
    
    This is the PUBLIC sample bundle that gets deployed to Firebase Hosting.
    It contains only whitelisted chapters and never the full manuscript.
    """
    bundle_version: str = Field(default="1.0.0", description="Bundle schema version")
    bundle_type: Literal["sample", "preview"] = Field(default="sample")
    
    # Book information
    book_id: str = Field(..., description="Unique book identifier")
    metadata: BookMetadataPublic = Field(...)
    
    # Table of contents (full, with sample flags)
    toc: List[TOCEntry] = Field(default_factory=list)
    
    # Sample content (whitelisted chapters only)
    sample_content: List[SampleChapter] = Field(default_factory=list)
    allowed_sample_ids: List[str] = Field(default_factory=list, description="Chapter IDs in sample")
    
    # Call to action
    purchase_info: Optional[PurchaseInfo] = Field(default=None)
    
    # Integrity
    integrity: IntegrityInfo = Field(...)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bundle_version": "1.0.0",
                "bundle_type": "sample",
                "book_id": "athar-book-001",
                "metadata": {
                    "title": "The Journey",
                    "title_ar": "الرحلة",
                    "author": "Aya El Badry",
                    "author_ar": "آية البدري",
                    "total_chapters": 12,
                    "sample_chapters": 2
                },
                "toc": [
                    {"id": "ch-1", "title": "Beginning", "level": 1, "is_sample": True, "order": 1},
                    {"id": "ch-2", "title": "The Path", "level": 1, "is_sample": True, "order": 2},
                    {"id": "ch-3", "title": "Discovery", "level": 1, "is_sample": False, "order": 3}
                ],
                "allowed_sample_ids": ["ch-1", "ch-2"],
                "integrity": {
                    "version": "1.0.0",
                    "checksum": "sha256:abc123...",
                    "manuscript_id": "athar-book-001"
                }
            }
        }
    )
