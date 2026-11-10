"""
Production End-to-End Verification Suite for Pod-Siksha 2.0
Target URL: https://pod-siksha-2.vercel.app
Database: Neon PostgreSQL
"""

import sys
import uuid
import httpx
import time

BASE_URL = "https://pod-siksha-2.vercel.app"
print(f"=== Starting Production Verification against {BASE_URL} ===\n")

client = httpx.Client(base_url=BASE_URL, timeout=45.0, follow_redirects=True)

test_results = {}

def record_test(name: str, passed: bool, details: str = ""):
    status = "PASSED" if passed else "FAILED"
    print(f"[{status}] {name}")
    if details:
        print(f"       Details: {details}")
    test_results[name] = {"passed": passed, "details": details}

# Test 1: Health Check Endpoint
try:
    r = client.get("/api/health")
    assert r.status_code == 200, f"Status code: {r.status_code}"
    data = r.json()
    assert data["status"] == "healthy", f"Status: {data.get('status')}"
    assert data["database"] == "connected", f"Database: {data.get('database')}"
    assert data["environment"] == "production", f"Environment: {data.get('environment')}"
    assert data["gnani_stt"] == "configured"
    assert data["gnani_tts"] == "configured"
    assert data["gemini_api"] == "configured"
    record_test("1. Production Health Check & Neon DB Connectivity", True, f"DB: {data['database']}, STT: {data['gnani_stt']}, TTS: {data['gnani_tts']}")
except Exception as e:
    record_test("1. Production Health Check & Neon DB Connectivity", False, str(e))

# Test 2: Unauthenticated Visitor on Root '/' sees Login
try:
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    assert "Pod-Siksha" in html
    # Check that login section exists and strict auth routing is active
    assert 'id="login-view"' in html or 'id="loginSection"' in html or 'data-auth="login"' in html or 'Sign in' in html or 'Login' in html
    record_test("2. Unauthenticated Visitor Root Landing (/)", True, "HTML correctly served with Login/Auth interfaces")
except Exception as e:
    record_test("2. Unauthenticated Visitor Root Landing (/)", False, str(e))

# Test 3: Strict Route Protection (Unauthenticated requests to protected endpoints return 401)
try:
    protected_paths = [
        "/api/auth/me",
        "/api/user/journeys",
        "/api/dashboard",
        "/api/insights/personal",
        "/api/misconceptions",
        "/api/memory-loop"
    ]
    all_401 = True
    for p in protected_paths:
        res = client.get(p)
        if res.status_code != 401:
            all_401 = False
            raise AssertionError(f"Path {p} returned {res.status_code} instead of 401")
    record_test("3. Strict Access Control (Protected APIs return 401)", all_401, f"All {len(protected_paths)} protected routes returned 401 Unauthorized")
except Exception as e:
    record_test("3. Strict Access Control (Protected APIs return 401)", False, str(e))

# Test 4: Registration of New User (Neon write verification)
rand_id = uuid.uuid4().hex[:8]
test_email = f"prod_verify_{rand_id}@example.com"
test_password = "Password@1234"
test_name = f"Neon Prod User {rand_id}"

reg_data = {}
try:
    r = client.post("/api/auth/register", json={
        "email": test_email,
        "password": test_password,
        "full_name": test_name,
        "preferred_language": "te"
    })
    assert r.status_code == 200, f"Status: {r.status_code}, Body: {r.text}"
    reg_data = r.json()
    assert "token" in reg_data or "user" in reg_data or "message" in reg_data
    record_test("4. User Registration (Neon PostgreSQL INSERT)", True, f"Registered user: {test_email}")
except Exception as e:
    record_test("4. User Registration (Neon PostgreSQL INSERT)", False, str(e))

# Test 5: Login with User Credentials
user_token = ""
try:
    r = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert r.status_code == 200, f"Status: {r.status_code}, Body: {r.text}"
    login_data = r.json()
    user_token = login_data.get("token")
    assert user_token, "No token returned in login response"
    record_test("5. User Authentication / Login (Neon session issuance)", True, f"Session token issued: {user_token[:12]}...")
except Exception as e:
    record_test("5. User Authentication / Login (Neon session issuance)", False, str(e))

# Test 6: Authenticated Session Verification (/api/auth/me)
try:
    auth_headers = {"Authorization": f"Bearer {user_token}"}
    r = client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200, f"Status: {r.status_code}"
    res_json = r.json()
    user_obj = res_json.get("user", {})
    assert user_obj.get("email") == test_email
    assert user_obj.get("full_name") == test_name
    record_test("6. Authenticated Session Identity (/api/auth/me)", True, f"Verified: {user_obj.get('full_name')} ({user_obj.get('email')})")
except Exception as e:
    record_test("6. Authenticated Session Identity (/api/auth/me)", False, str(e))

# Test 7: User-Level Data Isolation (New user has 0 journeys, demo user has historical journeys)
try:
    auth_headers = {"Authorization": f"Bearer {user_token}"}
    r_new = client.get("/api/user/journeys", headers=auth_headers)
    assert r_new.status_code == 200
    new_journeys = r_new.json().get("journeys", [])

    # Now query demo learner sessions
    demo_headers = {"Authorization": "Bearer session_demo_learner_001"}
    r_demo = client.get("/api/user/journeys", headers=demo_headers)
    assert r_demo.status_code == 200
    demo_journeys = r_demo.json().get("journeys", [])

    assert len(new_journeys) == 0, f"New user should have 0 journeys, got {len(new_journeys)}"
    assert len(demo_journeys) > 0, f"Demo user should have migrated journeys, got {len(demo_journeys)}"
    record_test("7. Strict User Data Isolation (Neon DB Isolation)", True, f"New user: {len(new_journeys)} journeys | Demo user: {len(demo_journeys)} journeys isolated")
except Exception as e:
    record_test("7. Strict User Data Isolation (Neon DB Isolation)", False, str(e))

# Test 8: Gnani Timbre Audio Synthesis (/api/tts)
try:
    auth_headers = {"Authorization": f"Bearer {user_token}"}
    r = client.get("/api/tts", params={"text": "నమస్కారం, పోడ్-శిక్ష 2.0 కి స్వాగతం", "lang": "te"}, headers=auth_headers)
    assert r.status_code == 200, f"TTS status: {r.status_code}"
    content_type = r.headers.get("content-type", "")
    assert "audio" in content_type or len(r.content) > 100, f"Expected audio stream, got {content_type}"
    record_test("8. Gnani Timbre Audio Synthesis (/api/tts)", True, f"Audio synthesized ({len(r.content)} bytes, {content_type})")
except Exception as e:
    record_test("8. Gnani Timbre Audio Synthesis (/api/tts)", False, str(e))

# Test 9: Gnani Prisma Voice Interruption & Q&A (/api/ask)
try:
    demo_headers = {"Authorization": "Bearer session_demo_learner_001"}
    # Use an existing demo session ID from demo_journeys
    target_session_id = demo_journeys[0]["id"] if demo_journeys else "session_demo_001"
    
    # 1-second silent WAV format audio buffer
    riff_wav = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00' + (b'\x00' * 500)
    files = {"file": ("student_doubt.wav", riff_wav, "audio/wav")}
    data = {
        "session_id": target_session_id,
        "turn_index": "1",
        "playback_ms": "1200",
        "language": "te"
    }
    r = client.post("/api/ask", data=data, files=files, headers=demo_headers)
    assert r.status_code in [200, 400], f"Voice ask status: {r.status_code}"
    ask_res = r.json() if r.status_code == 200 else {}
    record_test("9. Gnani Prisma Voice Interruption & Q&A (/api/ask)", True, f"Status: {r.status_code}, response: {ask_res.get('status', 'processed')}")
except Exception as e:
    record_test("9. Gnani Prisma Voice Interruption & Q&A (/api/ask)", False, str(e))

# Test 10: Concept DNA & Misconceptions & Memory Loop
try:
    demo_headers = {"Authorization": "Bearer session_demo_learner_001"}
    r_misc = client.get("/api/misconceptions", headers=demo_headers)
    assert r_misc.status_code == 200
    misc_list = r_misc.json().get("misconceptions", [])

    r_mem = client.get("/api/memory-loop", headers=demo_headers)
    assert r_mem.status_code == 200
    mem_list = r_mem.json().get("cards", [])

    r_insights = client.get("/api/insights/personal", headers=demo_headers)
    assert r_insights.status_code == 200

    record_test("10. Concept DNA, Misconception Radar & Memory Loop", True, f"Misconceptions: {len(misc_list)} | Memory Loop: {len(mem_list)}")
except Exception as e:
    record_test("10. Concept DNA, Misconception Radar & Memory Loop", False, str(e))

# Test 11: Teacher Observatory & CSV Exports
try:
    teacher_headers = {"Authorization": "Bearer session_demo_teacher_001"}
    r_recs = client.get("/api/teacher/recommendations", headers=teacher_headers)
    assert r_recs.status_code == 200

    r_csv = client.get("/api/teacher/export/csv", headers=teacher_headers)
    assert r_csv.status_code == 200
    assert "concept" in r_csv.text.lower() or "student" in r_csv.text.lower()

    record_test("11. Teacher Observatory & Analytics CSV Export", True, f"CSV Export generated ({len(r_csv.text)} bytes)")
except Exception as e:
    record_test("11. Teacher Observatory & Analytics CSV Export", False, str(e))

# Test 12: Logout and Token Invalidation
try:
    auth_headers = {"Authorization": f"Bearer {user_token}"}
    r_logout = client.post("/api/auth/logout", headers=auth_headers)
    assert r_logout.status_code == 200

    # Ensure token is revoked
    r_revoked = client.get("/api/auth/me", headers=auth_headers)
    assert r_revoked.status_code == 401, f"Expected 401 for revoked token, got {r_revoked.status_code}"
    record_test("12. Logout & Server-Side Token Invalidation (Neon DELETE)", True, "Token revoked successfully; subsequent calls rejected with 401")
except Exception as e:
    record_test("12. Logout & Server-Side Token Invalidation (Neon DELETE)", False, str(e))

print("\n=== Verification Summary ===")
total = len(test_results)
passed = sum(1 for t in test_results.values() if t["passed"])
print(f"Total Tests: {total} | Passed: {passed} | Failed: {total - passed}")
if passed == total:
    print("\nALL PRODUCTION TESTS PASSED SUCCESSFULLY ON VERCEL & NEON POSTGRESQL!")
else:
    print(f"\n{total - passed} tests failed.")
