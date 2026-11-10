"""
Extractor Factory for Universal AI Educator.
Routes document files to the appropriate extractor based on MIME type and file extension.
"""

import os
from typing import Optional
from extractors.base import BaseExtractor, ExtractionResult
from extractors.pdf_extractor import TextPdfExtractor
from extractors.office_extractor import DocxExtractor, PptxExtractor
from extractors.ocr_extractor import OcrPdfExtractor
from extractors.multimodal_extractor import MultimodalDocumentExtractor

class PlainTextExtractor(BaseExtractor):
    def get_extractor_name(self) -> str:
        return "plain_text_extractor"

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="ignore")

        return ExtractionResult(
            total_pages=1,
            sections=[],
            subject_detected="General Notes",
            full_text=text,
            extractor_used="plain_text_extractor"
        )

def get_extractor(filename: str, content_type: Optional[str] = None) -> BaseExtractor:
    lower_fn = filename.lower()
    if lower_fn.endswith(".pdf"):
        return TextPdfExtractor()
    elif lower_fn.endswith(".docx"):
        return DocxExtractor()
    elif lower_fn.endswith(".pptx") or lower_fn.endswith(".ppt"):
        return PptxExtractor()
    elif lower_fn.endswith(".txt") or lower_fn.endswith(".md"):
        return PlainTextExtractor()
    else:
        # Default fallback
        return TextPdfExtractor() if (content_type and "pdf" in content_type) else PlainTextExtractor()
