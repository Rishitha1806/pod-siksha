"""
Patches animated_router.py:
1. Fixes checkpoint foreign key by setting session_id = valid_sess_id (or None), returns ok: True.
2. In export manifest, returns both timeline and scenes keys.
"""

ROUTER_PATH = r"C:\Users\jvris\Downloads\pod-siksha\animated_router.py"

with open(ROUTER_PATH, "r", encoding="utf-8") as f:
    text = f.read()

OLD_CHECKPOINT = """        # Record concept event
        conn.execute(\"\"\"
            INSERT INTO concept_events (
                id, session_id, concept_tag, normalized_tag, event_type,
                hint_level, quiz_status, score, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            str(uuid.uuid4()), project_id, concept_tag, concept_tag.lower().strip(),
            "checkpoint", 1, "correct" if is_correct else "incorrect", score, user["id"]
        ))
        conn.commit()

    return {
        "status": "success",
        "is_correct": is_correct,
        "correct_index": correct_idx,
        "explanation": chk.get("explanation", "Good job engaging with the lesson visual concept!"),
        "score": score
    }"""

NEW_CHECKPOINT = """        # Check if project_id exists in sessions table to satisfy foreign key
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
        conn.commit()

    return {
        "status": "success",
        "ok": True,
        "concept_id": concept_event_id,
        "is_correct": is_correct,
        "correct_index": correct_idx,
        "explanation": chk.get("explanation", "Good job engaging with the lesson visual concept!"),
        "score": score
    }"""

text = text.replace(OLD_CHECKPOINT, NEW_CHECKPOINT)

OLD_MANIFEST_RETURN = """    return {
        "status": "success",
        "project_id": project_id,
        "title": proj["title"],
        "total_duration_sec": current_time,
        "language": proj["language"],
        "learner_profile": proj["learner_profile"],
        "animation_style": proj["animation_style"],
        "timeline": timeline
    }"""

NEW_MANIFEST_RETURN = """    return {
        "status": "success",
        "project_id": project_id,
        "title": proj["title"],
        "total_duration_sec": current_time,
        "language": proj["language"],
        "learner_profile": proj["learner_profile"],
        "animation_style": proj["animation_style"],
        "timeline": timeline,
        "scenes": timeline
    }"""

text = text.replace(OLD_MANIFEST_RETURN, NEW_MANIFEST_RETURN)

with open(ROUTER_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("animated_router.py checkpoint and manifest updated successfully!")
