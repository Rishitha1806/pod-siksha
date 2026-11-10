"""
Universal PDF Extractor with Structural Analysis & Automatic OCR for Universal AI Educator.
Preserves page numbers, identifies headings/subheadings, extracts code blocks (Python, Java, C, C++, JS, SQL),
preserves mathematical expressions in LaTeX format, parses markdown tables, and automatically triggers
Gemini Multimodal OCR on scanned/image-only pages (< 50 characters).
"""

import io
import re
import logging
from typing import List, Tuple, Set, Optional, Dict, Any
from extractors.base import BaseExtractor, ExtractedSection, ExtractionResult
from extractors.ocr_extractor import OcrPdfExtractor

log = logging.getLogger("pod_siksha.extractors.pdf")

# Regex patterns for code detection
CODE_PATTERNS = {
    "python": re.compile(r"(def\s+[a-zA-Z_]\w*\s*\(|import\s+[a-zA-Z_]|from\s+[a-zA-Z_]+\s+import|class\s+[a-zA-Z_]\w*\s*[:\(]|print\s*\(|elif\s+|if\s+__name__\s*==)"),
    "java": re.compile(r"(public\s+class|public\s+static\s+void\s+main|System\.out\.print|new\s+[A-Z]\w*\(|import\s+java\.)"),
    "cpp": re.compile(r"(#include\s*<[a-z]+>|std::cout|std::vector|int\s+main\s*\(|cout\s*<<|namespace\s+std)"),
    "c": re.compile(r"(#include\s*<stdio\.h>|printf\s*\(|scanf\s*\(|malloc\s*\(|struct\s+[a-zA-Z_]\w*\s*\{)"),
    "sql": re.compile(r"\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+.+\s+SET|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE|GROUP\s+BY|ORDER\s+BY)\b", re.IGNORECASE),
    "javascript": re.compile(r"(function\s+[a-zA-Z_]|const\s+[a-zA-Z_]\w*\s*=|let\s+[a-zA-Z_]\w*\s*=|console\.log\s*\(|=>\s*\{)"),
}

# Regex patterns for math detection
MATH_PATTERNS = [
    re.compile(r"(\$\$[^\$]+\$\$|\$[^\$\n]+\$)"),  # LaTeX
    re.compile(r"([a-zA-Z]\([a-zA-Z0-9,\s]+\)\s*=\s*[^;\n]{3,60})"),  # f(x) = ...
    re.compile(r"(\b[a-zA-Z]\^\{?[0-9a-zA-Z\+\-\*\/]+\}?)"),  # Exponents x^2, e^{i\pi}
    re.compile(r"(\\int|\\sum|\\frac|\\sqrt|\\alpha|\\beta|\\gamma|\\theta|\\pi|\\infty)"),  # LaTeX symbols
    re.compile(r"([A-Z]\s*=\s*mc\^2|[a-z]\s*=\s*[-+]?\d+)"),  # Simple formulas
]

TABLE_ROW_PATTERN = re.compile(r"^\s*\|?.+\|.+\|?\s*$")
HEADING_PATTERN = re.compile(r"^(?:#{1,4}\s+|[0-9]{1,2}(?:\.[0-9]{1,2})*\s+[A-Z]|[A-Z\s]{4,60}$)")

class TextPdfExtractor(BaseExtractor):
    """Universal PDF Extractor supporting native text extraction and automated OCR."""

    def __init__(self):
        self.ocr_extractor = OcrPdfExtractor()

    def get_extractor_name(self) -> str:
        return "universal_pdf_extractor"

    def detect_subject(self, full_text: str) -> str:
        """Determines genuine educational subject using lexical taxonomy."""
        t = full_text.lower()
        if any(w in t for w in ["def ", "class ", "python", "numpy", "pandas", "algorithm", "variable"]):
            if "java" in t or "public class" in t:
                return "Java Object-Oriented Programming"
            if "vector" in t or "#include" in t or "cout" in t:
                return "C++ & Data Structures"
            return "Python Programming & Computing"
        if any(w in t for w in ["select ", "insert into", "database", "relational", "sql", "table"]):
            return "Databases & SQL"
        if any(w in t for w in ["integral", "derivative", "calculus", "matrix", "eigenvalue", "polynomial", "theorem", "equation"]):
            return "Mathematics & Calculus"
        if any(w in t for w in ["cell", "mitochondria", "photosynthesis", "dna", "chloroplast", "protein", "organism"]):
            return "Biological Sciences"
        if any(w in t for w in ["reaction", "molecule", "acid", "base", "stoichiometry", "bond", "orbital"]):
            return "Chemical Sciences"
        if any(w in t for w in ["force", "velocity", "acceleration", "quantum", "gravity", "wave", "electromagnetic", "frequency"]):
            return "Physics & Mechanics"
        if any(w in t for w in ["revolution", "war", "century", "empire", "treaty", "dynasty", "civilization"]):
            return "History & World Studies"
        if any(w in t for w in ["climate", "river", "plateau", "atmosphere", "lithosphere", "monsoon", "topography"]):
            return "Earth Science & Geography"
        if any(w in t for w in ["abstract", "methodology", "citation", "participants", "doi", "results and discussion"]):
            return "Academic Research Paper"
        return "Universal Educational Studies"

    def is_code_line(self, line: str) -> Tuple[bool, Optional[str]]:
        for lang, pat in CODE_PATTERNS.items():
            if pat.search(line):
                return True, lang
        return False, None

    def is_math_line(self, line: str) -> bool:
        for pat in MATH_PATTERNS:
            if pat.search(line):
                return True
        return False

    def extract(self, file_bytes: bytes, filename: str, document_id: Optional[str] = None) -> ExtractionResult:
        sections: List[ExtractedSection] = []
        full_text_list: List[str] = []
        total_pages = 0
        detected_languages: Set[str] = set()

        # Try fitz (PyMuPDF) first for superior accuracy and OCR trigger
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)

            for p_idx in range(total_pages):
                page_num = p_idx + 1
                page = doc[p_idx]
                page_text = page.get_text() or ""

                # Check if page is image-only or scanned
                if self.ocr_extractor.is_scanned_page(page_text, page):
                    log.info("Page %d of %s is scanned; triggering OCR", page_num, filename)
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    ocr_res = self.ocr_extractor.ocr_page_image(img_bytes, page_num)
                    page_text = ocr_res.get("full_text", "")
                    sec_title = f"Page {page_num} (OCR Scanned)"
                    sections.append(ExtractedSection(
                        page_number=page_num,
                        section_index=len(sections) + 1,
                        section_title=sec_title,
                        content_type="text",
                        content=page_text,
                        metadata={"ocr": True, "confidence": ocr_res.get("confidence", 0.9)}
                    ))
                    full_text_list.append(page_text)
                    continue

                full_text_list.append(page_text)
                lines = page_text.splitlines()
                current_block_lines = []
                current_type = "text"
                current_title = f"Page {page_num} Overview"

                def flush_block():
                    nonlocal current_block_lines, current_type, current_title
                    if current_block_lines:
                        content = "\n".join(current_block_lines).strip()
                        if content:
                            sections.append(ExtractedSection(
                                page_number=page_num,
                                section_index=len(sections) + 1,
                                section_title=current_title,
                                content_type=current_type,
                                content=content,
                                metadata={"languages": list(detected_languages)} if current_type == "code" else {}
                            ))
                        current_block_lines = []
                        current_type = "text"

                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue

                    # Heading Check
                    if HEADING_PATTERN.match(stripped) and len(stripped) < 70:
                        flush_block()
                        current_title = stripped.lstrip("#").strip()
                        current_type = "heading"
                        current_block_lines.append(stripped)
                        flush_block()
                        current_title = f"Page {page_num} - {current_title}"
                        continue

                    # Code Check
                    is_code, lang = self.is_code_line(line)
                    if is_code:
                        if lang:
                            detected_languages.add(lang)
                        if current_type != "code":
                            flush_block()
                            current_type = "code"
                        current_block_lines.append(line)
                        continue

                    # Math Check
                    if self.is_math_line(line):
                        if current_type != "math" and current_type != "code":
                            flush_block()
                            current_type = "math"
                        current_block_lines.append(line)
                        continue

                    # Table Check
                    if TABLE_ROW_PATTERN.match(stripped):
                        if current_type != "table":
                            flush_block()
                            current_type = "table"
                        current_block_lines.append(line)
                        continue

                    # Regular Text
                    if current_type in ("code", "table") and (len(line) - len(line.lstrip())) == 0:
                        flush_block()
                    current_block_lines.append(line)

                flush_block()
            doc.close()

        except Exception as e:
            log.warning("fitz extraction failed, falling back to pypdf: %s", e)
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            for p_idx, page in enumerate(reader.pages):
                page_num = p_idx + 1
                txt = page.extract_text() or ""
                full_text_list.append(txt)
                sections.append(ExtractedSection(
                    page_number=page_num,
                    section_index=len(sections) + 1,
                    section_title=f"Page {page_num} Text",
                    content_type="text",
                    content=txt.strip()
                ))

        combined_text = "\n\n".join(full_text_list)
        subject = self.detect_subject(combined_text)

        return ExtractionResult(
            document_id=document_id or "",
            filename=filename,
            total_pages=total_pages,
            sections=sections,
            subject_detected=subject,
            full_text=combined_text,
            metadata={
                "detected_languages": list(detected_languages),
                "extractor": self.get_extractor_name()
            }
        )
