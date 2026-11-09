import ast

server_path = r"C:\Users\jvris\Downloads\pod-siksha\server.py"
with open(server_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. start_oral_quiz
text = text.replace(
    "def start_oral_quiz(payload: QuizStartRequest):",
    "def start_oral_quiz(payload: QuizStartRequest, user: dict = Depends(get_current_user)):\n    verify_session_ownership(payload.session_id, user)"
)

# 2. generate_quiz_legacy
text = text.replace(
    "def generate_quiz_legacy(payload: QuizGenerateRequest):",
    "def generate_quiz_legacy(payload: QuizGenerateRequest, user: dict = Depends(get_current_user)):\n    verify_session_ownership(payload.session_id, user)"
)

# 3. evaluate_quiz_legacy
text = text.replace(
    "def evaluate_quiz_legacy(payload: QuizEvalRequest):",
    "def evaluate_quiz_legacy(payload: QuizEvalRequest, user: dict = Depends(get_current_user)):"
)

# 4. get_teacher_recommendations
text = text.replace(
    "def get_teacher_recommendations():",
    "def get_teacher_recommendations(user: dict = Depends(require_teacher_user)):"
)

# 5. export_teacher_csv
text = text.replace(
    "def export_teacher_csv(\n    chapter: Optional[str] = None,\n    language: Optional[str] = None,\n    date_range: Optional[str] = None\n):",
    "def export_teacher_csv(\n    chapter: Optional[str] = None,\n    language: Optional[str] = None,\n    date_range: Optional[str] = None,\n    user: dict = Depends(require_teacher_user)\n):"
)
# also try single line
text = text.replace(
    "def export_teacher_csv(chapter: Optional[str] = None, language: Optional[str] = None, date_range: Optional[str] = None):",
    "def export_teacher_csv(chapter: Optional[str] = None, language: Optional[str] = None, date_range: Optional[str] = None, user: dict = Depends(require_teacher_user)):"
)

# 6. export_student_csv
text = text.replace(
    "def export_student_csv(session_id: str):",
    "def export_student_csv(session_id: str, user: dict = Depends(get_current_user)):\n    verify_session_ownership(session_id, user)"
)

# 7. get_session_transcript
text = text.replace(
    "def get_session_transcript(session_id: str):",
    "def get_session_transcript(session_id: str, user: dict = Depends(get_current_user)):\n    verify_session_ownership(session_id, user)"
)

with open(server_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Patched 7 remaining endpoints.")
