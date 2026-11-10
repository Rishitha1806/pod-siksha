"""
Base Extractor Interfaces and Data Structures for Universal AI Educator.
Defines contracts for multi-subject document ingestion across all document types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ExtractedSection:
    page_number: int
    section_index: int
    section_title: str
    content_type: str  # 'text', 'code', 'math', 'table', 'heading'
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtractionResult:
    total_pages: int
    sections: List[ExtractedSection]
    subject_detected: str = "General Education"
    language_detected: str = "en"
    code_languages: List[str] = field(default_factory=list)
    has_math: bool = False
    has_code: bool = False
    has_tables: bool = False
    full_text: str = ""
    extractor_used: str = "base"
    document_id: Optional[str] = ""
    filename: Optional[str] = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "total_pages": self.total_pages,
            "section_count": len(self.sections),
            "subject_detected": self.subject_detected,
            "language_detected": self.language_detected,
            "code_languages": self.code_languages,
            "has_math": self.has_math,
            "has_code": self.has_code,
            "has_tables": self.has_tables,
            "full_text_chars": len(self.full_text),
            "extractor_used": self.extractor_used,
            "metadata": self.metadata
        }

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        """
        Parses document bytes into structured sections preserving page numbers,
        code snippets, mathematical expressions, and tables.
        """
        pass

    @abstractmethod
    def get_extractor_name(self) -> str:
        pass
