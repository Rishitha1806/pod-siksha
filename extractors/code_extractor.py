"""
Programming Document Intelligence Extractor for Universal AI Educator.
Accurately detects and extracts programming code blocks across Python, Java, C, C++, JavaScript, SQL,
and other languages, preserving exact indentation, comments, algorithms, sample I/O, and purpose.
"""

import os
import re
import json
import uuid
import logging
from typing import List, Dict, Any, Optional

from extractors.base import BaseExtractor, ExtractionResult, ExtractedSection
from db_adapter import get_db

log = logging.getLogger("pod_siksha.code_extractor")

LANGUAGE_SIGNATURES = {
    "python": [r"def\s+\w+\s*\(", r"class\s+\w+.*:", r"import\s+\w+", r"from\s+\w+\s+import", r"elif\s+", r"if\s+__name__\s*=="],
    "java": [r"public\s+class\s+\w+", r"public\s+static\s+void\s+main", r"System\.out\.println", r"import\s+java\.", r"@Override", r"private\s+\w+\s+\w+;"],
    "cpp": [r"#include\s*<iostream>", r"#include\s*<\w+>", r"std::cout", r"std::vector", r"using\s+namespace\s+std;", r"int\s+main\s*\(\)"],
    "c": [r"#include\s*<stdio\.h>", r"#include\s*<stdlib\.h>", r"printf\s*\(", r"scanf\s*\(", r"malloc\s*\(", r"int\s+main\s*\("],
    "javascript": [r"const\s+\w+\s*=", r"let\s+\w+\s*=", r"function\s+\w+\s*\(", r"=>\s*{", r"console\.log\(", r"document\.getElementById"],
    "sql": [r"SELECT\s+.*\s+FROM\s+", r"CREATE\s+TABLE\s+", r"INSERT\s+INTO\s+", r"WHERE\s+\w+\s*=", r"GROUP\s+BY\s+", r"JOIN\s+\w+\s+ON\s+"]
}

class ProgrammingCodeExtractor:
    """Specialized code extraction engine with language detection and semantic parsing."""

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

    def detect_language(self, code_snippet: str) -> str:
        """Determines programming language from syntax signatures."""
        scores = {lang: 0 for lang in LANGUAGE_SIGNATURES}
        for lang, patterns in LANGUAGE_SIGNATURES.items():
            for pat in patterns:
                if re.search(pat, code_snippet):
                    scores[lang] += 2

        best_lang = max(scores, key=scores.get)
        return best_lang if scores[best_lang] > 0 else "generic"

    def extract_heuristically(self, page_text: str, page_number: int) -> List[Dict[str, Any]]:
        """Extracts fenced blocks (```lang ... ```) or algorithmic/code structures."""
        code_blocks = []
        # Fenced markdown blocks
        fenced_pattern = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)\n```", re.DOTALL)
        for m in fenced_pattern.finditer(page_text):
            lang_hint = m.group(1).lower().strip()
            raw_code = m.group(2)
            detected = lang_hint or self.detect_language(raw_code)
            code_blocks.append({
                "page_number": page_number,
                "language": detected,
                "code_text": raw_code,
                "purpose": f"Programmatic implementation in {detected.capitalize()}",
                "algorithm_name": None,
                "sample_inputs": [],
                "sample_outputs": [],
                "related_concepts": []
            })

        # Heuristic detection for unfenced code blocks
        if not code_blocks:
            lines = page_text.splitlines()
            code_trigger = re.compile(
                r"^(?:"
                r"package\s+[a-z0-9_.]+|"
                r"import\s+[a-z0-9_.*]+|"
                r"from\s+[a-z0-9_.]+\s+import|"
                r"(?:public|private|protected)?\s*(?:abstract\s+)?class\s+\w+|"
                r"(?:public|private|protected)?\s*(?:static\s+)?(?:void|int|double|String|boolean|float)\s+\w+\s*\(|"
                r"def\s+\w+\s*\(|"
                r"#include\s*<[a-z0-9_.]+>|"
                r"using\s+namespace\s+\w+|"
                r"int\s+main\s*\(|"
                r"SELECT\s+.*?\s+FROM|"
                r"CREATE\s+TABLE|"
                r"INSERT\s+INTO|"
                r"@Override|"
                r"if\s+__name__\s*=="
                r")"
            )

            buffer = []
            for l in lines:
                stripped = l.strip()
                if not stripped:
                    if buffer:
                        buffer.append(l)
                    continue

                is_code_start = bool(code_trigger.search(stripped))
                is_indented = bool(re.match(r"^( {4,}|\t+)", l) and len(stripped) > 2)
                is_syntax = bool(buffer and (
                    re.search(r"[{}();=><:\"']", l) or
                    stripped.startswith("//") or
                    stripped.startswith("#") or
                    stripped in ("}", "};", "});") or
                    re.match(r"^(return|elif|else|for|while|try|except|catch|finally)\b", stripped)
                ))

                if is_code_start or is_indented or is_syntax:
                    buffer.append(l)
                else:
                    if len([x for x in buffer if x.strip()]) >= 3:
                        joined = "\n".join(buffer).strip()
                        lang = self.detect_language(joined)
                        if lang != "generic" or "def " in joined or "class " in joined:
                            code_blocks.append({
                                "page_number": page_number,
                                "language": lang,
                                "code_text": joined,
                                "purpose": f"Algorithmic logic block in {lang.capitalize()}",
                                "algorithm_name": None,
                                "sample_inputs": [],
                                "sample_outputs": [],
                                "related_concepts": []
                            })
                    buffer = []

            if len([x for x in buffer if x.strip()]) >= 3:
                joined = "\n".join(buffer).strip()
                lang = self.detect_language(joined)
                if lang != "generic" or "def " in joined or "class " in joined:
                    code_blocks.append({
                        "page_number": page_number,
                        "language": lang,
                        "code_text": joined,
                        "purpose": f"Algorithmic logic block in {lang.capitalize()}",
                        "algorithm_name": None,
                        "sample_inputs": [],
                        "sample_outputs": [],
                        "related_concepts": []
                    })

        return code_blocks

    def enhance_with_gemini(self, code_blocks: List[Dict[str, Any]], page_context: str) -> List[Dict[str, Any]]:
        """Enriches raw code blocks with algorithm name, purpose, and sample I/O using Gemini."""
        if not self.client or not code_blocks:
            return code_blocks

        snippets_json = json.dumps([
            {"index": i, "language": b["language"], "code": b["code_text"][:600]}
            for i, b in enumerate(code_blocks)
        ])

        prompt = f"""You are a senior computer science educator.
Analyze these programming code blocks extracted from an educational document:
{snippets_json}

Context: "{page_context[:800]}"

For each snippet, identify:
1. Exact language (python, java, cpp, c, javascript, sql, etc.)
2. algorithm_name (e.g. "Binary Search", "Quicksort", "JDBC Connection", "Dijkstra")
3. purpose (What does this code do?)
4. sample_inputs (Expected inputs)
5. sample_outputs (Result produced)
6. related_concepts (e.g. ["Recursion", "Big-O Time Complexity", "Divide and Conquer"])

Respond strictly with valid JSON matching:
{{
  "analyzed_snippets": [
    {{
      "index": 0,
      "language": "python",
      "algorithm_name": "Binary Search",
      "purpose": "Searches for target in sorted list in O(log n) time",
      "sample_inputs": ["[1, 3, 5, 7, 9], target=5"],
      "sample_outputs": ["Index 2"],
      "related_concepts": ["Pointers", "Divide and Conquer", "O(log n)"]
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
            parsed = json.loads(raw).get("analyzed_snippets", [])
            for p in parsed:
                idx = p.get("index")
                if idx is not None and 0 <= idx < len(code_blocks):
                    code_blocks[idx]["language"] = p.get("language", code_blocks[idx]["language"])
                    code_blocks[idx]["algorithm_name"] = p.get("algorithm_name")
                    code_blocks[idx]["purpose"] = p.get("purpose", code_blocks[idx]["purpose"])
                    code_blocks[idx]["sample_inputs"] = p.get("sample_inputs", [])
                    code_blocks[idx]["sample_outputs"] = p.get("sample_outputs", [])
                    code_blocks[idx]["related_concepts"] = p.get("related_concepts", [])
        except Exception as e:
            log.warning("Gemini code enrichment note: %s", e)

        return code_blocks

    def process_document(self, sections: List[ExtractedSection], document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identifies and processes all code blocks across the document."""
        extracted_all = []
        for sec in sections:
            blocks = self.extract_heuristically(sec.content, sec.page_number)
            if blocks:
                enhanced = self.enhance_with_gemini(blocks, sec.content)
                for b in enhanced:
                    block_id = str(uuid.uuid4())
                    b["id"] = block_id
                    extracted_all.append(b)

                    # Persist in document_code_blocks
                    if document_id:
                        try:
                            with get_db() as conn:
                                conn.execute("""
                                    INSERT INTO document_code_blocks (
                                        id, document_id, page_number, language,
                                        purpose, code_text, algorithm_name,
                                        sample_inputs_json, sample_outputs_json,
                                        related_concepts_json
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    block_id, document_id, b["page_number"], b["language"],
                                    b["purpose"], b["code_text"], b.get("algorithm_name"),
                                    json.dumps(b.get("sample_inputs", [])),
                                    json.dumps(b.get("sample_outputs", [])),
                                    json.dumps(b.get("related_concepts", []))
                                ))
                                conn.commit()
                        except Exception as db_err:
                            log.warning("Could not persist code block for doc %s: %s", document_id, db_err)

        return extracted_all
