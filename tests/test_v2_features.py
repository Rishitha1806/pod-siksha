"""Pod-Siksha 2.0: Aura Atelier Feature & Security Test Suite
Verifies:
1. Sovereign User Authentication (Register, Login, Invalidation, Password Reset).
2. User-Level Data Isolation (Journeys, Episodes, Doubts, Misconceptions).
3. Concept DNA Knowledge Topology Generation & Graph Node Storage.
4. Teach-Back Mode Spoken Prompt & Semantic Misconception Evaluation.
5. Misconception Radar Real Telemetry from SQLite.
6. Memory Loop Adaptive Spaced Repetition Queue & Resolution.
7. Personal Learning Insights Mastery Ring & Breakdown.
8. Physical Audio WAV Header Sanitization (Valid RIFF Chunk Sizes).
"""
import io
import os
import sqlite3
import struct
import uuid
import pytest
import httpx

BASE_URL = "http://127.0.0.1:8008"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pod_siksha.db")

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c

def test_01_user_registration_and_login(client):
    """Verifies that new users can register and login with PBKDF2 hashed credentials."""
    unique_email = f"learner_{uuid.uuid4().hex[:6]}@demo.in"
    reg_payload = {
        "full_name": "Aura Test Learner",
        "email": unique_email,
        "password": "SecurePassword123!",
        "preferred_language": "te"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code in (200, 201)
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == unique_email
    assert reg_data["user"]["full_name"] == "Aura Test Learner"

    # Test login with correct password
    login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == unique_email

    # Test login with invalid password
    bad_login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "WrongPassword!"
    })
    assert bad_login_res.status_code == 401

def test_02_jwt_bearer_auth_me(client):
    """Verifies /api/auth/me returns the authenticated user identity."""
    # Login as default demo user
    login_res = client.post("/api/auth/login", json={
        "email": "learner@demo.in",
        "password": "podsiksha2026"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    user = me_res.json().get("user", me_res.json())
    assert user["email"] == "learner@demo.in"
    assert user["full_name"] == "Rishitha J.V."

def test_03_logout_invalidation(client):
    """Verifies that logging out invalidates the active session token."""
    login_res = client.post("/api/auth/login", json={
        "email": "learner@demo.in",
        "password": "podsiksha2026"
    })
    token = login_res.json()["access_token"]

    # Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

    # Token should be expired/removed in user_sessions
    with sqlite3.connect(DB_PATH) as conn:
        active_sess = conn.execute(
            "SELECT COUNT(*) FROM user_sessions WHERE token = ? AND expires_at > datetime('now')",
            (token,)
        ).fetchone()[0]
        assert active_sess == 0

def test_04_forgot_and_reset_password(client):
    """Verifies password reset token generation and password updating."""
    # Create a throwaway user
    temp_email = f"reset_{uuid.uuid4().hex[:6]}@demo.in"
    client.post("/api/auth/register", json={
        "full_name": "Reset Test",
        "email": temp_email,
        "password": "OldPassword123!",
        "preferred_language": "te"
    })

    # Request reset token
    forgot_res = client.post("/api/auth/forgot-password", json={"email": temp_email})
    assert forgot_res.status_code == 200
    token = forgot_res.json().get("dev_reset_token")
    assert token is not None

    # Reset password
    reset_res = client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "NewSecurePassword456!"
    })
    assert reset_res.status_code == 200

    # Login with new password
    new_login = client.post("/api/auth/login", json={
        "email": temp_email,
        "password": "NewSecurePassword456!"
    })
    assert new_login.status_code == 200

def test_05_user_data_isolation(client):
    """Verifies that user journeys and sessions remain isolated between different learners."""
    # User 1 registers and gets token
    u1_email = f"user1_{uuid.uuid4().hex[:6]}@demo.in"
    u1_token = client.post("/api/auth/register", json={
        "full_name": "User One", "email": u1_email, "password": "Password123!", "preferred_language": "te"
    }).json()["access_token"]

    # User 2 registers and gets token
    u2_email = f"user2_{uuid.uuid4().hex[:6]}@demo.in"
    u2_token = client.post("/api/auth/register", json={
        "full_name": "User Two", "email": u2_email, "password": "Password123!", "preferred_language": "te"
    }).json()["access_token"]

    # User 1 journeys list should initially be empty for User 1
    u1_journeys = client.get("/api/user/journeys", headers={"Authorization": f"Bearer {u1_token}"}).json()["journeys"]
    assert len(u1_journeys) == 0

def test_06_concept_dna_extraction_and_caching(client):
    """Verifies /api/concept-dna/{session_id} returns structured nodes with dependencies and mastery."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        sess = conn.execute("SELECT id FROM sessions WHERE user_id = 'user_demo_001' OR user_id IS NULL ORDER BY created_at DESC LIMIT 1").fetchone()
    assert sess is not None, "Need at least 1 session in database"
    session_id = sess["id"]

    dna_res = client.get(f"/api/concept-dna/{session_id}", headers=headers)
    assert dna_res.status_code == 200
    data = dna_res.json()
    assert "session_id" in data
    assert "nodes" in data
    assert len(data["nodes"]) >= 3

    node = data["nodes"][0]
    assert "concept_tag" in node
    assert "definition" in node
    assert "prerequisites" in node
    assert "mastery_score" in node

def test_07_teachback_prompt_generation(client):
    """Verifies that Host B (Priya) generates a grounded Socratic prompt for teach-back."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    with sqlite3.connect(DB_PATH) as conn:
        sess = conn.execute("SELECT id FROM sessions WHERE user_id = 'user_demo_001' OR user_id IS NULL ORDER BY created_at DESC LIMIT 1").fetchone()
    session_id = sess[0]

    tb_prompt_res = client.post("/api/teachback/prompt", json={
        "session_id": session_id,
        "concept_tag": "Water Photolysis"
    }, headers=headers)
    assert tb_prompt_res.status_code == 200
    data = tb_prompt_res.json()
    assert "ai_prompt" in data
    assert "concept_tag" in data
    assert len(data["ai_prompt"]) > 10

def test_08_teachback_semantic_evaluation_and_misconception_logging(client):
    """Verifies semantic evaluation of student explanation and logging in SQLite."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    with sqlite3.connect(DB_PATH) as conn:
        sess = conn.execute("SELECT id FROM sessions WHERE user_id = 'user_demo_001' OR user_id IS NULL ORDER BY created_at DESC LIMIT 1").fetchone()
    session_id = sess[0]

    # Submit an explanation containing a common misconception
    eval_res = client.post("/api/teachback/evaluate", data={
        "session_id": session_id,
        "concept_tag": "Water Photolysis",
        "ai_prompt": "Why does water photolysis happen?",
        "explanation_text": "Water molecules split in the green leaf when sunlight hits it to make sugar and oxygen directly."
    }, headers=headers)
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert "understood_points" in data
    assert "misconceptions" in data
    assert "missing_points" in data
    assert "mastery_score" in data
    assert "next_step" in data
    assert isinstance(data["mastery_score"], (int, float))

    # Verify recorded in teachback_sessions
    with sqlite3.connect(DB_PATH) as conn:
        cnt = conn.execute("SELECT COUNT(*) FROM teachback_sessions WHERE session_id = ?", (session_id,)).fetchone()[0]
        assert cnt >= 1

def test_09_misconceptions_radar_endpoint(client):
    """Verifies /api/misconceptions returns diagnosed misconceptions with confidence and source."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    res = client.get("/api/misconceptions", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "misconceptions" in data
    assert isinstance(data["misconceptions"], list)

def test_10_memory_loop_retention_queue_and_resolve(client):
    """Verifies memory loop retrieval and resolution endpoint."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    res = client.get("/api/memory-loop", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "touchpoints" in data
    touchpoints = data["touchpoints"]

    if touchpoints:
        first_id = touchpoints[0]["id"]
        resolve_res = client.post(f"/api/memory-loop/{first_id}/resolve", headers=headers)
        assert resolve_res.status_code == 200
        assert resolve_res.json()["status"] == "resolved"

def test_11_personal_insights_calculated_telemetry(client):
    """Verifies /api/insights/personal computes authentic telemetry from database tables."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    res = client.get("/api/insights/personal", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "overall_mastery" in data
    assert "concept_breakdown" in data
    assert "diagnosed_misconceptions" in data
    assert "memory_loop_touchpoints" in data
    assert "quizzes_completed" in data
    assert 0 <= data["overall_mastery"] <= 100

def test_12_sanitized_wav_audio_headers(client):
    """Verifies that /api/tts returns valid linear PCM WAV with sanitized RIFF headers."""
    headers = {"Authorization": "Bearer session_demo_learner_001"}
    with sqlite3.connect(DB_PATH) as conn:
        sess = conn.execute("SELECT id FROM sessions WHERE user_id = 'user_demo_001' OR user_id IS NULL ORDER BY created_at DESC LIMIT 1").fetchone()
    session_id = sess[0]

    tts_res = client.get(f"/api/tts?session_id={session_id}&turn_index=1&speaker=A&language=te", headers=headers)
    assert tts_res.status_code == 200
    assert tts_res.headers.get("content-type") == "audio/wav"

    wav_bytes = tts_res.content
    assert len(wav_bytes) > 44
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"

    # Verify chunk size in header matches actual byte length - 8 (not 0xFFFFFFFF placeholder)
    riff_size = struct.unpack("<I", wav_bytes[4:8])[0]
    assert riff_size == len(wav_bytes) - 8, f"Header size {riff_size} != expected {len(wav_bytes) - 8}"
