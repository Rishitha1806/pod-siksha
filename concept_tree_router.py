"""
Concept DNA & Knowledge Tree Router for Universal AI Educator.
Transforms extracted pedagogical concepts into an interactive, growing knowledge tree
rooted in actual learner progress, evidence-based statuses, and contextual actions.
"""

import os
import re
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, Header, Cookie

from db_adapter import get_db

log = logging.getLogger("pod_siksha.concept_tree")

router = APIRouter(prefix="/api/concept-tree", tags=["Concept Tree"])

# -------------------------------------------------------------
# Dependency: Authenticated User
# -------------------------------------------------------------
def get_auth_user(
    authorization: Optional[str] = Header(None),
    auth_token: Optional[str] = Cookie(None),
    token: Optional[str] = Query(None)
) -> dict:
    from server import get_current_user
    return get_current_user(authorization, auth_token, token)

def normalize_tag(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"[\s_]+", "-", clean)

def call_gemini_internal(prompt: str, json_mode: bool = False, temperature: float = 0.3) -> str:
    from server import call_gemini
    return call_gemini(prompt, json_mode=json_mode, temperature=temperature)

# -------------------------------------------------------------
# Pydantic Request Models
# -------------------------------------------------------------
class MarkRevisionRequest(BaseModel):
    concept_name: str
    reason: Optional[str] = "Needs further review"
    project_id: Optional[str] = None

class ConceptExplainRequest(BaseModel):
    concept_name: str
    mode: str = "simpler"  # 'simpler', 'step_by_step', 'analogy', 'real_world'
    complexity: str = "intermediate"  # 'beginner', 'intermediate', 'advanced'
    language: str = "en"
    project_id: Optional[str] = None

class ConceptCompareRequest(BaseModel):
    concept_a: str
    concept_b: str
    language: str = "en"
    project_id: Optional[str] = None

# -------------------------------------------------------------
# API: GET /api/concept-tree
# -------------------------------------------------------------
@router.get("")
def get_concept_tree(
    project_id: Optional[str] = None,
    user: dict = Depends(get_auth_user)
):
    """
    Returns the user's authentic personal knowledge tree.
    No hardcoded mock trees: derived purely from video_projects, video_scenes,
    document_concepts, and user_concept_progress.
    """
    user_id = user["id"]
    with get_db() as conn:
        # Fetch relevant projects for this user
        if project_id:
            projects_rows = conn.execute(
                "SELECT id, title, topic, language, total_scenes FROM video_projects WHERE id = ? AND (user_id = ? OR user_id IS NULL)",
                (project_id, user_id)
            ).fetchall()
        else:
            projects_rows = conn.execute(
                "SELECT id, title, topic, language, total_scenes FROM video_projects WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()

        if not projects_rows:
            return {
                "trees": [],
                "total_concepts": 0,
                "understood_count": 0,
                "learning_count": 0,
                "revision_count": 0,
                "message": "Your knowledge tree will grow as you explore and learn. Upload a document or enter any topic to begin."
            }

        trees = []
        global_total = 0
        global_understood = 0
        global_learning = 0
        global_revision = 0

        for proj in projects_rows:
            p_id = proj["id"]
            p_title = proj["title"]
            p_topic = proj["topic"] or p_title

            # Fetch scenes for this project
            scenes = conn.execute(
                "SELECT id, scene_index, title, concept_tag, learning_objective, narration_text, checkpoint_question FROM video_scenes WHERE project_id = ? ORDER BY scene_index ASC",
                (p_id,)
            ).fetchall()

            # Fetch user progress for these concepts
            prog_rows = conn.execute(
                "SELECT * FROM user_concept_progress WHERE user_id = ?",
                (user_id,)
            ).fetchall()
            prog_by_tag = {row["normalized_tag"]: dict(row) for row in prog_rows}

            # Map scenes to concept nodes
            concept_nodes = []
            seen_tags = set()

            for sc in scenes:
                raw_tag = sc["concept_tag"] or sc["title"]
                norm = normalize_tag(raw_tag)
                if not norm or norm in seen_tags:
                    continue
                seen_tags.add(norm)

                prog = prog_by_tag.get(norm, {})
                status = prog.get("status", "learning")
                status_reason = prog.get("status_reason") or f"Introduced in Scene {sc['scene_index']}: {sc['title']}"
                mastery = float(prog.get("mastery_score", 60.0))
                times_quizzed = int(prog.get("times_quizzed", 0))
                times_correct = int(prog.get("times_correct", 0))

                # Check if there is an active misconception in DB
                misc = conn.execute(
                    "SELECT misconception_text FROM misconceptions WHERE user_id = ? AND concept_tag = ? AND status = 'active'",
                    (user_id, raw_tag)
                ).fetchone()
                if misc:
                    status = "needs_revision"
                    status_reason = f"Diagnosed misconception: {misc['misconception_text']}"

                # Parse checkpoint question if available
                cp = {}
                if sc["checkpoint_question"]:
                    try:
                        cp = json.loads(sc["checkpoint_question"]) if isinstance(sc["checkpoint_question"], str) else sc["checkpoint_question"]
                    except Exception:
                        cp = {}

                # Determine prerequisites (previous scenes in the sequential curriculum)
                prereqs = []
                idx = sc["scene_index"]
                if idx > 1:
                    prev_scene = next((s for s in scenes if s["scene_index"] == idx - 1), None)
                    if prev_scene and prev_scene["concept_tag"] != raw_tag:
                        prereqs.append(prev_scene["concept_tag"])

                # Determine related concepts (next scene or peer concepts)
                related = []
                if idx < len(scenes):
                    next_scene = next((s for s in scenes if s["scene_index"] == idx + 1), None)
                    if next_scene and next_scene["concept_tag"] != raw_tag:
                        related.append(next_scene["concept_tag"])

                concept_node = {
                    "id": f"node_{norm}",
                    "name": raw_tag,
                    "normalized_tag": norm,
                    "definition": sc["learning_objective"] or sc["narration_text"][:140] + "...",
                    "summary": sc["learning_objective"] or f"Key concept in {p_title}",
                    "status": status,
                    "status_reason": status_reason,
                    "mastery_score": mastery,
                    "project_id": p_id,
                    "project_title": p_title,
                    "scene_index": sc["scene_index"],
                    "scene_id": sc["id"],
                    "scene_title": sc["title"],
                    "prerequisites": prereqs,
                    "related": related,
                    "has_checkpoint": bool(cp.get("question")),
                    "quiz_performance": {
                        "times_quizzed": times_quizzed,
                        "times_correct": times_correct
                    },
                    "children": []
                }
                concept_nodes.append(concept_node)

                global_total += 1
                if status == "understood":
                    global_understood += 1
                elif status == "needs_revision":
                    global_revision += 1
                else:
                    global_learning += 1

            # Build hierarchical tree:
            # Root: Lesson Topic
            # Level 1: Core concepts (First half or foundational scenes)
            # Level 2: Subconcepts (Second half or dependent scenes)
            if concept_nodes:
                root_node = {
                    "id": f"root_{p_id}",
                    "name": p_title,
                    "is_root": True,
                    "status": "in_progress",
                    "total_concepts": len(concept_nodes),
                    "children": []
                }

                # Partition into major concepts and subconcepts based on prerequisites
                major_concepts = []
                sub_concepts = []

                for idx, c in enumerate(concept_nodes):
                    if not c["prerequisites"] or idx < max(2, len(concept_nodes) // 2):
                        major_concepts.append(c)
                    else:
                        sub_concepts.append(c)

                # Attach subconcepts to matching major concepts where appropriate
                for sub in sub_concepts:
                    attached = False
                    for major in major_concepts:
                        if major["name"] in sub["prerequisites"] or sub["name"] in major["related"]:
                            major["children"].append(sub)
                            attached = True
                            break
                    if not attached:
                        major_concepts.append(sub)

                root_node["children"] = major_concepts

                # Build directed prerequisite edges
                edges = []
                for c in concept_nodes:
                    for pr in c["prerequisites"]:
                        norm_pr = normalize_tag(pr)
                        edges.append({
                            "from": f"node_{norm_pr}",
                            "to": c["id"],
                            "type": "prerequisite"
                        })
                    for rel in c["related"]:
                        norm_rel = normalize_tag(rel)
                        edges.append({
                            "from": c["id"],
                            "to": f"node_{norm_rel}",
                            "type": "related"
                        })

                trees.append({
                    "project_id": p_id,
                    "title": p_title,
                    "topic": p_topic,
                    "total_concepts": len(concept_nodes),
                    "tree": root_node,
                    "edges": edges,
                    "all_nodes": concept_nodes
                })

        return {
            "trees": trees,
            "total_concepts": global_total,
            "understood_count": global_understood,
            "learning_count": global_learning,
            "revision_count": global_revision
        }

# -------------------------------------------------------------
# API: GET /api/concept-tree/node/{concept_tag}
# -------------------------------------------------------------
@router.get("/node/{concept_tag}")
def get_concept_node_detail(
    concept_tag: str,
    project_id: Optional[str] = None,
    user: dict = Depends(get_auth_user)
):
    """Returns detailed context, evidence, and actions for a single concept."""
    user_id = user["id"]
    norm = normalize_tag(concept_tag)

    with get_db() as conn:
        # Check user_concept_progress
        prog = conn.execute(
            "SELECT * FROM user_concept_progress WHERE user_id = ? AND normalized_tag = ?",
            (user_id, norm)
        ).fetchone()

        # Find corresponding video scene
        scene_row = None
        if project_id:
            scene_row = conn.execute("""
                SELECT s.*, p.title as project_title, p.id as project_id
                FROM video_scenes s
                JOIN video_projects p ON p.id = s.project_id
                WHERE p.id = ? AND (s.concept_tag LIKE ? OR s.title LIKE ?)
            """, (project_id, f"%{concept_tag}%", f"%{concept_tag}%")).fetchone()

        if not scene_row:
            scene_row = conn.execute("""
                SELECT s.*, p.title as project_title, p.id as project_id
                FROM video_scenes s
                JOIN video_projects p ON p.id = s.project_id
                WHERE (p.user_id = ? OR p.user_id IS NULL) AND (s.concept_tag LIKE ? OR s.title LIKE ?)
                ORDER BY s.created_at DESC LIMIT 1
            """, (user_id, f"%{concept_tag}%", f"%{concept_tag}%")).fetchone()

        if not scene_row and not prog:
            raise HTTPException(status_code=404, detail=f"Concept '{concept_tag}' not found in your learning history.")

        # Misconception check
        misc = conn.execute(
            "SELECT * FROM misconceptions WHERE user_id = ? AND concept_tag LIKE ? AND status = 'active'",
            (user_id, f"%{concept_tag}%")
        ).fetchone()

        status = prog["status"] if prog else "learning"
        if misc:
            status = "needs_revision"

        status_reason = prog["status_reason"] if prog else (f"Diagnosed misconception: {misc['misconception_text']}" if misc else "Introduced during active lesson.")

        # Checkpoint quiz from scene
        checkpoint_data = {}
        if scene_row and scene_row["checkpoint_question"]:
            try:
                checkpoint_data = json.loads(scene_row["checkpoint_question"]) if isinstance(scene_row["checkpoint_question"], str) else scene_row["checkpoint_question"]
            except Exception:
                checkpoint_data = {}

        return {
            "name": concept_tag,
            "normalized_tag": norm,
            "definition": scene_row["learning_objective"] if scene_row else (prog["definition"] if prog else ""),
            "narration_excerpt": scene_row["narration_text"] if scene_row else "",
            "status": status,
            "status_reason": status_reason,
            "mastery_score": float(prog["mastery_score"]) if prog else 65.0,
            "project_id": scene_row["project_id"] if scene_row else (prog["project_id"] if prog else None),
            "project_title": scene_row["project_title"] if scene_row else "",
            "scene_index": scene_row["scene_index"] if scene_row else 1,
            "scene_id": scene_row["id"] if scene_row else None,
            "checkpoint_question": checkpoint_data,
            "has_active_misconception": bool(misc),
            "misconception_text": misc["misconception_text"] if misc else None
        }

# -------------------------------------------------------------
# API: POST /api/concept-tree/mark-revision
# -------------------------------------------------------------
@router.post("/mark-revision")
def mark_concept_for_revision(
    payload: MarkRevisionRequest,
    user: dict = Depends(get_auth_user)
):
    """Flags a concept as 'needs_revision' based on user intent or evidence."""
    user_id = user["id"]
    norm = normalize_tag(payload.concept_name)

    with get_db() as conn:
        reason = payload.reason or "Marked for revision by learner"
        conn.execute("""
            INSERT INTO user_concept_progress (
                id, user_id, concept_name, normalized_tag, status, status_reason,
                project_id, times_studied, updated_at
            ) VALUES (?, ?, ?, ?, 'needs_revision', ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, normalized_tag) DO UPDATE SET
                status = 'needs_revision',
                status_reason = excluded.status_reason,
                updated_at = CURRENT_TIMESTAMP
        """, (str(uuid.uuid4()), user_id, payload.concept_name, norm, reason, payload.project_id))

        # Add to memory_loop
        conn.execute("""
            INSERT INTO memory_loop (id, user_id, concept_tag, due_at, status)
            VALUES (?, ?, ?, datetime('now', '+24 hours'), 'queued')
        """, (str(uuid.uuid4()), user_id, payload.concept_name))

        conn.commit()

    return {
        "status": "success",
        "concept_name": payload.concept_name,
        "new_status": "needs_revision",
        "reason": reason
    }

# -------------------------------------------------------------
# API: POST /api/concept-tree/explain
# -------------------------------------------------------------
@router.post("/explain")
def explain_concept_dynamically(
    payload: ConceptExplainRequest,
    user: dict = Depends(get_auth_user)
):
    """Generates an authentic Gemini-grounded explanation tailored to requested mode and complexity."""
    mode_instructions = {
        "simpler": "Explain this concept in exceptionally simple, intuitive language avoiding heavy academic jargon. Use an everyday mental model.",
        "step_by_step": "Break down this concept into 3 to 4 sequential, numbered logical steps that build upon each other.",
        "analogy": "Create a vivid, relatable real-world analogy that makes this abstract concept instantly clear.",
        "real_world": "Explain how this concept is directly applied in real-world technology, nature, industry, or everyday life."
    }

    instruction = mode_instructions.get(payload.mode, mode_instructions["simpler"])

    prompt = f"""You are the master AI educator in Pod-Siksha 3.0.
A learner has selected the concept "{payload.concept_name}" from their interactive Knowledge Tree.

REQUESTED EXPLANATION MODE:
{payload.mode.upper()}: {instruction}

LEARNER COMPLEXITY LEVEL: {payload.complexity.upper()}
LANGUAGE: {payload.language} (Provide the explanation in this language, keeping scientific/technical terms clear).

Return a valid JSON response:
{{
  "title": "{payload.concept_name}",
  "mode": "{payload.mode}",
  "explanation": "2 to 3 paragraphs of clear, engaging educational explanation",
  "key_takeaways": [
    "Key takeaway point 1",
    "Key takeaway point 2"
  ],
  "visual_cue": "Brief description of how to visualize this concept mentally"
}}
"""
    raw = call_gemini_internal(prompt, json_mode=True, temperature=0.3)
    try:
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE)
        data = json.loads(clean)
    except Exception as e:
        log.warning("Could not parse explanation JSON: %s", e)
        data = {
            "title": payload.concept_name,
            "mode": payload.mode,
            "explanation": f"Understanding {payload.concept_name}: {instruction}",
            "key_takeaways": [f"Core principle of {payload.concept_name}"],
            "visual_cue": "Visualize the components functioning in sequence."
        }

    return data

# -------------------------------------------------------------
# API: POST /api/concept-tree/compare
# -------------------------------------------------------------
@router.post("/compare")
def compare_concepts(
    payload: ConceptCompareRequest,
    user: dict = Depends(get_auth_user)
):
    """Compares two concepts selected from the learner's knowledge tree."""
    prompt = f"""You are an educational comparative analyst in Pod-Siksha 3.0.
A learner wants to compare two concepts from their learning journey:

Concept A: "{payload.concept_a}"
Concept B: "{payload.concept_b}"

LANGUAGE: {payload.language}

Provide a rigorous, structured comparative analysis.
Return valid JSON matching this schema:
{{
  "concept_a": "{payload.concept_a}",
  "concept_b": "{payload.concept_b}",
  "overview": "Concise summary comparing the two concepts",
  "similarities": [
    "Shared characteristic 1",
    "Shared characteristic 2"
  ],
  "differences": [
    "Key distinction 1",
    "Key distinction 2"
  ],
  "comparison_table": [
    {{"attribute": "Primary Purpose", "concept_a_val": "...", "concept_b_val": "..."}},
    {{"attribute": "Key Mechanism", "concept_a_val": "...", "concept_b_val": "..."}},
    {{"attribute": "Typical Context", "concept_a_val": "...", "concept_b_val": "..."}}
  ],
  "check_question": {{
    "question": "A concise multiple-choice question testing understanding of the key distinction",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Why this distinction is fundamental"
  }}
}}
"""
    raw = call_gemini_internal(prompt, json_mode=True, temperature=0.2)
    try:
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE)
        data = json.loads(clean)
    except Exception as e:
        log.warning("Could not parse comparison JSON: %s", e)
        data = {
            "concept_a": payload.concept_a,
            "concept_b": payload.concept_b,
            "overview": f"Comparative analysis between {payload.concept_a} and {payload.concept_b}.",
            "similarities": ["Both are foundational principles in their respective domains."],
            "differences": [f"{payload.concept_a} operates under distinct mechanisms compared to {payload.concept_b}."],
            "comparison_table": [
                {"attribute": "Definition", "concept_a_val": payload.concept_a, "concept_b_val": payload.concept_b}
            ],
            "check_question": {
                "question": f"Which statement accurately distinguishes {payload.concept_a} from {payload.concept_b}?",
                "options": ["They serve distinct structural roles", "They are identical in all contexts", "Neither is applicable", "Both occur simultaneously without difference"],
                "correct_index": 0,
                "explanation": "Each concept addresses a distinct phase and operational constraint."
            }
        }

    return data
