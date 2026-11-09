import re

server_path = r"C:\Users\jvris\Downloads\pod-siksha\server.py"
with open(server_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update GET /api/tts
text = re.sub(
    r'@app\.get\("/api/tts"\)\s*def get_tts_audio\(\s*session_id: Optional\[str\] = None,\s*turn_index: Optional\[int\] = 1,\s*text: Optional\[str\] = None,\s*language: Optional\[str\] = "te",\s*speaker: Optional\[str\] = "A"\s*\):',
    '''@app.get("/api/tts")
def get_tts_audio(
    session_id: Optional[str] = None,
    turn_index: Optional[int] = 1,
    text: Optional[str] = None,
    language: Optional[str] = "te",
    speaker: Optional[str] = "A",
    user: dict = Depends(get_current_user)
):
    if session_id:
        verify_session_ownership(session_id, user)''',
    text
)

# 2. Update POST /api/tts
text = re.sub(
    r'@app\.post\("/api/tts"\)\s*def synthesize_tts\(payload: TTSRequest\):',
    '''@app.post("/api/tts")
def synthesize_tts(payload: TTSRequest, user: dict = Depends(get_current_user)):''',
    text
)

# 3. Update /api/audio/doubt/{audio_id}
text = re.sub(
    r'@app\.get\("/api/audio/doubt/\{audio_id\}"\)\s*def get_doubt_audio\(audio_id: str\):',
    '''@app.get("/api/audio/doubt/{audio_id}")
def get_doubt_audio(audio_id: str, user: dict = Depends(get_current_user)):''',
    text
)

# 4. Update /api/quiz/question/audio/{question_id}
text = re.sub(
    r'@app\.get\("/api/quiz/question/audio/\{question_id\}"\)\s*def get_question_audio\(question_id: str\):',
    '''@app.get("/api/quiz/question/audio/{question_id}")
def get_question_audio(question_id: str, user: dict = Depends(get_current_user)):''',
    text
)

# 5. Update /api/quiz/answer
text = re.sub(
    r'@app\.post\("/api/quiz/answer"\)\s*async def submit_quiz_answer\(',
    '''@app.post("/api/quiz/answer")
async def submit_quiz_answer(user: dict = Depends(get_current_user), ''',
    text
)

# 6. Update /api/quiz/{quiz_id}/results
text = re.sub(
    r'@app\.get\("/api/quiz/\{quiz_id\}/results"\)\s*def get_quiz_results\(quiz_id: str\):',
    '''@app.get("/api/quiz/{quiz_id}/results")
def get_quiz_results(quiz_id: str, user: dict = Depends(get_current_user)):''',
    text
)

# 7. Update /api/quiz/generate
text = re.sub(
    r'@app\.post\("/api/quiz/generate"\)\s*def generate_quiz\(payload: QuizGenerateRequest\):',
    '''@app.post("/api/quiz/generate")
def generate_quiz(payload: QuizGenerateRequest, user: dict = Depends(get_current_user)):''',
    text
)

# 8. Update /api/quiz/evaluate
text = re.sub(
    r'@app\.post\("/api/quiz/evaluate"\)\s*def evaluate_quiz\(payload: QuizEvaluateRequest\):',
    '''@app.post("/api/quiz/evaluate")
def evaluate_quiz(payload: QuizEvaluateRequest, user: dict = Depends(get_current_user)):''',
    text
)

# 9. Update /api/audio/quiz/{audio_id}
text = re.sub(
    r'@app\.get\("/api/audio/quiz/\{audio_id\}"\)\s*def get_quiz_audio\(audio_id: str\):',
    '''@app.get("/api/audio/quiz/{audio_id}")
def get_quiz_audio(audio_id: str, user: dict = Depends(get_current_user)):''',
    text
)

# 10. Update HTML routes /teacher and /report
text = re.sub(
    r'@app\.get\("/teacher"\)\s*def serve_teacher\(\):',
    '''@app.get("/teacher")
def serve_teacher(user: dict = Depends(require_teacher_user)):''',
    text
)

text = re.sub(
    r'@app\.get\("/report"\)\s*def serve_report\(\):',
    '''@app.get("/report")
def serve_report(user: dict = Depends(get_current_user)):''',
    text
)

with open(server_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Applied strict auth guards to all remaining endpoints.")
