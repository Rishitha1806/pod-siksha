with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''    with get_db() as conn:\n        sess = conn.execute("SELECT chapter_text FROM sessions WHERE id = ?", (session_id,)).fetchone()\n        chapter_ref = sess["chapter_text"][:2000] if sess else ""'''

replacement = '''    with get_db() as conn:\n        chapter_ref = ""\n        if project_id:\n            proj = conn.execute("SELECT source_content, summary FROM video_projects WHERE id = ?", (project_id,)).fetchone()\n            if proj:\n                chapter_ref = (proj["source_content"] or proj["summary"] or "")[:2000]\n        if not chapter_ref and session_id:\n            sess = conn.execute("SELECT chapter_text FROM sessions WHERE id = ?", (session_id,)).fetchone()\n            if sess:\n                chapter_ref = (sess["chapter_text"] or "")[:2000]\n        if not chapter_ref:\n            sc = conn.execute("SELECT narration_text, learning_objective FROM video_scenes WHERE concept_tag LIKE ? LIMIT 1", (f"%{concept_tag}%",)).fetchone()\n            if sc:\n                chapter_ref = f"{sc['learning_objective']}. {sc['narration_text']}"'''

text = text.replace('\r\n', '\n')
if target in text:
    text = text.replace(target, replacement, 1)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced chapter_ref in server.py successfully!")
else:
    print("Target not found in server.py.")
