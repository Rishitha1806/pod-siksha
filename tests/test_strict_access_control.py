import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_adapter import get_db
"""
Strict Authentication & Access Control Verification Test Suite for Pod-Siksha 2.0.
Verifies server-side rejection of unauthenticated, unverified, and unauthorized requests.
"""

import os
import sys
import pytest
import sqlite3
import uuid

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.testclient import TestClient
from server import app, DB_PATH

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def setup_test_users():
    """Create test fixtures for learner, teacher, and an unverified user in SQLite."""
    conn = get_db()
    cur = conn.cursor()

    # User A: Verified Learner
    cur.execute("""
        INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, is_verified, role, verification_token)
        VALUES ('user_audit_learner_a', 'learner_a@audit.in', 'hash_a', 'salt_a', 'Learner A', 1, 'student', 'token_a')
    """)
    cur.execute("""
        INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
        VALUES ('session_audit_learner_a', 'user_audit_learner_a', datetime('now', '+7 days'))
    """)

    # User B: Another Verified Learner
    cur.execute("""
        INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, is_verified, role, verification_token)
        VALUES ('user_audit_learner_b', 'learner_b@audit.in', 'hash_b', 'salt_b', 'Learner B', 1, 'student', 'token_b')
    """)
    cur.execute("""
        INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
        VALUES ('session_audit_learner_b', 'user_audit_learner_b', datetime('now', '+7 days'))
    """)

    # Session belonging to User B
    cur.execute("""
        INSERT OR REPLACE INTO sessions (id, user_id, title, chapter_text, language, script_json)
        VALUES ('sess_audit_b_001', 'user_audit_learner_b', 'Photosynthesis', 'Sample biology chapter text.', 'te', '[]')
    """)

    # User C: Unverified User
    cur.execute("""
        INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, is_verified, role, verification_token)
        VALUES ('user_audit_unverified', 'unverified@audit.in', 'hash_u', 'salt_u', 'Unverified Student', 0, 'student', 'audit_verify_token_123')
    """)
    cur.execute("""
        INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
        VALUES ('session_audit_unverified', 'user_audit_unverified', datetime('now', '+7 days'))
    """)

    # User D: Teacher
    cur.execute("""
        INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, is_verified, role, verification_token)
        VALUES ('user_audit_teacher', 'teacher@audit.in', 'hash_t', 'salt_t', 'Dr. Teacher', 1, 'teacher', 'token_t')
    """)
    cur.execute("""
        INSERT OR REPLACE INTO user_sessions (token, user_id, expires_at)
        VALUES ('session_audit_teacher', 'user_audit_teacher', datetime('now', '+7 days'))
    """)

    conn.commit()
    conn.close()

    yield

    # Clean up test records
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_sessions WHERE token LIKE 'session_audit_%'")
    cur.execute("DELETE FROM sessions WHERE id = 'sess_audit_b_001'")
    cur.execute("DELETE FROM users WHERE id LIKE 'user_audit_%'")
    conn.commit()
    conn.close()


# -------------------------------------------------------------
# 1. PUBLIC ENDPOINTS ALLOWED WITHOUT AUTH
# -------------------------------------------------------------

def test_public_root_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]

def test_public_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_public_privacy_pages(client):
    res_page = client.get("/privacy")
    assert res_page.status_code == 200
    res_json = client.get("/api/privacy")
    assert res_json.status_code == 200
    assert "voice_privacy" in res_json.json()

def test_public_terms_pages(client):
    res_page = client.get("/terms")
    assert res_page.status_code == 200
    res_json = client.get("/api/terms")
    assert res_json.status_code == 200
    assert "acceptable_use" in res_json.json()

def test_public_auth_routes(client):
    res = client.post("/api/auth/forgot-password", json={"email": "nonexistent_email_12345@domain.com"})
    assert res.status_code == 200


# -------------------------------------------------------------
# 2. PROTECTED ENDPOINTS RETURN 401 WITHOUT AUTH
# -------------------------------------------------------------

def test_unauthenticated_user_journeys_rejected(client):
    res = client.get("/api/user/journeys")
    assert res.status_code == 401
    assert "Authentication required" in res.json()["detail"]

def test_unauthenticated_session_creation_rejected(client):
    res = client.post("/api/session", json={"chapter_title": "Gravity", "content": "Sample content"})
    assert res.status_code == 401

def test_unauthenticated_session_detail_rejected(client):
    res = client.get("/api/session/sess_dummy_id")
    assert res.status_code == 401

def test_unauthenticated_session_patch_rejected(client):
    res = client.patch("/api/session/sess_dummy_id", json={"title": "New Title"})
    assert res.status_code == 401

def test_unauthenticated_session_delete_rejected(client):
    res = client.delete("/api/session/sess_dummy_id")
    assert res.status_code == 401

def test_unauthenticated_ask_doubt_rejected(client):
    res = client.post("/api/ask", data={"session_id": "sess_dummy_id", "text": "What is gravity?"})
    assert res.status_code == 401

def test_unauthenticated_tts_post_rejected(client):
    res = client.post("/api/tts", json={"text": "Hello world", "speaker": "A", "language": "en"})
    assert res.status_code == 401

def test_unauthenticated_tts_get_rejected(client):
    res = client.get("/api/tts?text=Hello+world&speaker=A&language=en")
    assert res.status_code == 401

def test_unauthenticated_quiz_start_rejected(client):
    res = client.post("/api/quiz/start", json={"session_id": "sess_dummy_id"})
    assert res.status_code == 401

def test_unauthenticated_concept_dna_rejected(client):
    res = client.get("/api/concept-dna/sess_dummy_id")
    assert res.status_code == 401

def test_unauthenticated_teachback_prompt_rejected(client):
    res = client.post("/api/teachback/prompt", json={"session_id": "sess_dummy_id", "concept_tag": "Chlorophyll"})
    assert res.status_code == 401

def test_unauthenticated_teachback_evaluate_rejected(client):
    res = client.post("/api/teachback/evaluate", json={"session_id": "sess_dummy_id", "concept_name": "Photosynthesis", "explanation": "It makes food"})
    assert res.status_code == 401

def test_unauthenticated_misconceptions_rejected(client):
    res = client.get("/api/misconceptions")
    assert res.status_code == 401

def test_unauthenticated_memory_loop_rejected(client):
    res = client.get("/api/memory-loop")
    assert res.status_code == 401

def test_unauthenticated_personal_insights_rejected(client):
    res = client.get("/api/insights/personal")
    assert res.status_code == 401

def test_unauthenticated_dashboard_rejected(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 401

def test_unauthenticated_teacher_recommendations_rejected(client):
    res = client.get("/api/teacher/recommendations")
    assert res.status_code == 401

def test_unauthenticated_teacher_export_rejected(client):
    res = client.get("/api/teacher/export/csv")
    assert res.status_code == 401


# -------------------------------------------------------------
# 3. ROLE-BASED ACCESS CONTROL (STUDENT VS TEACHER)
# -------------------------------------------------------------

def test_student_cannot_access_teacher_dashboard(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}
    res = client.get("/api/dashboard", headers=headers)
    assert res.status_code == 403
    assert "Teacher" in res.json()["detail"] or "educator" in res.json()["detail"]

def test_student_cannot_access_teacher_recommendations(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}
    res = client.get("/api/teacher/recommendations", headers=headers)
    assert res.status_code == 403

def test_student_cannot_export_teacher_csv(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}
    res = client.get("/api/teacher/export/csv", headers=headers)
    assert res.status_code == 403

def test_teacher_can_access_teacher_dashboard(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_teacher"}
    res = client.get("/api/dashboard", headers=headers)
    assert res.status_code == 200
    assert "summary" in res.json()


# -------------------------------------------------------------
# 4. RESOURCE OWNERSHIP ENFORCEMENT
# -------------------------------------------------------------

def test_learner_a_cannot_access_learner_b_session(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}
    res = client.get("/api/session/sess_audit_b_001", headers=headers)
    assert res.status_code == 403
    assert "permission" in res.json()["detail"]

def test_learner_a_cannot_modify_learner_b_session(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}
    res = client.patch("/api/session/sess_audit_b_001", json={"title": "Unauthorized Rename"}, headers=headers)
    assert res.status_code == 403
    assert "permission" in res.json()["detail"]

def test_learner_a_cannot_delete_learner_b_session(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}
    res = client.delete("/api/session/sess_audit_b_001", headers=headers)
    assert res.status_code == 403
    assert "permission" in res.json()["detail"]

def test_learner_b_can_access_own_session(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_b"}
    res = client.get("/api/session/sess_audit_b_001", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == "sess_audit_b_001"


# -------------------------------------------------------------
# 5. EMAIL VERIFICATION ENFORCEMENT
# -------------------------------------------------------------

def test_unverified_user_cannot_access_protected_apis(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_unverified"}
    res = client.get("/api/user/journeys", headers=headers)
    assert res.status_code == 403
    assert "Email verification required" in res.json()["detail"]

def test_verify_email_flow_activates_user(client, setup_test_users):
    res = client.post("/api/auth/verify-email", json={"token": "audit_verify_token_123"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # User can now access protected endpoint
    headers = {"Authorization": "Bearer session_audit_unverified"}
    res_after = client.get("/api/user/journeys", headers=headers)
    assert res_after.status_code == 200


# -------------------------------------------------------------
# 6. LOGOUT INVALIDATES SESSION TOKEN
# -------------------------------------------------------------

def test_logout_invalidates_token(client, setup_test_users):
    headers = {"Authorization": "Bearer session_audit_learner_a"}

    # Verify token works for personal insights
    check1 = client.get("/api/insights/personal", headers=headers)
    assert check1.status_code == 200

    # Call logout
    logout_res = client.post("/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    # Subsequent call with invalidated token must return 401
    check2 = client.get("/api/insights/personal", headers=headers)
    assert check2.status_code == 401
    assert "invalid or expired" in check2.json()["detail"] or "Authentication required" in check2.json()["detail"]
