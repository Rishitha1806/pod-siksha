import os
import re

file_path = os.path.join(os.path.dirname(__file__), "..", "server.py")
file_path = os.path.abspath(file_path)

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_block = """    with get_db() as conn:
        sess = conn.execute("SELECT chapter_text FROM sessions WHERE id = ?", (session_id,)).fetchone()
        chapter_ref = sess["chapter_text"][:2000] if sess else \"\"\""""

new_block = """    with get_db() as conn:
        chapter_ref = ""
        if project_id:
            proj = conn.execute("SELECT source_content, summary FROM video_projects WHERE id = ?", (project_id,)).fetchone()
            if proj:
                chapter_ref = (proj["source_content"] or proj["summary"] or "")[:2000]
        if not chapter_ref and session_id:
            sess = conn.execute("SELECT chapter_text FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if sess:
                chapter_ref = (sess["chapter_text"] or "")[:2000]
        if not chapter_ref:
            # Check video_scenes
            sc = conn.execute("SELECT narration_text, learning_objective FROM video_scenes WHERE concept_tag LIKE ? LIMIT 1", (f"%{concept_tag}%",)).fetchone()
            if sc:
                chapter_ref = f"{sc['learning_objective']}. {sc['narration_text']}"
"""

if old_block in code:
    code = code.replace(old_block, new_block, 1)
    print("Patched chapter_ref lookup in evaluate_teachback.")
else:
    print("Warning: old_block not found.")

# Update teachback status persistence into user_concept_progress
old_ev_id = """        # Record in concept_events
        ev_id = str(uuid.uuid4())"""

new_ev_id = """        # Update genuine user_concept_progress
        norm_tag = normalize_concept(concept_tag)
        new_status = "understood" if score >= 75 and not eval_data.get("misconceptions") else "needs_revision"
        status_reason = f"Demonstrated in Teach-Back with {score}% score" if new_status == "understood" else f"Diagnosed in Teach-Back: {eval_data.get('misconceptions', ['Needs clarification'])[0]}"
        try:
            conn.execute(\"\"\"
                INSERT INTO user_concept_progress (
                    id, user_id, concept_name, normalized_tag, status, status_reason,
                    mastery_score, times_studied, project_id, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, normalized_tag) DO UPDATE SET
                    status = excluded.status,
                    status_reason = excluded.status_reason,
                    mastery_score = excluded.mastery_score,
                    updated_at = CURRENT_TIMESTAMP
            \"\"\", (str(uuid.uuid4()), uid, concept_tag, norm_tag, new_status, status_reason, score, project_id or session_id))
        except Exception as prog_e:
            log.warning("Could not update user_concept_progress from teachback: %s", prog_e)

        # Record in concept_events
        ev_id = str(uuid.uuid4())"""

if old_ev_id in code:
    code = code.replace(old_ev_id, new_ev_id, 1)
    print("Patched user_concept_progress update in evaluate_teachback.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)
print("Finished patching teachback in server.py.")
