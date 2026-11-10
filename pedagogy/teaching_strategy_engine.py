"""
Adaptive Teaching Strategy Engine for Universal AI Educator.
Dynamically maps extracted concepts, programming algorithms, mathematical equations,
and visual diagrams to optimal cognitive teaching methods (code walkthroughs,
execution traces, derivations, process animations, timelines, case studies)
instead of static subject templates.
"""

import os
import re
import json
import uuid
import logging
from typing import List, Dict, Any, Optional

from pedagogy.models import Concept, TeachingRecommendation
from db_adapter import get_db

log = logging.getLogger("pod_siksha.teaching_strategy")

METHOD_ANIMATION_MAP = {
    "code_walkthrough": "sorting_algorithm",
    "execution_trace": "sorting_algorithm",
    "mathematical_derivation": "force_vectors",
    "interactive_graph": "growth_curve",
    "process_animation": "circulation",
    "labelled_diagram": "educational_2d",
    "timeline": "cycle_loop",
    "case_study": "educational_2d",
    "step_by_step": "educational_2d",
    "socratic_questioning": "cycle_loop"
}

class AdaptiveTeachingStrategyEngine:
    """Selects pedagogical strategies dynamically based on conceptual taxonomy and cognitive load."""

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

    def recommend_strategies(
        self,
        document_id: str,
        subject: str,
        concepts: List[Concept],
        has_code: bool = False,
        has_math: bool = False,
        has_figures: bool = False
    ) -> List[TeachingRecommendation]:
        """Generates cognitive teaching strategy recommendations for each concept."""
        concept_summaries = [
            {"name": c.concept_name, "type": c.concept_type, "summary": c.summary or c.definition}
            for c in concepts
        ]

        prompt = f"""You are an elite educational psychologist and instructional designer for an AI Universal Educator.
Document Subject: "{subject}"
Document Modalities Present: Code={has_code}, Math/Equations={has_math}, Visual Diagrams={has_figures}

Concepts to teach:
{json.dumps(concept_summaries)}

For each concept, select the single most effective pedagogical teaching method from:
- "step_by_step" (Linear procedural breakdown)
- "animated_demonstration" (Dynamic motion and cycle visualization)
- "interactive_diagram" (Spatial component exploration)
- "code_walkthrough" (Syntax, algorithm logic, and line-by-line flow)
- "execution_trace" (Variable state evolution across time and loop steps)
- "mathematical_derivation" (Analytical step-by-step transformation)
- "worked_example" (Concrete numerical or practical problem solving)
- "timeline" (Chronological cause-and-effect progression)
- "comparison" (Side-by-side trade-off and distinction analysis)
- "case_study" (Real-world scenario application)
- "socratic_questioning" (Inquiry-based guided discovery)

Provide:
1. concept_name
2. recommended_method
3. rationale (Why this method is cognitively superior for this concept)
4. suggested_animation_type: "circulation" | "cycle_loop" | "force_vectors" | "sorting_algorithm" | "molecular_reaction" | "growth_curve" | "educational_2d"
5. step_plan: 3 to 5 concrete teaching stages to guide the student from novice to mastery.

Respond strictly with valid JSON matching:
{{
  "recommendations": [
    {{
      "concept_name": "...",
      "recommended_method": "...",
      "rationale": "...",
      "suggested_animation_type": "...",
      "step_plan": ["Step 1", "Step 2", "Step 3"]
    }}
  ]
}}
"""
        recommendations = []
        parsed = None

        if self.client:
            models_to_try = [os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"), "gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
            for model in models_to_try:
                try:
                    res = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )
                    raw = re.sub(r"^```(?:json)?\s*", "", res.text.strip(), flags=re.MULTILINE)
                    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
                    parsed = json.loads(raw).get("recommendations", [])
                    break
                except Exception as e:
                    log.warning("Teaching strategy recommendation on %s failed: %s", model, e)
                    continue

        if not parsed:
            # Heuristic strategy selection
            parsed = []
            for c in concepts:
                c_name_lower = c.concept_name.lower()
                if has_code or any(k in c_name_lower for k in ["tree", "search", "sort", "algorithm", "loop", "pointer"]):
                    method = "code_walkthrough"
                    anim = "sorting_algorithm"
                    rationale = "Code structure and state transitions require visual walkthrough and trace."
                elif has_math or any(k in c_name_lower for k in ["calculus", "integral", "derivative", "equation", "wave", "matrix"]):
                    method = "mathematical_derivation"
                    anim = "force_vectors"
                    rationale = "Mathematical expressions are best understood through step-by-step derivation."
                elif has_figures or any(k in c_name_lower for k in ["cell", "heart", "cycle", "reaction", "system"]):
                    method = "animated_demonstration"
                    anim = "circulation"
                    rationale = "Dynamic biological/physical processes benefit from visual motion."
                else:
                    method = "step_by_step"
                    anim = "educational_2d"
                    rationale = "Foundational concepts require structured, bite-sized explanatory steps."

                parsed.append({
                    "concept_name": c.concept_name,
                    "recommended_method": method,
                    "rationale": rationale,
                    "suggested_animation_type": anim,
                    "step_plan": [
                        f"Introduce core definition of {c.concept_name}",
                        "Present intuitive visual analogy",
                        "Deconstruct key mechanics and edge cases",
                        "Reinforce with interactive checkpoint"
                    ]
                })

        for p_idx, rec in enumerate(parsed):
            strat_id = str(uuid.uuid4())
            method = rec.get("recommended_method", "step_by_step")
            anim = rec.get("suggested_animation_type") or METHOD_ANIMATION_MAP.get(method, "educational_2d")
            rationale = rec.get("rationale", "")
            step_plan = rec.get("step_plan", [])
            concept_name = rec.get("concept_name", concepts[min(p_idx, len(concepts)-1)].concept_name)

            rec_obj = TeachingRecommendation(
                id=strat_id,
                concept_name=concept_name,
                recommended_method=method,
                rationale=rationale,
                suggested_animation_type=anim,
                priority=p_idx + 1,
                step_plan=step_plan
            )
            recommendations.append(rec_obj)

            # Persist in teaching_strategies
            if document_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO teaching_strategies (
                                id, document_id, concept_name, recommended_method,
                                rationale, suggested_animation_type, priority, step_plan_json
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            strat_id, document_id, concept_name, method,
                            rationale, anim, p_idx + 1, json.dumps(step_plan)
                        ))
                        conn.commit()
                except Exception as db_err:
                    log.warning("Could not persist teaching_strategy: %s", db_err)

        return recommendations
