import os
import re

file_path = os.path.join(os.path.dirname(__file__), "..", "animated_router.py")
file_path = os.path.abspath(file_path)

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update scene loop to register concept into user_concept_progress
old_code_1 = """            conn.execute(\"\"\"
                INSERT INTO video_scenes (
                    id, project_id, scene_index, title, concept_tag,
                    learning_objective, narration_text, display_text,
                    animation_type, visual_spec, duration_sec, subtitles_spec,
                    checkpoint_question
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (
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

        conn.commit()"""

new_code_1 = """            conn.execute(\"\"\"
                INSERT INTO video_scenes (
                    id, project_id, scene_index, title, concept_tag,
                    learning_objective, narration_text, display_text,
                    animation_type, visual_spec, duration_sec, subtitles_spec,
                    checkpoint_question
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (
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

            c_tag = s.get("concept_tag") or f"Concept {idx+1}"
            norm_c = re.sub(r"[^\\w\\s-]", "", c_tag.strip().lower())
            norm_c = re.sub(r"[\\s_]+", "-", norm_c)
            if norm_c:
                try:
                    conn.execute(\"\"\"
                        INSERT INTO user_concept_progress (
                            id, user_id, concept_name, normalized_tag, definition,
                            summary, status, status_reason, mastery_score,
                            times_studied, project_id, scene_id, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, 'learning', ?, 60.0, 1, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id, normalized_tag) DO UPDATE SET
                            times_studied = user_concept_progress.times_studied + 1,
                            project_id = excluded.project_id,
                            scene_id = excluded.scene_id,
                            updated_at = CURRENT_TIMESTAMP
                    \"\"\", (
                        str(uuid.uuid4()), user_id, c_tag, norm_c,
                        s.get("learning_objective", ""), s.get("title", ""),
                        f"Introduced in lesson '{final_title}' (Scene {idx+1})",
                        project_id, scene_id
                    ))
                except Exception as prog_err:
                    log.warning("Could not register user_concept_progress: %s", prog_err)

        conn.commit()"""

if old_code_1 in code:
    code = code.replace(old_code_1, new_code_1, 1)
    print("Patched scene insertion successfully.")
else:
    print("Warning: old_code_1 not found, checking if already patched.")

# 2. Update ask_scene_doubt to accept Request body (JSON or Form) + complexity & style
old_ask = """@router.post("/scene/{scene_id}/ask")
async def ask_scene_doubt(
    scene_id: str,
    doubt_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_auth_user)
):
    \"\"\"Interactive In-Video Question: Learner pauses video and asks about the current scene.\"\"\"
    from server import call_gemini, call_gnani_tts, call_gnani_stt
    
    with get_db() as conn:
        row = conn.execute(\"\"\"
            SELECT s.*, p.title as project_title, p.language as project_lang, p.user_id, p.id as project_id
            FROM video_scenes s
            JOIN video_projects p ON p.id = s.project_id
            WHERE s.id = ?
        \"\"\", (scene_id,)).fetchone()
        
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
        question = "Can you explain this visual demonstration again in simpler terms?\""""

new_ask = """@router.post("/scene/{scene_id}/ask")
async def ask_scene_doubt(
    scene_id: str,
    request: Request,
    doubt_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_auth_user)
):
    \"\"\"Interactive In-Video Question: Learner pauses video and asks about the current scene.\"\"\"
    from server import call_gemini, call_gnani_tts, call_gnani_stt
    
    with get_db() as conn:
        row = conn.execute(\"\"\"
            SELECT s.*, p.title as project_title, p.language as project_lang, p.user_id, p.id as project_id
            FROM video_scenes s
            JOIN video_projects p ON p.id = s.project_id
            WHERE s.id = ?
        \"\"\", (scene_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Scene not found.")
        scene = dict(row)
        if user.get("role") not in ("teacher", "admin") and scene["user_id"] and scene["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden.")

    # Parse question from JSON body or Form
    question = doubt_text or ""
    complexity = "intermediate"
    style = "simple"
    try:
        body = await request.json()
        if isinstance(body, dict):
            question = body.get("question") or body.get("doubt_text") or question
            complexity = body.get("complexity", complexity)
            style = body.get("explanation_style", style)
    except Exception:
        pass

    if file and file.filename:
        audio_bytes = await file.read()
        if len(audio_bytes) > 200:
            stt_res = call_gnani_stt(audio_bytes, filename="scene_doubt.wav", language=scene["project_lang"])
            question = stt_res.get("transcript", "").strip()

    if not question:
        question = "Can you explain this visual demonstration again in simpler terms?\""""

if old_ask in code:
    code = code.replace(old_ask, new_ask, 1)
    print("Patched ask_scene_doubt successfully.")
else:
    print("Warning: old_ask not found.")

# 3. Add explain_scene_again endpoint and checkpoint progress updating
checkpoint_marker = """        # Check if project_id exists in sessions table to satisfy foreign key
        sess_check = conn.execute("SELECT id FROM sessions WHERE id = ?", (project_id,)).fetchone()
        valid_sess_id = project_id if sess_check else None

        concept_event_id = str(uuid.uuid4())
        # Record concept event
        conn.execute(\"\"\"
            INSERT INTO concept_events (
                id, session_id, concept_tag, normalized_tag, event_type,
                hint_level, quiz_status, score, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            concept_event_id, valid_sess_id, concept_tag, concept_tag.lower().strip(),
            "checkpoint", 1, "correct" if is_correct else "incorrect", score, user["id"]
        ))
        conn.commit()"""

new_checkpoint_block = """        # Check if project_id exists in sessions table to satisfy foreign key
        sess_check = conn.execute("SELECT id FROM sessions WHERE id = ?", (project_id,)).fetchone()
        valid_sess_id = project_id if sess_check else None

        concept_event_id = str(uuid.uuid4())
        # Record concept event
        conn.execute(\"\"\"
            INSERT INTO concept_events (
                id, session_id, concept_tag, normalized_tag, event_type,
                hint_level, quiz_status, score, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            concept_event_id, valid_sess_id, concept_tag, concept_tag.lower().strip(),
            "checkpoint", 1, "correct" if is_correct else "incorrect", score, user["id"]
        ))

        # Update genuine user_concept_progress
        norm_tag = re.sub(r"[^\\w\\s-]", "", concept_tag.strip().lower())
        norm_tag = re.sub(r"[\\s_]+", "-", norm_tag)
        new_status = "understood" if is_correct else "needs_revision"
        status_reason = f"Mastered in Checkpoint Quiz on Scene {row['scene_index'] if 'scene_index' in row else ''} (Score: 100%)" if is_correct else "Incorrect answer in Checkpoint Quiz - flagged for revision"
        new_score = 100.0 if is_correct else 35.0

        try:
            conn.execute(\"\"\"
                INSERT INTO user_concept_progress (
                    id, user_id, concept_name, normalized_tag, status, status_reason,
                    mastery_score, times_quizzed, times_correct, project_id, scene_id, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, normalized_tag) DO UPDATE SET
                    status = excluded.status,
                    status_reason = excluded.status_reason,
                    mastery_score = excluded.mastery_score,
                    times_quizzed = user_concept_progress.times_quizzed + 1,
                    times_correct = user_concept_progress.times_correct + excluded.times_correct,
                    updated_at = CURRENT_TIMESTAMP
            \"\"\", (
                str(uuid.uuid4()), user["id"], concept_tag, norm_tag, new_status,
                status_reason, new_score, 1 if is_correct else 0, project_id, payload.scene_id
            ))
            if not is_correct:
                conn.execute(\"\"\"
                    INSERT INTO memory_loop (id, user_id, concept_tag, session_id, due_at, status)
                    VALUES (?, ?, ?, ?, datetime('now', '+24 hours'), 'queued')
                \"\"\", (str(uuid.uuid4()), user["id"], concept_tag, project_id))
        except Exception as prog_e:
            log.warning("Could not update concept progress from checkpoint: %s", prog_e)

        conn.commit()"""

if checkpoint_marker in code:
    code = code.replace(checkpoint_marker, new_checkpoint_block, 1)
    print("Patched checkpoint progress tracking successfully.")

# Add Explain It Again endpoint before export manifest
explain_again_endpoint = """
@router.post("/scene/{scene_id}/explain-again")
async def explain_scene_again(
    scene_id: str,
    request: Request,
    user: dict = Depends(get_auth_user)
):
    \"\"\"Generates an alternative AI explanation for the active animated scene.\"\"\"
    from server import call_gemini, call_gnani_tts

    with get_db() as conn:
        row = conn.execute(\"\"\"
            SELECT s.*, p.title as project_title, p.language as project_lang, p.user_id, p.id as project_id
            FROM video_scenes s
            JOIN video_projects p ON p.id = s.project_id
            WHERE s.id = ?
        \"\"\", (scene_id,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Scene not found.")
        scene = dict(row)

    payload = {}
    try:
        payload = await request.json()
    except Exception:
        pass

    mode = payload.get("mode", "simpler")  # 'simpler', 'step_by_step', 'analogy', 'real_world', 'visual_focus'
    complexity = payload.get("complexity", "intermediate")  # 'beginner', 'intermediate', 'advanced'
    lang = payload.get("language") or scene["project_lang"] or "en"

    mode_prompts = {
        "simpler": "Explain this scene's concept in crystal-clear, highly simplified terms avoiding any confusing jargon.",
        "step_by_step": "Break down this scene's mechanism into 3 sequential numbered cause-and-effect steps.",
        "analogy": "Provide a memorable real-world analogy comparing this scene's concept to everyday experiences.",
        "real_world": "Explain a direct real-world engineering, biological, or practical application of this concept.",
        "visual_focus": "Explain how the visual shapes, motions, and colors on the canvas represent the underlying mechanics."
    }
    instruction = mode_prompts.get(mode, mode_prompts["simpler"])

    prompt = f\"\"\"You are the master AI educator in Pod-Siksha 3.0.
A learner watching an animated video lesson requested an alternative explanation for this specific scene.

SCENE CONTEXT:
- Lesson Title: {scene['project_title']}
- Scene Title: {scene['title']}
- Concept: {scene['concept_tag']}
- Narration: {scene['narration_text']}
- Visual Type: {scene['animation_type']}

REQUESTED EXPLANATION MODE:
{mode.upper()}: {instruction}

TARGET COMPLEXITY: {complexity.upper()}
LANGUAGE: {lang}

Return ONLY valid JSON:
{{
  "mode": "{mode}",
  "explanation_text": "2-3 paragraphs of high-quality educational explanation in {lang}",
  "key_takeaway": "Single-sentence core insight",
  "visual_cue": "Visual instruction of what to look for on the canvas"
}}
\"\"\"
    raw = call_gemini(prompt, json_mode=True)
    try:
        clean = re.sub(r"^```(?:json)?\\s*", "", raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r"\\s*```$", "", clean, flags=re.MULTILINE)
        data = json.loads(clean)
    except Exception as e:
        data = {
            "mode": mode,
            "explanation_text": f"Understanding {scene['concept_tag']}: {instruction}",
            "key_takeaway": f"Core mechanism of {scene['concept_tag']}",
            "visual_cue": "Observe the animated elements transitioning across the stage."
        }

    return {
        "status": "success",
        "scene_id": scene_id,
        "concept_tag": scene["concept_tag"],
        "mode": mode,
        "complexity": complexity,
        "explanation": data.get("explanation_text"),
        "key_takeaway": data.get("key_takeaway"),
        "visual_cue": data.get("visual_cue")
    }
"""

if "/explain-again" not in code:
    code = code.replace('@router.get("/project/{project_id}/export/manifest")', explain_again_endpoint + '\n@router.get("/project/{project_id}/export/manifest")')
    print("Added explain_scene_again endpoint.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)
print("Finished patching animated_router.py successfully.")
