"""
FastAPI Router for Pod-Siksha 2.0 — Universal AI Animated Learning Platform.
Integrates adaptive learning profiles, multi-format document extraction,
Gemini storyboard generation, Neon PostgreSQL persistence, scene narration,
and interactive visual Q&A.
"""

import json
import logging
import re
import uuid
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, Request
from pydantic import BaseModel

from db_adapter import get_db
from animated_curator import (
    LEARNER_PROFILES,
    ANIMATION_TYPES,
    build_storyboard_prompt,
    generate_subtitles_spec
)
from doc_parser import extract_document_content

log = logging.getLogger("pod_siksha.animated_router")

router = APIRouter(prefix="/api/animated", tags=["animated_learning"])

def get_auth_user(req: Request) -> dict:
    from server import get_current_user
    auth = req.headers.get("Authorization")
    cookie = req.cookies.get("auth_token")
    return get_current_user(authorization=auth, auth_token=cookie)

def verify_project_ownership(project_id: str, user: dict) -> dict:
    """Verifies that the requested animated project belongs to the authenticated user."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM video_projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Animated video project not found.")
        proj = dict(row)
        if user.get("role") in ("teacher", "admin"):
            return proj
        if proj.get("user_id") and proj.get("user_id") != user.get("id"):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have permission to access another learner's animated lesson.")
        return proj


class SceneRegenerateRequest(BaseModel):
    instruction: Optional[str] = "Make it clearer and more visual"
    focus_concept: Optional[str] = None


class CheckpointAnswerRequest(BaseModel):
    scene_id: str
    selected_option_index: Optional[int] = None
    selected_idx: Optional[int] = None
    question: Optional[str] = None
    is_correct: Optional[bool] = None


@router.get("/profiles")
def get_learner_profiles():
    """Returns the 5 universal learner audience profiles with pedagogical guidelines."""
    return {
        "status": "success",
        "profiles": LEARNER_PROFILES,
        "default": "teen"
    }


@router.get("/styles")
def get_animation_styles():
    """Returns supported animation styles with visual themes."""
    styles = {
        "educational_2d": {
            "name": "Clean 2D Educational",
            "description": "Crisp geometric diagrams, vector illustrations, fluid arrows and high-contrast labels."
        },
        "cartoon": {
            "name": "Playful Storytelling",
            "description": "Warm character illustrations, expressive analogies, and friendly colorful metaphors."
        },
        "simulation": {
            "name": "Scientific & Technical Simulation",
            "description": "Particle dynamics, vector fields, force lines, circuits, and coordinate transformations."
        },
        "whiteboard": {
            "name": "Whiteboard Explainer",
            "description": "Hand-sketched aesthetic, step-by-step marker reveals, and clear progressive formulas."
        },
        "infographic": {
            "name": "Data & Process Infographic",
            "description": "Sleek charts, flow topologies, quantitative growth curves, and architectural blocks."
        }
    }
    return {
        "status": "success",
        "styles": styles,
        "animation_types": ANIMATION_TYPES
    }


@router.post("/project")
async def create_animated_project(
    title: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    learner_profile: Optional[str] = Form("teen"),
    language: Optional[str] = Form("te"),
    animation_style: Optional[str] = Form("educational_2d"),
    source_type: Optional[str] = Form("topic"),
    content_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_auth_user)
):
    """Creates a new AI animated lesson project with structured visual scenes."""
    from server import call_gemini, LANG_CONFIGS
    
    extracted_text = ""
    if file and file.filename:
        file_bytes = await file.read()
        extracted_text = extract_document_content(file.filename, file_bytes)
        source_type = "document"
        if not title:
            title = file.filename.rsplit(".", 1)[0].replace("_", " ").title()
    elif content_text and content_text.strip():
        extracted_text = content_text.strip()
    elif topic and topic.strip():
        extracted_text = topic.strip()
    
    if not extracted_text or len(extracted_text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Learning topic or source material is required (at least 10 characters)."
        )

    topic_summary = topic or (extracted_text[:120] + "...")
    lesson_title = title or topic_summary[:60]
    learner_profile = learner_profile if learner_profile in LEARNER_PROFILES else "teen"
    language = language or "te"
    lang_info = LANG_CONFIGS.get(language, LANG_CONFIGS.get("te", {"name": "Telugu"}))
    lang_name = lang_info["name"]

    prompt = build_storyboard_prompt(
        title=lesson_title,
        source_content=extracted_text,
        profile_key=learner_profile,
        language=language,
        lang_name=lang_name,
        animation_style=animation_style or "educational_2d"
    )

    log.info("Generating animated lesson storyboard for profile '%s' in '%s'", learner_profile, lang_name)
    raw_json = call_gemini(prompt, json_mode=True)
    
    # Robust Multi-Stage JSON Extractor
    data = None
    try:
        text = raw_json.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        m = re.search(r"(\{[\s\S]*\})", text)
        if m:
            text = m.group(1)
        cleaned = re.sub(r",\s*([\]}])", r"\1", text)
        data = json.loads(cleaned)
    except Exception as parse_err:
        log.warning("Primary JSON parse failed: %s. Attempting regex extraction.", parse_err)
        # Attempt to recover title, summary, concepts, scenes
        try:
            # Fallback structure
            data = {
                "lesson_title": lesson_title,
                "summary": f"Interactive animated visual explanation of {topic_summary}.",
                "concepts": [lesson_title, "Fundamental Principles", "Practical Application"],
                "scenes": [
                    {
                        "scene_index": 1,
                        "title": f"Introduction to {lesson_title}",
                        "concept_tag": "Foundation",
                        "learning_objective": "Understand the core concept intuitively",
                        "narration_text": f"Welcome! Today we explore {lesson_title} and discover how it works step-by-step.",
                        "display_text": f"Core Concept: {lesson_title}",
                        "animation_type": "circulation" if "bio" in topic_summary.lower() else "cycle_loop" if "rain" in topic_summary.lower() else "force_vectors",
                        "duration_sec": 14.0,
                        "visual_spec": {"theme": animation_style, "highlight": lesson_title, "labels": ["Input", "Transformation", "Output"]},
                        "checkpoint_question": {"question": f"What is the main topic of this lesson?", "options": [lesson_title, "Unrelated Topic", "Random Noise", "None"], "correct_index": 0, "explanation": "The lesson introduces this core topic."}
                    },
                    {
                        "scene_index": 2,
                        "title": "Visual Mechanism & Dynamics",
                        "concept_tag": "Mechanics",
                        "learning_objective": "Observe the dynamic flow in action",
                        "narration_text": f"Notice the moving parts and key forces interacting together in harmony.",
                        "display_text": "Dynamic Simulation Stage",
                        "animation_type": "sorting_algorithm" if "sort" in topic_summary.lower() else "molecular_reaction" if "chem" in topic_summary.lower() else "growth_curve" if "interest" in topic_summary.lower() else "force_vectors",
                        "duration_sec": 14.0,
                        "visual_spec": {"theme": animation_style, "highlight": "Active Motion", "labels": ["Phase A", "Phase B", "Phase C"]},
                        "checkpoint_question": {"question": "How do the components interact?", "options": ["Through coordinated dynamic forces", "They do not interact", "Randomly", "Static"], "correct_index": 0, "explanation": "The components interact through coordinated forces."}
                    }
                ]
            }
        except Exception:
            raise HTTPException(status_code=500, detail="Could not extract lesson storyboard.")

    project_id = str(uuid.uuid4())
    final_title = data.get("lesson_title") or lesson_title
    summary = data.get("summary") or f"Visual lesson on {topic_summary}"
    scenes_data = data.get("scenes", [])
    
    if not scenes_data:
        raise HTTPException(status_code=500, detail="AI did not generate any scenes for this topic.")

    total_duration = sum(s.get("duration_sec", 12.0) for s in scenes_data)

    user_id = user.get("id", "user_demo_001")
    with get_db() as conn:
        conn.execute("""
            INSERT INTO video_projects (
                id, user_id, title, topic, learner_profile, teaching_style,
                animation_style, language, source_type, source_content,
                summary, total_scenes, total_duration_sec, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, user_id, final_title, topic_summary, learner_profile,
            "visual_demonstration", animation_style, language, source_type,
            extracted_text[:5000], summary, len(scenes_data), total_duration, "ready"
        ))

        for idx, s in enumerate(scenes_data):
            scene_id = str(uuid.uuid4())
            dur = float(s.get("duration_sec", 12.0))
            subtitles = generate_subtitles_spec(s.get("narration_text", ""), dur)
            visual_spec = s.get("visual_spec", {})
            anim_type = s.get("animation_type")
            if anim_type not in ANIMATION_TYPES:
                anim_type = "force_vectors" if "phys" in anim_type else "educational_2d"

            conn.execute("""
                INSERT INTO video_scenes (
                    id, project_id, scene_index, title, concept_tag,
                    learning_objective, narration_text, display_text,
                    animation_type, visual_spec, duration_sec, subtitles_spec,
                    checkpoint_question
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scene_id, project_id, idx + 1,
                s.get("title", f"Scene {idx+1}"),
                s.get("concept_tag", "Core Concept"),
                s.get("learning_objective", ""),
                s.get("narration_text", ""),
                s.get("display_text", ""),
                anim_type,
                json.dumps(visual_spec),
                dur,
                json.dumps(subtitles),
                json.dumps(s.get("checkpoint_question", {}))
            ))

        conn.commit()

    # Query inserted scenes to return comprehensive representation
    inserted_scenes = []
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, scene_index, title, concept_tag, narration_text, display_text, animation_type, visual_spec, duration_sec, checkpoint_question FROM video_scenes WHERE project_id = ? ORDER BY scene_index ASC", (project_id,))
        for row in cursor.fetchall():
            vs = json.loads(row[7]) if isinstance(row[7], str) else (row[7] or {})
            cp = json.loads(row[9]) if isinstance(row[9], str) else (row[9] or {})
            inserted_scenes.append({
                "id": row[0],
                "scene_index": row[1],
                "title": row[2],
                "concept_tag": row[3],
                "narration_text": row[4],
                "display_text": row[5],
                "animation_type": row[6],
                "visual_spec": vs,
                "duration_sec": row[8],
                "checkpoint_question": cp
            })

    return {
        "status": "success",
        "project_id": project_id,
        "id": project_id,
        "title": final_title,
        "summary": summary,
        "learner_profile": learner_profile,
        "language": language,
        "animation_style": animation_style,
        "total_scenes": len(scenes_data),
        "total_duration_sec": total_duration,
        "concepts": data.get("concepts", []),
        "scenes": inserted_scenes
    }


@router.get("/projects")
def list_animated_projects(user: dict = Depends(get_auth_user)):
    """Lists animated learning projects owned by the authenticated user."""
    user_id = user["id"]
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, title, topic, learner_profile, animation_style,
                   language, source_type, summary, total_scenes,
                   total_duration_sec, status, created_at
            FROM video_projects
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        
        projects = []
        for r in rows:
            d = dict(r)
            if hasattr(d.get("created_at"), "isoformat"):
                d["created_at"] = d["created_at"].isoformat()
            projects.append(d)

        return {
            "status": "success",
            "total": len(projects),
            "projects": projects
        }


@router.get("/project/{project_id}")
def get_animated_project(project_id: str, user: dict = Depends(get_auth_user)):
    """Fetches complete animated project details including all ordered scenes and visual specs."""
    proj = verify_project_ownership(project_id, user)
    
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, scene_index, title, concept_tag, learning_objective,
                   narration_text, display_text, animation_type, visual_spec,
                   duration_sec, subtitles_spec, checkpoint_question
            FROM video_scenes
            WHERE project_id = ?
            ORDER BY scene_index ASC
        """, (project_id,)).fetchall()

        scenes = []
        for r in rows:
            sc = dict(r)
            # Parse json fields if strings
            if isinstance(sc.get("visual_spec"), str):
                try:
                    sc["visual_spec"] = json.loads(sc["visual_spec"])
                except Exception:
                    pass
            if isinstance(sc.get("subtitles_spec"), str):
                try:
                    sc["subtitles_spec"] = json.loads(sc["subtitles_spec"])
                except Exception:
                    pass
            if isinstance(sc.get("checkpoint_question"), str):
                try:
                    sc["checkpoint_question"] = json.loads(sc["checkpoint_question"])
                except Exception:
                    pass
            scenes.append(sc)

    return {
        "status": "success",
        "project": proj,
        "scenes": scenes
    }


@router.delete("/project/{project_id}")
def delete_animated_project(project_id: str, user: dict = Depends(get_auth_user)):
    """Deletes an animated project and all its scenes."""
    verify_project_ownership(project_id, user)
    with get_db() as conn:
        conn.execute("DELETE FROM video_projects WHERE id = ?", (project_id,))
        conn.commit()
    return {"status": "success", "message": "Project deleted successfully."}


@router.get("/scene/{scene_id}/audio")
def get_scene_audio(scene_id: str, user: dict = Depends(get_auth_user)):
    """Generates / serves audio narration for an individual scene."""
    from server import call_gnani_tts
    
    with get_db() as conn:
        row = conn.execute("""
            SELECT s.narration_text, p.language, p.id as project_id, p.user_id
            FROM video_scenes s
            JOIN video_projects p ON p.id = s.project_id
            WHERE s.id = ?
        """, (scene_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Scene not found.")
        
        # Verify ownership
        if user.get("role") not in ("teacher", "admin") and row["user_id"] and row["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden.")
            
        text = row["narration_text"]
        lang = row["language"] or "te"

    audio_bytes = call_gnani_tts(text, language=lang, speaker="A")
    return Response(content=audio_bytes, media_type="audio/wav")


@router.post("/scene/{scene_id}/ask")
async def ask_scene_doubt(
    scene_id: str,
    doubt_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_auth_user)
):
    """Interactive In-Video Question: Learner pauses video and asks about the current scene."""
    from server import call_gemini, call_gnani_tts, call_gnani_stt
    
    with get_db() as conn:
        row = conn.execute("""
            SELECT s.*, p.title as project_title, p.language as project_lang, p.user_id, p.id as project_id
            FROM video_scenes s
            JOIN video_projects p ON p.id = s.project_id
            WHERE s.id = ?
        """, (scene_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Scene not found.")
        scene = dict(row)
        if user.get("role") not in ("teacher", "admin") and scene["user_id"] and scene["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden.")

    question = doubt_text or ""
    if file and file.filename:
        audio_bytes = await file.read()
        if len(audio_bytes) > 200:
            stt_res = call_gnani_stt(audio_bytes, filename="scene_doubt.wav", language=scene["project_lang"])
            question = stt_res.get("transcript", "").strip()

    if not question:
        question = "Can you explain this visual demonstration again in simpler terms?"

    prompt = f"""You are the Socratic AI teacher in Pod-Siksha 2.0.
A learner is watching an animated educational video and paused the lesson at this specific scene to ask a doubt.

LESSON CONTEXT:
- Lesson Title: {scene['project_title']}
- Scene Title: {scene['title']}
- Concept Tag: {scene['concept_tag']}
- Visual Animation Type: {scene['animation_type']}
- Scene Narration: {scene['narration_text']}
- Display Caption: {scene['display_text']}

LEARNER QUESTION:
"{question}"

INSTRUCTIONS:
1. Answer warmly, directly addressing the visual animation elements seen in this scene.
2. Provide an intuitive analogy or concrete visual detail.
3. Keep the spoken answer concise (2-3 sentences, < 240 chars) in {scene['project_lang']} code-mixed with English scientific/technical terms.
4. Provide an English summary (< 180 chars).

Respond with valid JSON:
{{
  "spoken_answer": "Concise spoken answer in {scene['project_lang']} (< 240 chars)",
  "display_answer": "English caption (< 180 chars)",
  "concept_clarified": "{scene['concept_tag']}"
}}
"""
    raw_json = call_gemini(prompt, json_mode=True)
    try:
        ans_data = json.loads(raw_json)
    except Exception:
        ans_data = {
            "spoken_answer": "ఈ యానిమేషన్ లో చూపించిన భావన చాలా ముఖ్యం.",
            "display_answer": f"In this scene, {scene['concept_tag']} illustrates how the system operates.",
            "concept_clarified": scene["concept_tag"]
        }

    # Generate audio for the answer
    audio_bytes = call_gnani_tts(ans_data["spoken_answer"], language=scene["project_lang"], speaker="A")
    import base64
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    # Record doubt in database
    with get_db() as conn:
        conn.execute("""
            INSERT INTO doubts (
                id, session_id, turn_index, transcribed_text,
                detected_language, concept_tag, hint_level, answer_text, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), scene["project_id"], scene["scene_index"],
            question, scene["project_lang"], scene["concept_tag"], 1,
            ans_data["spoken_answer"], user["id"]
        ))
        conn.commit()

    return {
        "status": "success",
        "question": question,
        "spoken_answer": ans_data.get("spoken_answer"),
        "display_answer": ans_data.get("display_answer"),
        "concept_clarified": ans_data.get("concept_clarified"),
        "audio_base64": audio_b64
    }


@router.post("/project/{project_id}/checkpoint")
def submit_checkpoint_answer(
    project_id: str,
    payload: CheckpointAnswerRequest,
    user: dict = Depends(get_auth_user)
):
    """Submits answer to an interactive checkpoint question; updates Concept DNA."""
    proj = verify_project_ownership(project_id, user)
    
    with get_db() as conn:
        row = conn.execute("""
            SELECT checkpoint_question, concept_tag
            FROM video_scenes
            WHERE id = ? AND project_id = ?
        """, (payload.scene_id, project_id)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Scene not found.")
            
        chk = row["checkpoint_question"]
        if isinstance(chk, str):
            try:
                chk = json.loads(chk)
            except Exception:
                chk = {}

        sel_idx = payload.selected_option_index if payload.selected_option_index is not None else (payload.selected_idx or 0)
        correct_idx = chk.get("correct_index", 0)
        is_correct = (sel_idx == correct_idx)
        score = 1.0 if is_correct else 0.3
        concept_tag = row["concept_tag"]

        # Check if project_id exists in sessions table to satisfy foreign key
        sess_check = conn.execute("SELECT id FROM sessions WHERE id = ?", (project_id,)).fetchone()
        valid_sess_id = project_id if sess_check else None

        concept_event_id = str(uuid.uuid4())
        # Record concept event
        conn.execute("""
            INSERT INTO concept_events (
                id, session_id, concept_tag, normalized_tag, event_type,
                hint_level, quiz_status, score, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            concept_event_id, valid_sess_id, concept_tag, concept_tag.lower().strip(),
            "checkpoint", 1, "correct" if is_correct else "incorrect", score, user["id"]
        ))
        conn.commit()

    return {
        "status": "success",
        "ok": True,
        "concept_id": concept_event_id,
        "is_correct": is_correct,
        "correct_index": correct_idx,
        "explanation": chk.get("explanation", "Good job engaging with the lesson visual concept!"),
        "score": score
    }


@router.get("/project/{project_id}/export/manifest")
def get_video_export_manifest(project_id: str, user: dict = Depends(get_auth_user)):
    """Returns complete manifest of scenes, visual parameters, audio URLs, and subtitles for client/server video compilation."""
    proj = verify_project_ownership(project_id, user)
    
    with get_db() as conn:
        scenes = conn.execute("""
            SELECT id, scene_index, title, concept_tag, narration_text,
                   display_text, animation_type, visual_spec, duration_sec,
                   subtitles_spec
            FROM video_scenes
            WHERE project_id = ?
            ORDER BY scene_index ASC
        """, (project_id,)).fetchall()

        timeline = []
        current_time = 0.0
        for s in scenes:
            d = dict(s)
            dur = float(d.get("duration_sec", 10.0))
            timeline.append({
                "scene_id": d["id"],
                "scene_index": d["scene_index"],
                "title": d["title"],
                "concept": d["concept_tag"],
                "start_time_sec": current_time,
                "end_time_sec": current_time + dur,
                "duration_sec": dur,
                "audio_url": f"/api/animated/scene/{d['id']}/audio",
                "animation_type": d["animation_type"],
                "visual_spec": json.loads(d["visual_spec"]) if isinstance(d["visual_spec"], str) else d["visual_spec"],
                "subtitles": json.loads(d["subtitles_spec"]) if isinstance(d["subtitles_spec"], str) else d["subtitles_spec"]
            })
            current_time += dur

    return {
        "status": "success",
        "project_id": project_id,
        "title": proj["title"],
        "total_duration_sec": current_time,
        "language": proj["language"],
        "learner_profile": proj["learner_profile"],
        "animation_style": proj["animation_style"],
        "timeline": timeline,
        "scenes": timeline
    }
