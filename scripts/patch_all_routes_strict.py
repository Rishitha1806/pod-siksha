import re

server_path = r"C:\Users\jvris\Downloads\pod-siksha\server.py"
with open(server_path, "r", encoding="utf-8") as f:
    text = f.read()

public_routes = [
    "/",
    "/prototype",
    "/redesign",
    "/privacy",
    "/api/privacy",
    "/terms",
    "/api/terms",
    "/api/health",
    "/api/auth/register",
    "/api/auth/verify-email",
    "/api/auth/resend-verification",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
]

# Specifically ensure:
# 1. get_quiz_question_audio has user: dict = Depends(get_current_user)
text = text.replace(
    "def get_quiz_question_audio(question_id: str):",
    "def get_quiz_question_audio(question_id: str, user: dict = Depends(get_current_user)):"
)

# 2. memory loop resolve
text = text.replace(
    "def resolve_memory_loop(item_id: str, payload: Optional[MemoryLoopResolveRequest] = None):",
    "def resolve_memory_loop(item_id: str, payload: Optional[MemoryLoopResolveRequest] = None, user: dict = Depends(get_current_user)):"
)

# 3. teacher recommendations
text = text.replace(
    "def get_teacher_recommendations():",
    "def get_teacher_recommendations(user: dict = Depends(require_teacher_user)):"
)

# 4. teacher export csv
text = text.replace(
    "def export_teacher_classroom_csv(\n    chapter: Optional[str] = None,\n    language: Optional[str] = None,\n    date_range: Optional[str] = None\n):",
    "def export_teacher_classroom_csv(\n    chapter: Optional[str] = None,\n    language: Optional[str] = None,\n    date_range: Optional[str] = None,\n    user: dict = Depends(require_teacher_user)\n):"
)

# 5. student export csv
text = text.replace(
    "def export_student_study_report_csv(session_id: str):",
    "def export_student_study_report_csv(session_id: str, user: dict = Depends(get_current_user)):\n    verify_session_ownership(session_id, user)"
)

# 6. session transcript
text = text.replace(
    "def get_transcript(session_id: str):",
    "def get_transcript(session_id: str, user: dict = Depends(get_current_user)):\n    verify_session_ownership(session_id, user)"
)

# 7. doubt audio
text = text.replace(
    "def get_doubt_audio(audio_id: str):",
    "def get_doubt_audio(audio_id: str, user: dict = Depends(get_current_user)):"
)

# 8. quiz answer
text = text.replace(
    "async def submit_quiz_answer(\n    quiz_session_id: str = Form(...),",
    "async def submit_quiz_answer(\n    quiz_session_id: str = Form(...),\n    user: dict = Depends(get_current_user),"
)

# 9. quiz results
text = text.replace(
    "def get_quiz_results(quiz_id: str):",
    "def get_quiz_results(quiz_id: str, user: dict = Depends(get_current_user)):"
)

# 10. quiz audio
text = text.replace(
    "def get_quiz_audio(audio_id: str):",
    "def get_quiz_audio(audio_id: str, user: dict = Depends(get_current_user)):"
)

# 11. HTML /teacher and /report routes
text = text.replace(
    "def serve_teacher():",
    "def serve_teacher(user: dict = Depends(require_teacher_user)):"
)
text = text.replace(
    "def serve_report():",
    "def serve_report(user: dict = Depends(get_current_user)):"
)

with open(server_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Applied exact replacements for remaining protected endpoints.")
