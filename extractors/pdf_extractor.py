"""
Text-based PDF Extractor with Structural Analysis for Universal AI Educator.
Preserves page numbers, identifies headings, extracts code blocks (Python, Java, C++, SQL),
detects mathematical formulas, tables, and subject classifications.
"""

import io
import re
import logging
from typing import List, Tuple, Set
from pypdf import PdfReader
from extractors.base import BaseExtractor, ExtractedSection, ExtractionResult

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
    re.compile(r"(\\[a-zA-Z]+|\b(sum|int|lim|frac|sqrt|partial)\b|[∑∫∂√∞πθλσ])"),
    re.compile(r"([a-zA-Z0-9]\s*=\s*[-+]?[a-zA-Z0-9\(\)\/\*\^]+(?:\s*[-+*\/]\s*[a-zA-Z0-9\(\)\/\*\^]+)+)"),
    re.compile(r"\b(Theorem|Lemma|Corollary|Proof|Q\.E\.D\.|dx\/dt|dy\/dx)\b", re.IGNORECASE),
]

# Subject classification keywords
SUBJECT_KEYWORDS = {
    "Computer Science": ["algorithm", "data structure", "recursion", "binary tree", "graph", "hash map", "time complexity", "pointer", "array", "linked list", "sorting", "dynamic programming", "sql", "database"],
    "Mathematics": ["derivative", "integral", "matrix", "eigenvalue", "vector space", "probability", "theorem", "equation", "calculus", "linear algebra", "polynomial", "geometry", "trigonometry"],
    "Physics": ["mechanics", "thermodynamics", "quantum", "gravity", "velocity", "acceleration", "force", "electromagnetism", "kinetic", "energy", "newton", "optics"],
    "Chemistry": ["molecule", "atom", "reaction", "bond", "acid", "base", "solution", "organic chemistry", "equilibrium", "periodic table", "electron"],
    "Biology": ["cell", "dna", "rna", "protein", "photosynthesis", "genetics", "organism", "mitochondria", "enzyme", "ecosystem"],
    "Economics & Finance": ["gdp", "inflation", "market", "demand", "supply", "microeconomics", "macroeconomics", "interest rate", "revenue", "fiscal"],
    "Humanities & History": ["civilization", "empire", "revolution", "constitution", "governance", "treaty", "historical", "archaeology", "philosophy"],
}

class TextPdfExtractor(BaseExtractor):
    def get_extractor_name(self) -> str:
        return "text_pdf_extractor"

    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Invalid PDF file or corrupt structure: {e}")

        total_pages = len(reader.pages)
        sections: List[ExtractedSection] = []
        detected_languages: Set[str] = set()
        has_math = False
        has_code = False
        has_tables = False
        all_text_parts: List[str] = []

        subject_scores = {k: 0 for k in SUBJECT_KEYWORDS}

        for page_idx, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as e:
                log.warning("Could not extract text from page %d of %s: %s", page_idx, filename, e)
                page_text = ""

            clean_text = page_text.strip()
            if not clean_text:
                continue

            all_text_parts.append(f"[Page {page_idx}]\n{clean_text}")

            # Check for subject keywords
            lower_text = clean_text.lower()
            for subject, keywords in SUBJECT_KEYWORDS.items():
                for kw in keywords:
                    if kw in lower_text:
                        subject_scores[subject] += 1

            # Identify content type and sections on this page
            # Split page into logical paragraphs
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean_text) if p.strip()]

            for sec_idx, para in enumerate(paragraphs, start=1):
                content_type = "text"
                para_meta = {"page": page_idx}

                # Check code
                for lang, pat in CODE_PATTERNS.items():
                    if pat.search(para):
                        content_type = "code"
                        has_code = True
                        detected_languages.add(lang)
                        para_meta["code_language"] = lang
                        break

                # Check math
                if content_type == "text":
                    for m_pat in MATH_PATTERNS:
                        if m_pat.search(para):
                            has_math = True
                            if "\\[" in para or "\\begin" in para or "∑" in para or "∫" in para:
                                content_type = "math"
                            para_meta["has_math_notation"] = True
                            break

                # Check table structure (lines with multiple delimiters or tab alignments)
                lines = para.splitlines()
                if len(lines) >= 3 and any(("|" in l or "\t" in l or "   " in l) for l in lines):
                    if lines[0].count("|") >= 2 or lines[0].count("\t") >= 2:
                        content_type = "table"
                        has_tables = True

                # Determine section title (first line if short, or generic)
                first_line = lines[0] if lines else f"Page {page_idx} Section {sec_idx}"
                section_title = first_line[:80].strip("# ").strip() if len(first_line) < 100 else f"Page {page_idx} Section {sec_idx}"

                sections.append(ExtractedSection(
                    page_number=page_idx,
                    section_index=sec_idx,
                    section_title=section_title,
                    content_type=content_type,
                    content=para,
                    metadata=para_meta
                ))

        # Best detected subject
        top_subject = "General Education"
        max_score = 0
        for subj, score in subject_scores.items():
            if score > max_score and score >= 2:
                max_score = score
                top_subject = subj

        full_text = "\n\n".join(all_text_parts)

        return ExtractionResult(
            total_pages=total_pages,
            sections=sections,
            subject_detected=top_subject,
            language_detected="en",
            code_languages=sorted(list(detected_languages)),
            has_math=has_math,
            has_code=has_code,
            has_tables=has_tables,
            full_text=full_text,
            extractor_used="text_pdf_extractor"
        )
