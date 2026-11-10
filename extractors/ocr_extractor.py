"""
Real OCR Extractor for Universal AI Educator.
Utilizes PyMuPDF (fitz) to rasterize image-only and scanned pages to high-resolution PNG,
then invokes Google Gemini Multimodal Vision to accurately extract printed text, handwriting,
tables, and structure while preserving exact page numbers and layout integrity.
"""

import os
import io
import re
import json
import logging
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from PIL import Image

from extractors.base import BaseExtractor, ExtractionResult, ExtractedSection
from db_adapter import get_db

log = logging.getLogger("pod_siksha.ocr")

class OcrPdfExtractor(BaseExtractor):
    """Real OCR extractor for scanned and low-extractability document pages."""

    def __init__(self, gemini_client=None):
        self.client = gemini_client
        if not self.client:
            try:
                from google import genai
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    self.client = genai.Client(api_key=api_key)
            except Exception as e:
                log.warning("Could not auto-initialize Gemini client for OCR: %s", e)

    def get_extractor_name(self) -> str:
        return "gemini_multimodal_ocr"

    def is_scanned_page(self, page_text: str, page) -> bool:
        """Determines if a page is scanned or image-based (< 50 text characters with image elements)."""
        stripped = (page_text or "").strip()
        if len(stripped) < 50:
            images = page.get_images()
            drawings = page.get_drawings()
            if len(images) > 0 or len(drawings) > 0 or len(stripped) == 0:
                return True
        return False

    def ocr_page_image(self, img_bytes: bytes, page_number: int) -> Dict[str, Any]:
        """Sends page PNG bytes to Gemini Multimodal Vision for high-fidelity OCR."""
        if not self.client:
            log.warning("Gemini client unavailable for OCR; returning unextracted notice.")
            return {
                "text": "[Scanned page: OCR requires configured GEMINI_API_KEY]",
                "confidence": 0.0,
                "has_handwriting": False,
                "sections": []
            }

        from google.genai import types

        prompt = f"""You are an expert OCR engine for an AI Universal Educator.
Analyze this high-resolution image of document page {page_number}.
Transcribe all text accurately, preserving headings, paragraphs, lists, mathematical formulas, and tables.

CRITICAL INSTRUCTIONS:
1. Do NOT hallucinate or fabricate text not visible on the page.
2. If text is blurry or cut off, transcribe what is discernible and mark uncertain terms.
3. Detect if handwritten notes or handwriting is present.
4. If tables are present, transcribe them with markdown table formatting.
5. Provide a realistic confidence estimate between 0.0 and 1.0.

Respond strictly with valid JSON matching this schema:
{{
  "full_text": "Complete transcribed page text",
  "has_handwriting": false,
  "confidence": 0.95,
  "headings": ["Heading 1", "Heading 2"],
  "sections": [
    {{
      "title": "Section Title",
      "content_type": "text" | "heading" | "table" | "code" | "math",
      "content": "Transcribed section text"
    }}
  ]
}}
"""
        models_to_try = [os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"), "gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
        for model in models_to_try:
            try:
                part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
                res = self.client.models.generate_content(
                    model=model,
                    contents=[part, prompt],
                    config={"response_mime_type": "application/json"}
                )
                raw_json = res.text.strip()
                raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json, flags=re.MULTILINE)
                raw_json = re.sub(r"\s*```$", "", raw_json, flags=re.MULTILINE)
                return json.loads(raw_json)
            except Exception as e:
                log.warning("OCR attempt on model %s for page %d failed: %s", model, page_number, e)
                continue

        return {
            "full_text": "[OCR processing timed out for this page]",
            "has_handwriting": False,
            "confidence": 0.2,
            "sections": []
        }

    def extract(self, file_bytes: bytes, filename: str, document_id: Optional[str] = None) -> ExtractionResult:
        """Extracts text and structured content across scanned PDF pages."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        sections: List[ExtractedSection] = []
        full_text_parts = []
        ocr_performed_pages = []

        for p_idx in range(total_pages):
            page_num = p_idx + 1
            page = doc[p_idx]
            raw_text = page.get_text()

            # Check if page is image-only / scanned
            if self.is_scanned_page(raw_text, page):
                log.info("Page %d of %s detected as scanned/image-based; running real OCR", page_num, filename)
                # Rasterize page to 150 DPI PNG
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")

                ocr_data = self.ocr_page_image(img_bytes, page_num)
                page_text = ocr_data.get("full_text", "")
                confidence = float(ocr_data.get("confidence", 0.9))
                has_hw = bool(ocr_data.get("has_handwriting", False))
                ocr_performed_pages.append(page_num)

                # Persist OCR record in document_ocr_results if document_id is provided
                if document_id:
                    try:
                        import uuid
                        with get_db() as conn:
                            conn.execute("""
                                INSERT INTO document_ocr_results (
                                    id, document_id, page_number, ocr_text,
                                    confidence, provider, has_handwriting, processing_status
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                str(uuid.uuid4()), document_id, page_num, page_text,
                                confidence, "gemini_multimodal", has_hw, "completed"
                            ))
                            conn.commit()
                    except Exception as db_err:
                        log.warning("Could not persist OCR record for doc %s page %d: %s", document_id, page_num, db_err)

                parsed_sections = ocr_data.get("sections", [])
                if parsed_sections:
                    for s_idx, sec in enumerate(parsed_sections):
                        sections.append(ExtractedSection(
                            page_number=page_num,
                            section_index=len(sections) + 1,
                            section_title=sec.get("title", f"Page {page_num} Section {s_idx + 1}"),
                            content_type=sec.get("content_type", "text"),
                            content=sec.get("content", ""),
                            metadata={
                                "ocr": True,
                                "confidence": confidence,
                                "has_handwriting": has_hw,
                                "provider": "gemini_multimodal"
                            }
                        ))
                else:
                    sections.append(ExtractedSection(
                        page_number=page_num,
                        section_index=len(sections) + 1,
                        section_title=f"Page {page_num} OCR Content",
                        content_type="text",
                        content=page_text,
                        metadata={
                            "ocr": True,
                            "confidence": confidence,
                            "has_handwriting": has_hw,
                            "provider": "gemini_multimodal"
                        }
                    ))
                full_text_parts.append(page_text)
            else:
                # Text is already extractable natively
                full_text_parts.append(raw_text)
                sections.append(ExtractedSection(
                    page_number=page_num,
                    section_index=len(sections) + 1,
                    section_title=f"Page {page_num} Native Content",
                    content_type="text",
                    content=raw_text.strip(),
                    metadata={"ocr": False, "confidence": 1.0}
                ))

        doc.close()
        return ExtractionResult(
            document_id=document_id or "",
            filename=filename,
            total_pages=total_pages,
            sections=sections,
            full_text="\n\n".join(full_text_parts),
            metadata={
                "ocr_performed": len(ocr_performed_pages) > 0,
                "ocr_pages_count": len(ocr_performed_pages),
                "ocr_pages": ocr_performed_pages,
                "extractor": self.get_extractor_name()
            }
        )
