"""
Multimodal Document Extractor Interface (Phase 2 Component).
Stands ready for Gemini Multimodal Vision / diagram understanding in Phase 2.
Explicitly indicates scheduled status rather than mock implementation.
"""

from extractors.base import BaseExtractor, ExtractionResult

class MultimodalDocumentExtractor(BaseExtractor):
    def get_extractor_name(self) -> str:
        return "multimodal_vision_extractor"

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        raise NotImplementedError(
            "Multimodal visual and diagram extraction is scheduled for Phase 2 implementation. "
            "Structural text and code extraction is currently active."
        )

    @classmethod
    def is_available(cls) -> bool:
        """Checks if vision model pipeline is configured."""
        return False
