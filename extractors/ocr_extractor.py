"""
OCR Extractor Interface (Phase 2 Component).
Stands ready for Tesseract / Google Cloud Vision integration in Phase 2.
Explicitly indicates unconfigured status rather than mock implementation.
"""

from extractors.base import BaseExtractor, ExtractionResult

class OcrPdfExtractor(BaseExtractor):
    def get_extractor_name(self) -> str:
        return "ocr_pdf_extractor"

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        raise NotImplementedError(
            "OCR extraction pipeline for scanned PDFs is scheduled for Phase 2 implementation. "
            "Text-based PDF extraction is currently active."
        )

    @classmethod
    def is_available(cls) -> bool:
        """Checks if OCR dependencies (e.g. tesseract/google-cloud-vision) are installed."""
        return False
