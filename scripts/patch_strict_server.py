"""
Patches server.py with:
1. Strict get_current_user (rejects missing/invalid/expired tokens with 401; rejects unverified email with 403; no fallback to demo user).
2. verify_session_ownership helper (enforces resource ownership; returns 403 on violation).
3. require_teacher_user helper (restricts teacher dashboard and exports to teacher/admin role).
4. Protected endpoint decorators on all private routes.
5. Email verification endpoints (/api/auth/verify-email, /api/auth/resend-verification).
6. Privacy Policy and Terms endpoints (/privacy, /terms).
"""

import os
import re

server_path = r"C:\Users\jvris\Downloads\pod-siksha\server.py"
with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    "from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, Header, Depends",
    "from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, Header, Depends, Cookie"
)

# 2. Update get_current_user and add ownership helpers
old_auth_block = """def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization:
        # Default fallback to demo user for backward compatibility
        with get_db() as conn:
            u = conn.execute("SELECT id, email, full_name, preferred_language, is_verified FROM users WHERE email = 'learner@demo.in'").fetchone()
            return dict(u) if u else None
    token = authorization.replace("Bearer ", "").strip()
    with get_db() as conn:
        row = conn.execute(\"\"\"
            SELECT u.id, u.email, u.full_name, u.preferred_language, u.is_verified
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > datetime('now')
        \"\"\", (token,)).fetchone()
        if row:
            return dict(row)
        u = conn.execute("SELECT id, email, full_name, preferred_language, is_verified FROM users WHERE email = 'learner@demo.in'").fetchone()
        return dict(u) if u else None"""

new_auth_block = """def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_token: Optional[str] = Cookie(None)
) -> dict:
    \"\"\"Strict Authentication Guard: Validates bearer token or session cookie.
    Rejects unauthenticated requests with HTTP 401.
    Rejects unverified email accounts with HTTP 403.
    \"\"\"
    token = None
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
        elif len(authorization.strip()) > 5:
            token = authorization.strip()
    elif auth_token:
        token = auth_token.strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in to access Pod-Siksha."
        )

    with get_db() as conn:
        row = conn.execute(\"\"\"
            SELECT u.id, u.email, u.full_name, u.preferred_language, u.is_verified, u.role
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > datetime('now')
        \"\"\", (token,)).fetchone()
        
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Session token is invalid or expired. Please sign in again."
            )
        
        user = dict(row)
        if not user.get("is_verified"):
            raise HTTPException(
                status_code=403,
                detail="Email verification required before accessing the learning application."
            )
        return user

def verify_session_ownership(session_id: str, user: dict) -> sqlite3.Row:
    \"\"\"Verifies that the requested session exists and belongs to the authenticated user (or user is teacher/admin).
    Returns 404 if session does not exist.
    Returns 403 Forbidden if the user attempts to access another learner's private session.
    \"\"\"
    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found.")
        
        # Teachers and Admins have supervisory oversight
        if user.get("role") in ("teacher", "admin"):
            return sess
        
        # If the session is tagged with a user_id, it must match current user's ID
        if sess["user_id"] and sess["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden. You do not have permission to access another learner's session.")
        
        return sess

def require_teacher_user(user: dict = Depends(get_current_user)) -> dict:
    \"\"\"Ensures that the endpoint is only accessible to users with the teacher or admin role.\"\"\"
    if user.get("role") not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Forbidden. Teacher or educator privileges required.")
    return user"""

if old_auth_block in content:
    content = content.replace(old_auth_block, new_auth_block)
    print("Replaced auth block with strict enforcement.")
else:
    print("Warning: old_auth_block did not match exactly.")

# 3. Add email verification & terms request models
req_models = """class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: str
"""
content = content.replace("class RegisterRequest(BaseModel):", req_models + "\nclass RegisterRequest(BaseModel):")

# 4. Update register_user and login_user to set cookie and handle email verification
old_reg_user = """@app.post("/api/auth/register")
def register_user(payload: RegisterRequest):
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        
        user_id = str(uuid.uuid4())
        pw_hash, salt = hash_password(payload.password)
        conn.execute(\"\"\"
            INSERT INTO users (id, email, password_hash, salt, full_name, preferred_language, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        \"\"\", (user_id, email, pw_hash, salt, payload.full_name.strip(), payload.preferred_language or "te"))
        conn.commit()
        
    token = create_user_session(user_id)
    return {
        "status": "success",
        "token": token,
        "access_token": token,
        "user": {
            "id": user_id,
            "email": email,
            "full_name": payload.full_name.strip(),
            "preferred_language": payload.preferred_language or "te"
        }
    }"""

new_reg_user = """@app.post("/api/auth/register")
def register_user(payload: RegisterRequest, response: Response):
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        
        user_id = str(uuid.uuid4())
        pw_hash, salt = hash_password(payload.password)
        verif_token = secrets.token_hex(16)
        # Check if email verification is explicitly required via env
        req_verif = os.getenv("REQUIRE_EMAIL_VERIFICATION", "false").lower() in ("true", "1", "yes")
        is_verified = 0 if req_verif else 1
        
        conn.execute(\"\"\"
            INSERT INTO users (id, email, password_hash, salt, full_name, preferred_language, is_verified, verification_token, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'student')
        \"\"\", (user_id, email, pw_hash, salt, payload.full_name.strip(), payload.preferred_language or "te", is_verified, verif_token))
        conn.commit()
        
    token = create_user_session(user_id)
    response.set_cookie(key="auth_token", value=token, httponly=True, samesite="lax", max_age=30*86400)
    return {
        "status": "success",
        "token": token,
        "access_token": token,
        "verification_token": verif_token,
        "is_verified": bool(is_verified),
        "user": {
            "id": user_id,
            "email": email,
            "full_name": payload.full_name.strip(),
            "preferred_language": payload.preferred_language or "te",
            "role": "student"
        }
    }

@app.post("/api/auth/verify-email")
def verify_email(payload: VerifyEmailRequest, response: Response):
    \"\"\"Verifies learner email address using secure verification token.\"\"\"
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE verification_token = ?", (payload.token.strip(),)).fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired email verification token.")
        conn.execute("UPDATE users SET is_verified = 1, verification_token = NULL WHERE id = ?", (user["id"],))
        conn.commit()
    
    token = create_user_session(user["id"])
    response.set_cookie(key="auth_token", value=token, httponly=True, samesite="lax", max_age=30*86400)
    return {
        "status": "success",
        "message": "Email verified successfully. Welcome to Pod-Siksha!",
        "token": token,
        "access_token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "preferred_language": user["preferred_language"],
            "role": user["role"] or "student"
        }
    }

@app.post("/api/auth/resend-verification")
def resend_verification(payload: ResendVerificationRequest):
    \"\"\"Issues a fresh verification token for unverified accounts.\"\"\"
    email = payload.email.strip().lower()
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with this email.")
        if user["is_verified"]:
            return {"status": "success", "message": "Email is already verified."}
        
        token = secrets.token_hex(16)
        conn.execute("UPDATE users SET verification_token = ? WHERE id = ?", (token, user["id"]))
        conn.commit()
    return {
        "status": "success",
        "message": "Verification code resent.",
        "verification_token": token
    }"""

content = content.replace(old_reg_user, new_reg_user)

# 5. Update login_user and logout_user to set/clear cookies and check is_verified
old_login_logout = """@app.post("/api/auth/login")
def login_user(payload: LoginRequest):
    email = payload.email.strip().lower()
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"], user["salt"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        
        token = create_user_session(user["id"])
        return {
            "status": "success",
            "token": token,
            "access_token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "preferred_language": user["preferred_language"]
            }
        }

@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        with get_db() as conn:
            conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            conn.commit()
    return {"status": "success", "message": "Logged out successfully."}"""

new_login_logout = """@app.post("/api/auth/login")
def login_user(payload: LoginRequest, response: Response):
    email = payload.email.strip().lower()
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"], user["salt"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        
        if not user["is_verified"]:
            raise HTTPException(
                status_code=403,
                detail="Email verification required before accessing the learning application. Please check your email or verify your token."
            )
        
        token = create_user_session(user["id"])
        response.set_cookie(key="auth_token", value=token, httponly=True, samesite="lax", max_age=30*86400)
        return {
            "status": "success",
            "token": token,
            "access_token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "preferred_language": user["preferred_language"],
                "role": user["role"] or "student"
            }
        }

@app.post("/api/auth/logout")
def logout_user(
    response: Response,
    authorization: Optional[str] = Header(None),
    auth_token: Optional[str] = Cookie(None)
):
    token = None
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
    elif auth_token:
        token = auth_token.strip()
    
    if token:
        with get_db() as conn:
            conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            conn.commit()
    
    response.delete_cookie("auth_token")
    return {"status": "success", "message": "Logged out successfully."}"""

content = content.replace(old_login_logout, new_login_logout)

# 6. Update get_session with ownership check
old_get_sess = """@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    \"\"\"Retrieves session script, progress, and metadata.\"\"\"
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")"""

new_get_sess = """@app.get("/api/session/{session_id}")
def get_session(session_id: str, user: dict = Depends(get_current_user)):
    \"\"\"Retrieves session script, progress, and metadata with ownership verification.\"\"\"
    row = verify_session_ownership(session_id, user)
    with get_db() as conn:"""

content = content.replace(old_get_sess, new_get_sess)

# 7. Update rename_session and delete_session with ownership check
old_rename_delete = """@app.patch("/api/session/{session_id}")
def rename_session(session_id: str, payload: SessionRenameRequest):
    with get_db() as conn:
        conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (payload.title.strip(), session_id))
        conn.commit()
    return {"status": "success", "message": "Session renamed successfully."}

@app.delete("/api/session/{session_id}")
def delete_session(session_id: str):"""

new_rename_delete = """@app.patch("/api/session/{session_id}")
def rename_session(session_id: str, payload: SessionRenameRequest, user: dict = Depends(get_current_user)):
    verify_session_ownership(session_id, user)
    with get_db() as conn:
        conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (payload.title.strip(), session_id))
        conn.commit()
    return {"status": "success", "message": "Session renamed successfully."}

@app.delete("/api/session/{session_id}")
def delete_session(session_id: str, user: dict = Depends(get_current_user)):
    verify_session_ownership(session_id, user)"""

content = content.replace(old_rename_delete, new_rename_delete)

# 8. Update get_transcript with ownership check
old_transcript = """@app.get("/api/session/{session_id}/transcript")
def get_transcript(session_id: str):
    \"\"\"Returns the transcript turns for a session.\"\"\"
    with get_db() as conn:
        row = conn.execute("SELECT script_json FROM sessions WHERE id = ?", (session_id,)).fetchone()"""

new_transcript = """@app.get("/api/session/{session_id}/transcript")
def get_transcript(session_id: str, user: dict = Depends(get_current_user)):
    \"\"\"Returns the transcript turns for a session with ownership verification.\"\"\"
    row = verify_session_ownership(session_id, user)
    with get_db() as conn:"""

content = content.replace(old_transcript, new_transcript)

# 9. Update ask_doubt with ownership check
old_ask = """@app.post("/api/ask")
async def ask_doubt(
    session_id: str = Form(...),
    turn_index: int = Form(1),
    playback_ms: int = Form(0),
    language: Optional[str] = Form("te"),
    file: UploadFile = File(...)
):"""

new_ask = """@app.post("/api/ask")
async def ask_doubt(
    session_id: str = Form(...),
    turn_index: int = Form(1),
    playback_ms: int = Form(0),
    language: Optional[str] = Form("te"),
    file: Optional[UploadFile] = File(None),
    doubt_text: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    verify_session_ownership(session_id, user)"""

content = content.replace(old_ask, new_ask)

# 10. Update get_concept_dna and get_teachback_prompt with ownership check
old_dna = """@app.get("/api/concept-dna/{session_id}")
def get_concept_dna(session_id: str):
    \"\"\"Returns interactive concept topology graph extracted from chapter knowledge.\"\"\"
    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")"""

new_dna = """@app.get("/api/concept-dna/{session_id}")
def get_concept_dna(session_id: str, user: dict = Depends(get_current_user)):
    \"\"\"Returns interactive concept topology graph with ownership verification.\"\"\"
    sess = verify_session_ownership(session_id, user)
    with get_db() as conn:"""

content = content.replace(old_dna, new_dna)

old_tb_prompt = """@app.post("/api/teachback/prompt")
def get_teachback_prompt(payload: TeachBackPromptRequest):
    \"\"\"Generates an authentic spoken Socratic prompt from Host B (Priya) asking the learner to explain a concept.\"\"\"
    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (payload.session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")"""

new_tb_prompt = """@app.post("/api/teachback/prompt")
def get_teachback_prompt(payload: TeachBackPromptRequest, user: dict = Depends(get_current_user)):
    \"\"\"Generates an authentic spoken Socratic prompt with ownership verification.\"\"\"
    sess = verify_session_ownership(payload.session_id, user)
    with get_db() as conn:"""

content = content.replace(old_tb_prompt, new_tb_prompt)

# 11. Update teacher dashboard and exports with require_teacher_user
old_dashboard = """@app.get("/api/dashboard")
def get_teacher_dashboard(
    chapter: Optional[str] = None,
    language: Optional[str] = None,
    date_range: Optional[str] = None
):"""

new_dashboard = """@app.get("/api/dashboard")
def get_teacher_dashboard(
    chapter: Optional[str] = None,
    language: Optional[str] = None,
    date_range: Optional[str] = None,
    user: dict = Depends(require_teacher_user)
):"""

content = content.replace(old_dashboard, new_dashboard)

old_recs = """@app.get("/api/teacher/recommendations")
def get_teacher_recommendations():"""

new_recs = """@app.get("/api/teacher/recommendations")
def get_teacher_recommendations(user: dict = Depends(require_teacher_user)):"""

content = content.replace(old_recs, new_recs)

old_teacher_csv = """@app.get("/api/teacher/export/csv")
def export_teacher_classroom_csv(
    chapter: Optional[str] = None,
    language: Optional[str] = None,
    date_range: Optional[str] = None
):"""

new_teacher_csv = """@app.get("/api/teacher/export/csv")
def export_teacher_classroom_csv(
    chapter: Optional[str] = None,
    language: Optional[str] = None,
    date_range: Optional[str] = None,
    user: dict = Depends(require_teacher_user)
):"""

content = content.replace(old_teacher_csv, new_teacher_csv)

# 12. Update student report and student report export with ownership check
old_student_rep = """@app.get("/api/student/{session_id}/report")
def get_student_study_report(session_id: str):
    \"\"\"Returns an individual student study report based on persistent SQLite session records.\"\"\"
    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")"""

new_student_rep = """@app.get("/api/student/{session_id}/report")
def get_student_study_report(session_id: str, user: dict = Depends(get_current_user)):
    \"\"\"Returns an individual student study report with ownership verification.\"\"\"
    sess = verify_session_ownership(session_id, user)
    with get_db() as conn:"""

content = content.replace(old_student_rep, new_student_rep)

old_student_csv = """@app.get("/api/student/{session_id}/export/csv")
def export_student_study_report_csv(session_id: str):
    \"\"\"Generates a downloadable CSV summary of a student's session study report.\"\"\"
    with get_db() as conn:
        sess = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")"""

new_student_csv = """@app.get("/api/student/{session_id}/export/csv")
def export_student_study_report_csv(session_id: str, user: dict = Depends(get_current_user)):
    \"\"\"Generates a downloadable CSV summary with ownership verification.\"\"\"
    sess = verify_session_ownership(session_id, user)
    with get_db() as conn:"""

content = content.replace(old_student_csv, new_student_csv)

# 13. Update quiz start
old_quiz_start = """@app.post("/api/quiz/start")
def start_oral_quiz(payload: QuizStartRequest):"""

new_quiz_start = """@app.post("/api/quiz/start")
def start_oral_quiz(payload: QuizStartRequest, user: dict = Depends(get_current_user)):
    verify_session_ownership(payload.session_id, user)"""

content = content.replace(old_quiz_start, new_quiz_start)

# 14. Add Privacy Policy and Terms public routes
legal_routes = """
@app.get("/privacy")
@app.get("/api/privacy")
def get_privacy_policy():
    \"\"\"Public route: Privacy Policy regarding voice data, learner isolation, and ephemeral processing.\"\"\"
    return {
        "title": "Pod-Siksha 2.0 Privacy Policy",
        "data_isolation": "Strict user-level isolation. Each learner's history, doubts, and scores are accessible only by the authenticated owner.",
        "voice_privacy": "Zero student voice audio is permanently retained on disk. All audio is processed ephemerally for STT transcription and immediately discarded.",
        "ai_processing": "Interactions are grounded strictly in uploaded educational material with Google Gemini.",
        "version": "2.0.0",
        "effective_date": "2026-11-09"
    }

@app.get("/terms")
@app.get("/api/terms")
def get_terms_and_conditions():
    \"\"\"Public route: Terms and Conditions for Pod-Siksha AI learning platform.\"\"\"
    return {
        "title": "Pod-Siksha 2.0 Terms and Conditions",
        "usage": "Educational assistance and classroom learning companion.",
        "acceptable_use": "Users must engage in academic learning, ask questions constructively, and respect intellectual property of uploaded textbook materials.",
        "version": "2.0.0",
        "effective_date": "2026-11-09"
    }
"""

if "@app.get(\"/privacy\")" not in content:
    content = content.replace('if __name__ == "__main__":', legal_routes + '\nif __name__ == "__main__":')

with open(server_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Patched {server_path} with strict access control.")
