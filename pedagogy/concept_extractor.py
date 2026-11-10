"""
Pedagogical Concept Extractor for Universal AI Educator.
Analyzes extracted document sections, code, math, and figures to construct a rich,
grounded concept dependency graph with prerequisites, definitions, learning objectives,
and universal subject taxonomy without arbitrary category restrictions.
"""

import os
import re
import json
import uuid
import logging
from typing import List, Dict, Any, Optional

from pedagogy.models import Concept, ConceptRelationship, ConceptGraph
from extractors.base import ExtractedSection
from db_adapter import get_db

log = logging.getLogger("pod_siksha.concept_extractor")

class PedagogicalConceptExtractor:
    """Universal pedagogical concept analyzer and dependency graph constructor."""

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
                log.warning("Could not auto-initialize Gemini client in ConceptExtractor: %s", e)

    def extract_concepts_and_graph(
        self,
        document_id: str,
        filename: str,
        sections: List[ExtractedSection],
        code_blocks: Optional[List[Dict[str, Any]]] = None,
        math_expressions: Optional[List[Dict[str, Any]]] = None,
        figures: Optional[List[Dict[str, Any]]] = None
    ) -> ConceptGraph:
        """Constructs a comprehensive concept graph from multimodal document extractions."""
        # Collate summary sample of sections across pages
        sample_sections = []
        for s in sections[:15]:
            sample_sections.append(f"[Page {s.page_number} - {s.section_title} ({s.content_type})]: {s.content[:350]}")

        doc_summary_text = "\n".join(sample_sections)
        code_hints = [f"{b.get('language')}: {b.get('algorithm_name') or b.get('purpose')}" for b in (code_blocks or [])[:5]]
        math_hints = [m.get("latex_expr") for m in (math_expressions or [])[:5]]
        fig_hints = [f"{f.get('figure_type')}: {f.get('caption')}" for f in (figures or [])[:5]]

        prompt = f"""You are a master curriculum architect and cognitive scientist for an AI Universal Educator.
Analyze the following document extractions:

Filename: "{filename}"
Extracted Sections:
\"\"\"
{doc_summary_text[:6000]}
\"\"\"

Code Snippets Detected: {json.dumps(code_hints)}
Mathematical Formulas: {json.dumps(math_hints)}
Figures/Diagrams: {json.dumps(fig_hints)}

YOUR TASK:
1. Identify the genuine subject (e.g. "Computer Science / Data Structures", "Cell Biology & Bioenergetics", "Quantum Mechanics", "Differential Calculus", "Medieval History", "Constitutional Law", etc.). Do NOT restrict yourself to a predefined 8-subject list.
2. Identify the central Topic and Chapter Title.
3. Extract 4 to 8 primary educational concepts taught in this document.
   For each concept:
   - concept_name: Canonical, concise concept name.
   - concept_type: "foundational" | "core" | "mechanism" | "algorithm" | "theorem" | "applied"
   - definition: Precise educational definition grounded in the document.
   - summary: 1-2 sentence intuitive explanation.
   - prerequisites: What must a student know BEFORE learning this concept?
   - learning_objectives: What will the student be able to do/explain after mastering it?
   - common_confusions: Misconceptions students often suffer regarding this concept.
   - examples: Real-world or code/mathematical examples illustrating it.
   - source_page: The primary page number (integer) where this concept is introduced.
   - confidence: Number between 0.8 and 1.0.
4. Establish concept relationships (directed edges in the learning graph):
   - from_concept -> to_concept
   - relationship_type: "prerequisite_for" | "part_of" | "specializes" | "leads_to"
   - evidence_text: Short text reason for this link.
5. Provide the optimal sequential learning path (ordered list of concept names).

Respond strictly with valid JSON matching this schema:
{{
  "subject": "Specific Subject Area",
  "topic": "Core Topic",
  "chapter_title": "Chapter or Document Title",
  "concepts": [
    {{
      "concept_name": "Concept 1",
      "concept_type": "core",
      "definition": "...",
      "summary": "...",
      "prerequisites": ["Prereq 1"],
      "learning_objectives": ["Objective 1"],
      "common_confusions": ["Misconception 1"],
      "examples": ["Example 1"],
      "source_page": 1,
      "confidence": 0.95
    }}
  ],
  "relationships": [
    {{
      "from_concept": "Concept 1",
      "to_concept": "Concept 2",
      "relationship_type": "prerequisite_for",
      "evidence_text": "..."
    }}
  ],
  "suggested_learning_path": ["Concept 1", "Concept 2"]
}}
"""
        models_to_try = [os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"), "gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
        graph_data = None

        if self.client:
            for model in models_to_try:
                try:
                    res = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )
                    raw = re.sub(r"^```(?:json)?\s*", "", res.text.strip(), flags=re.MULTILINE)
                    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
                    graph_data = json.loads(raw)
                    break
                except Exception as e:
                    log.warning("Concept graph generation with model %s failed: %s", model, e)
                    continue

        if not graph_data:
            # Fallback heuristic graph construction if Gemini unreachable
            base_title = filename.rsplit(".", 1)[0].replace("_", " ").title()
            graph_data = {
                "subject": "Universal Learning",
                "topic": base_title,
                "chapter_title": base_title,
                "concepts": [
                    {
                        "concept_name": f"{base_title} Fundamentals",
                        "concept_type": "foundational",
                        "definition": f"Core introductory concepts and definitions for {base_title}.",
                        "summary": "Foundational grounding in the subject matter.",
                        "prerequisites": [],
                        "learning_objectives": [f"Understand core principles of {base_title}"],
                        "common_confusions": [],
                        "examples": [],
                        "source_page": 1,
                        "confidence": 0.8
                    }
                ],
                "relationships": [],
                "suggested_learning_path": [f"{base_title} Fundamentals"]
            }

        # Build Concept objects
        concepts_list = []
        for c in graph_data.get("concepts", []):
            c_id = str(uuid.uuid4())
            concept_obj = Concept(
                id=c_id,
                concept_name=c.get("concept_name", "Core Concept"),
                concept_type=c.get("concept_type", "core"),
                definition=c.get("definition", ""),
                summary=c.get("summary", ""),
                prerequisites=c.get("prerequisites", []),
                learning_objectives=c.get("learning_objectives", []),
                common_confusions=c.get("common_confusions", []),
                examples=c.get("examples", []),
                source_page=int(c.get("source_page", 1)),
                confidence=float(c.get("confidence", 0.95))
            )
            concepts_list.append(concept_obj)

            # Persist in document_concepts
            if document_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO document_concepts (
                                id, document_id, concept_name, concept_type,
                                definition, summary, prerequisites_json,
                                learning_objectives_json, common_confusions_json,
                                examples_json, source_page, confidence
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            c_id, document_id, concept_obj.concept_name, concept_obj.concept_type,
                            concept_obj.definition, concept_obj.summary,
                            json.dumps(concept_obj.prerequisites),
                            json.dumps(concept_obj.learning_objectives),
                            json.dumps(concept_obj.common_confusions),
                            json.dumps(concept_obj.examples),
                            concept_obj.source_page, concept_obj.confidence
                        ))
                        conn.commit()
                except Exception as db_err:
                    log.warning("Could not persist document_concept: %s", db_err)

        # Build Relationships
        relationships_list = []
        for r in graph_data.get("relationships", []):
            r_id = str(uuid.uuid4())
            rel_obj = ConceptRelationship(
                id=r_id,
                from_concept=r.get("from_concept", ""),
                to_concept=r.get("to_concept", ""),
                relationship_type=r.get("relationship_type", "leads_to"),
                evidence_text=r.get("evidence_text", ""),
                weight=float(r.get("weight", 1.0))
            )
            relationships_list.append(rel_obj)

            # Persist in concept_relationships
            if document_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO concept_relationships (
                                id, document_id, from_concept, to_concept,
                                relationship_type, evidence_text, weight
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            r_id, document_id, rel_obj.from_concept, rel_obj.to_concept,
                            rel_obj.relationship_type, rel_obj.evidence_text, rel_obj.weight
                        ))
                        conn.commit()
                except Exception as db_err:
                    log.warning("Could not persist concept_relationship: %s", db_err)

        return ConceptGraph(
            document_id=document_id,
            subject=graph_data.get("subject", "Universal Subject"),
            topic=graph_data.get("topic", filename),
            chapter_title=graph_data.get("chapter_title", filename),
            concepts=concepts_list,
            relationships=relationships_list,
            suggested_learning_path=graph_data.get("suggested_learning_path", [c.concept_name for c in concepts_list])
        )
