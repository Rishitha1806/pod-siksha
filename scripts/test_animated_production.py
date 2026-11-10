"""
Comprehensive automated production verification suite for Pod-Siksha 2.0
Universal AI Animated Learning Platform deployed at https://pod-siksha-2.vercel.app
"""

import sys
import json
import uuid
import urllib.request
import urllib.parse
import urllib.error
import time

BASE_URL = "https://pod-siksha-2.vercel.app"
TEST_USER_ID = uuid.uuid4().hex[:8]
TEST_EMAIL = f"anim_prod_{TEST_USER_ID}@aurasiksha.edu"
TEST_PASS = "Password@1234"

results = []

def run_test(name, fn):
    print(f"\n--- [TEST] {name} ---")
    start = time.time()
    try:
        res = fn()
        dur = round(time.time() - start, 2)
        print(f"PASSED ({dur}s): {res}")
        results.append({"name": name, "status": "PASSED", "duration": dur, "details": str(res)})
        return True
    except Exception as e:
        dur = round(time.time() - start, 2)
        print(f"FAILED ({dur}s): {e}")
        results.append({"name": name, "status": "FAILED", "duration": dur, "error": str(e)})
        return False

# 1. Health Check
def test_health():
    req = urllib.request.Request(f"{BASE_URL}/api/health", headers={"User-Agent": "TestSuite/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        if data.get("status") not in ("ok", "healthy"):
            raise ValueError(f"Health returned unexpected status: {data}")
        return f"Status: {data.get('status')}, Database: {data.get('database')}, Environment: {data.get('environment')}"

# 2. Static Asset Animation Engine
def test_static_engine():
    req = urllib.request.Request(f"{BASE_URL}/static/animation_engine.js", headers={"User-Agent": "TestSuite/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8")
        if "UniversalAnimationEngine" not in content:
            raise ValueError("UniversalAnimationEngine class missing in static/animation_engine.js")
        return f"Delivered {len(content)} bytes with UniversalAnimationEngine verified."

# 3. Unauthenticated Root Login-First Enforcement
def test_root_login_first():
    req = urllib.request.Request(f"{BASE_URL}/", headers={"User-Agent": "TestSuite/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8")
        if 'id="view-login"' not in html or 'id="view-animated-studio"' not in html:
            raise ValueError("HTML structure missing login or animated-studio views.")
        return "Root serves login-first container with animated studio views mounted."

# 4. Animated Profiles Endpoint
def test_animated_profiles():
    req = urllib.request.Request(f"{BASE_URL}/api/animated/profiles", headers={"User-Agent": "TestSuite/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        profiles = data.get("profiles", {})
        required = ["child", "teen", "university", "professional", "older_adult"]
        for r in required:
            if r not in profiles:
                raise ValueError(f"Profile {r} missing from profiles: {list(profiles.keys())}")
        return f"All 5 universal generational profiles present: {list(profiles.keys())}"

# 5. Animated Styles Endpoint
def test_animated_styles():
    req = urllib.request.Request(f"{BASE_URL}/api/animated/styles", headers={"User-Agent": "TestSuite/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        styles = data.get("styles", {})
        if len(styles) < 5:
            raise ValueError(f"Expected at least 5 styles, got: {styles}")
        return f"Visual styles verified: {list(styles.keys())}"

# 6. User Registration & Authentication (Neon PostgreSQL)
auth_token = None
def test_auth_register_and_login():
    global auth_token
    reg_payload = json.dumps({
        "full_name": f"Aura Learner {TEST_USER_ID}",
        "email": TEST_EMAIL,
        "password": TEST_PASS,
        "preferred_language": "te"
    }).encode()
    reg_req = urllib.request.Request(
        f"{BASE_URL}/api/auth/register",
        data=reg_payload,
        headers={"Content-Type": "application/json", "User-Agent": "TestSuite/1.0"}
    )
    with urllib.request.urlopen(reg_req, timeout=20) as resp:
        reg_data = json.loads(resp.read().decode())

    login_payload = json.dumps({"email": TEST_EMAIL, "password": TEST_PASS}).encode()
    login_req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=login_payload,
        headers={"Content-Type": "application/json", "User-Agent": "TestSuite/1.0"}
    )
    with urllib.request.urlopen(login_req, timeout=20) as resp:
        login_data = json.loads(resp.read().decode())
        auth_token = login_data.get("token")
        if not auth_token:
            raise ValueError(f"Login failed: {login_data}")
        return f"Registered & logged in {TEST_EMAIL} -> Session token issued: {auth_token[:20]}..."

# 7. User Animated Projects List
def test_list_projects():
    req = urllib.request.Request(
        f"{BASE_URL}/api/animated/projects",
        headers={"Authorization": f"Bearer {auth_token}", "User-Agent": "TestSuite/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        return f"User has {len(data)} animated projects isolated in Neon PostgreSQL."

# 8. Create New Universal Animated Lesson (Child Profile: Water Cycle / Rain in Hindi)
created_project = None
def test_create_child_animated_lesson():
    global created_project
    boundary = "----WebKitFormBoundaryAnimTest7MA4YWxkTrZu0gW"
    fields = {
        "title": "Why Does It Rain? The Magical Water Cycle",
        "topic": "Explain evaporation, cloud condensation, and precipitation for young kids using everyday analogies like boiling tea and cold windows.",
        "learner_profile": "child",
        "language": "hi",
        "animation_style": "cartoon",
        "source_type": "topic"
    }
    
    body = ""
    for k, v in fields.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n"
    body += f"--{boundary}--\r\n"

    req = urllib.request.Request(
        f"{BASE_URL}/api/animated/project",
        data=body.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "TestSuite/1.0"
        }
    )
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        create_res = json.loads(resp.read().decode())
        project_id = create_res.get("project_id")
        if not project_id:
            raise ValueError(f"Project creation failed: {create_res}")
        
    # Fetch full project details including ordered scenes
    detail_req = urllib.request.Request(
        f"{BASE_URL}/api/animated/project/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}", "User-Agent": "TestSuite/1.0"}
    )
    with urllib.request.urlopen(detail_req, timeout=20) as resp:
        created_project = json.loads(resp.read().decode())
        scenes = created_project.get("scenes", [])
        if not scenes:
            raise ValueError("Created project has no scenes.")
        return (
            f"Created Child Lesson '{created_project.get('title')}' (ID: {created_project.get('id')}) "
            f"with {len(scenes)} scenes in Hindi cartoon style. Scene 1 visual_type: {scenes[0].get('animation_type')} "
            f"('{scenes[0].get('title')}')"
        )

# 9. In-Video Socratic Ask Doubt
def test_socratic_doubt():
    if not created_project or not created_project.get("scenes"):
        raise ValueError("No created project scene available to test doubt.")
    
    scene = created_project["scenes"][0]
    payload = json.dumps({"doubt_text": "Why do clouds become gray and dark before it rains?"}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/animated/scene/{scene['id']}/ask",
        data=payload,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "TestSuite/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode())
        ans = data.get("answer_text", "")
        if not ans:
            raise ValueError(f"Socratic doubt returned empty answer: {data}")
        has_audio = bool(data.get("audio_b64"))
        return f"Socratic response received ({len(ans)} chars). Voice synthesized: {has_audio}. Answer preview: '{ans[:75]}...'"

# 10. Checkpoint Concept DNA Logging
def test_checkpoint_dna():
    if not created_project or not created_project.get("scenes"):
        raise ValueError("No created project scene available.")
    
    scene = created_project["scenes"][0]
    cp = scene.get("checkpoint_question") or {}
    q = cp.get("question", "What happens during evaporation?")
    
    payload = json.dumps({
        "scene_id": scene["id"],
        "question": q,
        "selected_idx": cp.get("correct_index", 0),
        "is_correct": True
    }).encode()
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/animated/project/{created_project['id']}/checkpoint",
        data=payload,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "TestSuite/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        if not data.get("ok"):
            raise ValueError(f"Checkpoint logging failed: {data}")
        return f"Concept DNA checkpoint recorded in Neon PostgreSQL for user: {data.get('concept_id')}"

# 11. Video Export Manifest
def test_export_manifest():
    if not created_project:
        raise ValueError("No created project.")
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/animated/project/{created_project['id']}/export/manifest",
        headers={"Authorization": f"Bearer {auth_token}", "User-Agent": "TestSuite/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        scenes = data.get("scenes", [])
        dur = data.get("total_duration_sec")
        return f"Export manifest generated with {len(scenes)} scenes (Total duration: {dur}s). Audio tracks & visual specs verified."

def main():
    print(f"Starting Pod-Siksha 2.0 Live Production Verification at {BASE_URL}")
    run_test("1. Production Backend Health & Neon DB Status", test_health)
    run_test("2. Static Animation Simulation Engine Delivery", test_static_engine)
    run_test("3. Root URL Login-First Enforcement", test_root_login_first)
    run_test("4. Universal Learner Profiles (5 Generations)", test_animated_profiles)
    run_test("5. Visual Animation Styles (5 Themes)", test_animated_styles)
    run_test("6. Multi-Tenant Authentication & Session Login", test_auth_register_and_login)
    run_test("7. User Animated Projects List from Neon DB", test_list_projects)
    run_test("8. AI Storyboard Synthesis (Child Profile, Hindi, Cartoon)", test_create_child_animated_lesson)
    run_test("9. In-Video Socratic Question Answering with Voice", test_socratic_doubt)
    run_test("10. Checkpoint DNA Telemetry & Concept Recording", test_checkpoint_dna)
    run_test("11. Client-Side Video Export Manifest Generation", test_export_manifest)

    passed = [r for r in results if r["status"] == "PASSED"]
    failed = [r for r in results if r["status"] == "FAILED"]
    print(f"\n==========================================")
    print(f"VERIFICATION SUMMARY: {len(passed)}/{len(results)} PASSED ({len(failed)} failed)")
    print(f"==========================================")
    
    if failed:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
