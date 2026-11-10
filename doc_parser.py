"""
Multi-format Document Extractor for Pod-Siksha 2.0.
Supports PDF, DOCX, PPTX, and TXT with zero external C-dependencies.
"""

import io
import logging
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

log = logging.getLogger("pod_siksha.doc_parser")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text content across all pages of a PDF."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text()
            if txt and txt.strip():
                pages_text.append(f"[Page {i+1}]\n{txt.strip()}")
        return "\n\n".join(pages_text)
    except Exception as e:
        log.error("PDF parsing error: %s", e)
        return ""

def extract_text_from_docx(docx_bytes: bytes) -> str:
    """Extracts paragraphs and headings from a .docx file via standard library zipfile."""
    try:
        with zipfile.ZipFile(io.BytesIO(docx_bytes)) as docx_zip:
            xml_content = docx_zip.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            # Find all paragraph text elements (w:t)
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for p in tree.iterfind('.//w:p', namespaces):
                texts = [node.text for node in p.iterfind('.//w:t', namespaces) if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
            return '\n\n'.join(paragraphs)
    except Exception as e:
        log.error("DOCX parsing error: %s", e)
        return ""

def extract_text_from_pptx(pptx_bytes: bytes) -> str:
    """Extracts slide notes and shapes from a .pptx file via standard library zipfile."""
    try:
        slides_text = []
        with zipfile.ZipFile(io.BytesIO(pptx_bytes)) as pptx_zip:
            slide_names = [f for f in pptx_zip.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            # Sort slide filenames numerically
            slide_names.sort(key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
            namespaces = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
            for idx, slide_name in enumerate(slide_names, 1):
                xml_content = pptx_zip.read(slide_name)
                tree = ET.fromstring(xml_content)
                slide_lines = []
                for p in tree.iterfind('.//a:p', namespaces):
                    texts = [t.text for t in p.iterfind('.//a:t', namespaces) if t.text]
                    if texts:
                        slide_lines.append(''.join(texts))
                if slide_lines:
                    slides_text.append(f"[Slide {idx}]\n" + '\n'.join(slide_lines))
        return '\n\n'.join(slides_text)
    except Exception as e:
        log.error("PPTX parsing error: %s", e)
        return ""

def extract_document_content(filename: str, file_bytes: bytes) -> str:
    """Detects file format by extension and extracts readable text."""
    lower_fn = filename.lower()
    if lower_fn.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif lower_fn.endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    elif lower_fn.endswith('.pptx') or lower_fn.endswith('.ppt'):
        return extract_text_from_pptx(file_bytes)
    elif lower_fn.endswith('.txt') or lower_fn.endswith('.md'):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return file_bytes.decode('latin-1', errors='ignore')
    else:
        # Fallback attempt text decoding
        try:
            return file_bytes.decode('utf-8')
        except Exception:
            return ""
