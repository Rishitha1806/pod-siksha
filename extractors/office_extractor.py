"""
DOCX & PPTX Extractors for Universal AI Educator.
Supports Microsoft Word (.docx) and PowerPoint (.pptx) using standard library zipfile.
"""

import io
import re
import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import List
from extractors.base import BaseExtractor, ExtractedSection, ExtractionResult

log = logging.getLogger("pod_siksha.extractors.office")

class DocxExtractor(BaseExtractor):
    def get_extractor_name(self) -> str:
        return "docx_extractor"

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx_zip:
                xml_content = docx_zip.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paragraphs = []
                for p in tree.iterfind(".//w:p", namespaces):
                    texts = [node.text for node in p.iterfind(".//w:t", namespaces) if node.text]
                    if texts:
                        paragraphs.append("".join(texts))
        except Exception as e:
            raise ValueError(f"Invalid DOCX document: {e}")

        sections = []
        for idx, para in enumerate(paragraphs, start=1):
            sections.append(ExtractedSection(
                page_number=1,
                section_index=idx,
                section_title=para[:60],
                content_type="text",
                content=para
            ))

        full_text = "\n\n".join(paragraphs)
        return ExtractionResult(
            total_pages=1,
            sections=sections,
            subject_detected="General Education",
            full_text=full_text,
            extractor_used="docx_extractor"
        )


class PptxExtractor(BaseExtractor):
    def get_extractor_name(self) -> str:
        return "pptx_extractor"

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        try:
            slides_text = []
            sections = []
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as pptx_zip:
                slide_names = [f for f in pptx_zip.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
                slide_names.sort(key=lambda x: int("".join(filter(str.isdigit, x)) or 0))
                namespaces = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

                for idx, slide_name in enumerate(slide_names, 1):
                    xml_content = pptx_zip.read(slide_name)
                    tree = ET.fromstring(xml_content)
                    slide_lines = []
                    for p in tree.iterfind(".//a:p", namespaces):
                        texts = [t.text for t in p.iterfind(".//a:t", namespaces) if t.text]
                        if texts:
                            slide_lines.append("".join(texts))

                    slide_content = "\n".join(slide_lines)
                    if slide_content:
                        slides_text.append(f"[Slide {idx}]\n{slide_content}")
                        sections.append(ExtractedSection(
                            page_number=idx,
                            section_index=idx,
                            section_title=f"Slide {idx}: {slide_lines[0][:50] if slide_lines else ''}",
                            content_type="text",
                            content=slide_content
                        ))
        except Exception as e:
            raise ValueError(f"Invalid PPTX presentation: {e}")

        full_text = "\n\n".join(slides_text)
        return ExtractionResult(
            total_pages=len(slide_names),
            sections=sections,
            subject_detected="Presentation / Lecture Slides",
            full_text=full_text,
            extractor_used="pptx_extractor"
        )
