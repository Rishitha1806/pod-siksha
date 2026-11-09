with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

target = "report = get_student_study_report(session_id)"
replacement = "report = get_student_study_report(session_id, user=user)"

if target in code:
    code = code.replace(target, replacement, 1)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Successfully patched get_student_study_report(session_id, user=user).")
else:
    print("Target not found.")
