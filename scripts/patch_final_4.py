server_path = r"C:\Users\jvris\Downloads\pod-siksha\server.py"
with open(server_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. start_oral_quiz
text = text.replace(
    'def start_oral_quiz(session_id: str = Form(...), lang: Optional[str] = Form(None)):',
    '''def start_oral_quiz(session_id: str = Form(...), lang: Optional[str] = Form(None), user: dict = Depends(get_current_user)):
    sess = verify_session_ownership(session_id, user)'''
)

# 2. generate_quiz_legacy
text = text.replace(
    'def generate_quiz_legacy(session_id: str = Form(...)):',
    '''def generate_quiz_legacy(session_id: str = Form(...), user: dict = Depends(get_current_user)):
    verify_session_ownership(session_id, user)'''
)

# 3. evaluate_quiz_legacy
text = text.replace(
    '''async def evaluate_quiz_legacy(
    session_id: str = Form(...),
    question_index: int = Form(...),
    answer_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):''',
    '''async def evaluate_quiz_legacy(
    session_id: str = Form(...),
    question_index: int = Form(...),
    answer_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user)
):
    verify_session_ownership(session_id, user)'''
)

# 4. get_teacher_recommendations
text = text.replace(
    'def get_teacher_recommendations(chapter: Optional[str] = None, refresh: bool = False):',
    'def get_teacher_recommendations(chapter: Optional[str] = None, refresh: bool = False, user: dict = Depends(require_teacher_user)):'
)

with open(server_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Patched final 4 endpoints.")
