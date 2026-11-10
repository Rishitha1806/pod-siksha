"""
Mathematical Intelligence Extractor for Universal AI Educator.
Detects, normalizes, and extracts mathematical expressions:
- Equations, fractions, summations, integrals, limits, and matrices
- Prepares expressions in standardized LaTeX syntax for frontend KaTeX rendering
- Preserves variables dictionary, derivation context, and sequence steps.
"""

import os
import re
import json
import uuid
import logging
from typing import List, Dict, Any, Optional

from extractors.base import ExtractedSection
from db_adapter import get_db

log = logging.getLogger("pod_siksha.math_extractor")

MATH_PATTERNS = [
    # LaTeX display blocks $$ ... $$ or \[ ... \]
    (r"\$\$(.*?)\$\$", "display_equation"),
    (r"\\\[(.*?)\\\]", "display_equation"),
    # Inline LaTeX $ ... $ or \( ... \)
    (r"\$([^\$\n]+)\$", "inline_math"),
    (r"\\\((.*?)\\\)", "inline_math"),
    # Common Unicode math / ASCII equations: e.g. E = mc^2, f(x) = \int, \sum_{i=1}^n
    (r"(?:[a-zA-Z]\([a-zA-Z0-9,\s]+\)|[a-zA-Z_0-9]+)\s*=\s*[^;\n]{3,60}", "equation"),
    (r"\\int(?:_\{?[^}]*\}?)?(?:\^\{?[^}]*\}?)?.*?[a-zA-Z]d[a-zA-Z]", "integral"),
    (r"\\sum(?:_\{?[^}]*\}?)?(?:\^\{?[^}]*\}?)?.*?", "summation"),
    (r"\\frac\{[^}]+\}\{[^}]+\}", "fraction"),
    (r"\\begin\{matrix\}.*?\\end\{matrix\}", "matrix")
]

class MathematicalIntelligenceExtractor:
    """Specialized mathematical expression parser and LaTeX normalizer."""

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
            except Exception:
                pass

    def normalize_to_latex(self, raw_expr: str, expr_type: str) -> str:
        """Converts raw equation text into clean, valid LaTeX representation."""
        cleaned = raw_expr.strip()
        # If already wrapped in $, unwrap
        if cleaned.startswith("$$") and cleaned.endswith("$$"):
            cleaned = cleaned[2:-2].strip()
        elif cleaned.startswith("$") and cleaned.endswith("$"):
            cleaned = cleaned[1:-1].strip()

        # Common ASCII replacements to LaTeX
        cleaned = re.sub(r"\bint\b", r"\\int", cleaned)
        cleaned = re.sub(r"\bsum\b", r"\\sum", cleaned)
        cleaned = re.sub(r"\bsqrt\(([^)]+)\)", r"\\sqrt{\1}", cleaned)
        cleaned = re.sub(r"\b([a-zA-Z0-9_]+)\s*\/\s*([a-zA-Z0-9_]+)\b", r"\\frac{\1}{\2}", cleaned)
        cleaned = re.sub(r"\btheta\b", r"\\theta", cleaned)
        cleaned = re.sub(r"\balpha\b", r"\\alpha", cleaned)
        cleaned = re.sub(r"\bbeta\b", r"\\beta", cleaned)
        cleaned = re.sub(r"\bpi\b", r"\\pi", cleaned)
        cleaned = re.sub(r"\bnabla\b", r"\\nabla", cleaned)
        cleaned = re.sub(r"\bpartial\b", r"\\partial", cleaned)

        return f"$${cleaned}$$"

    def extract_heuristically(self, page_text: str, page_number: int) -> List[Dict[str, Any]]:
        """Extracts candidate mathematical expressions from page text."""
        results = []
        seen = set()

        for pattern, m_type in MATH_PATTERNS:
            for match in re.finditer(pattern, page_text):
                raw = match.group(0).strip()
                if len(raw) < 3 or raw in seen:
                    continue
                seen.add(raw)

                # Classify expression subtype
                sub_type = "equation"
                if "\\frac" in raw or "/" in raw:
                    sub_type = "fraction"
                elif "\\int" in raw or "integral" in raw.lower():
                    sub_type = "integral"
                elif "\\sum" in raw:
                    sub_type = "summation"
                elif "matrix" in raw:
                    sub_type = "matrix"
                elif "->" in raw or "\\Rightarrow" in raw:
                    sub_type = "derivation"

                latex = self.normalize_to_latex(raw, sub_type)

                # Context around expression (50 chars before and after)
                start = max(0, match.start() - 60)
                end = min(len(page_text), match.end() + 60)
                ctx = page_text[start:end].replace("\n", " ").strip()

                results.append({
                    "page_number": page_number,
                    "latex_expr": latex,
                    "expression_type": sub_type,
                    "context_text": ctx,
                    "variables": {},
                    "derivation_step": len(results) + 1
                })

        return results

    def enhance_with_gemini(self, math_items: List[Dict[str, Any]], page_context: str) -> List[Dict[str, Any]]:
        """Extracts variable mappings and verifies LaTeX validity via Gemini."""
        if not self.client or not math_items:
            return math_items

        items_sample = [
            {"index": i, "latex": item["latex_expr"], "type": item["expression_type"]}
            for i, item in enumerate(math_items[:6])
        ]

        prompt = f"""You are a mathematics professor.
Analyze these mathematical formulas extracted from an educational textbook:
{json.dumps(items_sample)}

Context: "{page_context[:800]}"

For each formula:
1. Provide accurate LaTeX syntax (KaTeX-compatible)
2. Identify expression_type: "equation" | "integral" | "derivation" | "matrix" | "fraction" | "summation"
3. Identify variables dictionary: e.g. {{"E": "Energy in Joules", "m": "Mass in kg", "c": "Speed of light in m/s"}}

Respond strictly with valid JSON matching:
{{
  "analyzed_math": [
    {{
      "index": 0,
      "latex": "$$E = mc^2$$",
      "expression_type": "equation",
      "variables": {{"E": "Energy", "m": "Mass", "c": "Speed of light"}}
    }}
  ]
}}
"""
        try:
            res = self.client.models.generate_content(
                model=os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"),
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            raw = re.sub(r"^```(?:json)?\s*", "", res.text.strip(), flags=re.MULTILINE)
            raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
            parsed = json.loads(raw).get("analyzed_math", [])
            for p in parsed:
                idx = p.get("index")
                if idx is not None and 0 <= idx < len(math_items):
                    if p.get("latex"):
                        math_items[idx]["latex_expr"] = p["latex"]
                    if p.get("expression_type"):
                        math_items[idx]["expression_type"] = p["expression_type"]
                    if p.get("variables"):
                        math_items[idx]["variables"] = p["variables"]
        except Exception as e:
            log.warning("Gemini math enhancement note: %s", e)

        return math_items

    def process_document(self, sections: List[ExtractedSection], document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Processes and stores mathematical formulas across document."""
        extracted_all = []
        for sec in sections:
            items = self.extract_heuristically(sec.content, sec.page_number)
            if items:
                enhanced = self.enhance_with_gemini(items, sec.content)
                for item in enhanced:
                    expr_id = str(uuid.uuid4())
                    item["id"] = expr_id
                    extracted_all.append(item)

                    # Persist in document_math_expressions
                    if document_id:
                        try:
                            with get_db() as conn:
                                conn.execute("""
                                    INSERT INTO document_math_expressions (
                                        id, document_id, page_number, latex_expr,
                                        expression_type, context_text, variables_json,
                                        derivation_step
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    expr_id, document_id, item["page_number"],
                                    item["latex_expr"], item["expression_type"],
                                    item.get("context_text", ""),
                                    json.dumps(item.get("variables", {})),
                                    item.get("derivation_step", 1)
                                ))
                                conn.commit()
                        except Exception as db_err:
                            log.warning("Could not persist math expr for doc %s: %s", document_id, db_err)

        return extracted_all
