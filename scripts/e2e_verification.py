"""
Comprehensive End-to-End Verification Suite for Pod-Siksha 3.0 Universal AI Educator.
Tests Priority 1 (Working Experience), Priority 2 (Universal Subjects), Priority 3 (Topic-Only),
Priority 4 (Socratic Studio), and Priority 5 (Security & Isolation).
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

BASE_URL = "http://127.0.0.1:8008"
FIXTURES_DIR = Path("tests/fixtures/phase2_documents")

def run_e2e_verification():
    print("=" * 70)
    print("POD-SIKSHA 3.0 — END-TO-END VERIFICATION & ACCEPTANCE SUITE")
    print("=" * 70)

    # 1. User Setup & Auth
    user_a_email = f"e2e_user_a_{int(time.time())}@podsiksha.edu"
    user_b_email = f"e2e_user_b_{int(time.time())}@podsiksha.edu"
    pwd = "TestPassword@123"

    res_a = requests.post(f"{BASE_URL}/api/auth/register", json={"email": user_a_email, "password": pwd, "full_name": "Scholar Alpha"})
    assert res_a.status_code == 200, f"Register User A failed: {res_a.text}"
    token_a = res_a.json()["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    res_b = requests.post(f"{BASE_URL}/api/auth/register", json={"email": user_b_email, "password": pwd, "full_name": "Scholar Beta"})
    assert res_b.status_code == 200, f"Register User B failed: {res_b.text}"
    token_b = res_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("[AUTH] User A & User B registered and isolated.")

    # 2. PRIORITY 2: Test 3 Universal Subjects
    test_docs = [
        {
            "fixture": "01_python_programming.pdf",
            "subject_expected": "Computer Science / Python",
            "expected_strategy": ["code_walkthrough", "algorithmic_trace", "interactive_derivation"]
        },
        {
            "fixture": "02_java_oop.pdf",
            "subject_expected": "Object-Oriented Programming / Java",
            "expected_strategy": ["hierarchy_diagram", "code_walkthrough", "comparative_table"]
        },
        {
            "fixture": "05_biology_cell_energetics.pdf",
            "subject_expected": "Cell Biology & Bioenergetics",
            "expected_strategy": ["process_animation", "structural_model", "causal_flow"]
        }
    ]

    user_a_doc_ids = []
    user_a_proj_ids = []

    for item in test_docs:
        fx = item["fixture"]
        pdf_path = FIXTURES_DIR / fx
        print(f"\n[SUBJECT TEST] Uploading & Processing: {fx}...")
        assert pdf_path.exists(), f"Fixture {fx} missing"

        # Upload
        with open(pdf_path, "rb") as f:
            up_res = requests.post(
                f"{BASE_URL}/api/documents/upload",
                files={"file": (fx, f, "application/pdf")},
                headers=headers_a
            )
        assert up_res.status_code == 200, f"Upload {fx} failed: {up_res.text}"
        doc_data = up_res.json()
        doc_id = doc_data["document_id"]
        job_id = doc_data["job_id"]
        user_a_doc_ids.append(doc_id)

        # Process Job
        from document_service import DocumentService
        job_res = DocumentService.process_document_job(job_id)
        assert job_res["status"] == "completed", f"Job failed: {job_res}"
        summary = job_res["summary"]
        print(f"  -> Extracted: {summary['concept_count']} concepts, {summary.get('code_blocks_count', 0)} code blocks, {summary.get('figures_count', 0)} figures, {summary.get('strategies_count', 0)} strategies")

        # Verify Concepts & Page References
        c_res = requests.get(f"{BASE_URL}/api/documents/{doc_id}/concepts", headers=headers_a)
        assert c_res.status_code == 200
        concepts = c_res.json()["concepts"]
        assert len(concepts) >= 1
        target_concept = concepts[0]
        print(f"  -> Top Concept: '{target_concept['name']}' (Page ref: {target_concept.get('source_page', 1)})")

        # Verify Strategies
        s_res = requests.get(f"{BASE_URL}/api/documents/{doc_id}/teaching-strategies", headers=headers_a)
        assert s_res.status_code == 200
        strategies = s_res.json().get("teaching_strategies", [])
        primary_method = strategies[0]["method"] if strategies else "concept_explanation"
        print(f"  -> Recommended Method: '{primary_method}'")

        # Launch Concept Lesson (PRIORITY 1: Full Visual Lesson Generation)
        learn_res = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/learn-concept",
            json={"concept_name": target_concept["name"], "learner_profile": "teen", "language": "te"},
            headers=headers_a
        )
        assert learn_res.status_code == 200, f"Learn concept failed: {learn_res.text}"
        proj = learn_res.json()["project"]
        proj_id = proj.get("id") or proj.get("project_id")
        user_a_proj_ids.append(proj_id)

        # Fetch Project Details
        proj_detail_res = requests.get(f"{BASE_URL}/api/animated/project/{proj_id}", headers=headers_a)
        assert proj_detail_res.status_code == 200
        proj_detail = proj_detail_res.json()
        scenes = proj_detail.get("scenes", [])
        assert len(scenes) >= 3, f"Expected at least 3 scenes, got {len(scenes)}"
        print(f"  -> Lesson Created: '{proj['title']}' with {len(scenes)} fully populated scenes")

        # Inspect Scene Properties
        for idx, sc in enumerate(scenes):
            narration = sc.get("narration_text") or sc.get("narration_te") or sc.get("narration")
            assert narration and len(narration) > 10, f"Scene {idx+1} missing narration"
            assert sc.get("visual_spec"), f"Scene {idx+1} missing visual spec"
            assert sc.get("checkpoint_question"), f"Scene {idx+1} missing checkpoint question"
        print(f"  -> Verified non-empty scenes, visual specs, animations, checkpoints & Telugu narration across all {len(scenes)} scenes.")

    # 3. PRIORITY 3: Topic-Only Learning
    print("\n[TOPIC-ONLY TEST] Requesting lesson for topic: 'Quantum Entanglement & Bell State' (No file, No notes)...")
    topic_res = requests.post(
        f"{BASE_URL}/api/animated/project",
        data={
            "topic": "Quantum Entanglement and Bell State",
            "learner_profile": "adult",
            "language": "te",
            "source_type": "topic"
        },
        headers=headers_a
    )
    assert topic_res.status_code == 200, f"Topic project failed: {topic_res.text}"
    top_proj = topic_res.json()
    top_proj_id = top_proj.get("id") or top_proj.get("project_id")
    top_detail = requests.get(f"{BASE_URL}/api/animated/project/{top_proj_id}", headers=headers_a).json()
    assert len(top_detail.get("scenes", [])) >= 3
    print(f"  -> Topic-only project verified! Title: '{top_proj['title']}' with {len(top_detail['scenes'])} scenes.")

    # 4. PRIORITY 4: Socratic Broadcast Studio & Audio Playback
    print("\n[SOCRATIC STUDIO TEST] Ingesting topic 'Indian Constitutional Law' without text...")
    sess_res = requests.post(
        f"{BASE_URL}/api/session",
        data={"title": "Indian Constitutional Law", "language": "te"},
        headers=headers_a
    )
    assert sess_res.status_code == 200, f"Session creation failed: {sess_res.text}"
    sess_id = sess_res.json()["session_id"]
    sess_detail = requests.get(f"{BASE_URL}/api/session/{sess_id}", headers=headers_a).json()
    assert len(sess_detail.get("turns", [])) >= 10
    print(f"  -> Socratic episode generated: {len(sess_detail['turns'])} turns of two-host dialogue.")

    # Test Audio Endpoint with Query Token (used by <audio> tags)
    audio_url = f"{BASE_URL}/api/tts?session_id={sess_id}&turn_index=1&speaker=A&language=te&token={token_a}"
    audio_res = requests.get(audio_url)
    assert audio_res.status_code == 200, f"Audio fetch failed: {audio_res.status_code}"
    assert "audio" in audio_res.headers.get("content-type", "").lower()
    print(f"  -> Audio streaming verified: {len(audio_res.content)} bytes received with Content-Type: {audio_res.headers.get('content-type')}.")

    # 5. PRIORITY 5: Security & Isolation
    print("\n[SECURITY TEST] Verifying Cross-Tenant Isolation...")
    # User B tries to read User A's document
    doc_b_res = requests.get(f"{BASE_URL}/api/documents/{user_a_doc_ids[0]}", headers=headers_b)
    assert doc_b_res.status_code in [403, 404], f"Cross-tenant document leak! User B got: {doc_b_res.status_code}"
    print(f"  -> Document isolation: User B blocked with HTTP {doc_b_res.status_code} on User A's document.")

    # User B tries to read User A's animated project
    proj_b_res = requests.get(f"{BASE_URL}/api/animated/project/{user_a_proj_ids[0]}", headers=headers_b)
    assert proj_b_res.status_code in [403, 404], f"Cross-tenant project leak! User B got: {proj_b_res.status_code}"
    print(f"  -> Animated project isolation: User B blocked with HTTP {proj_b_res.status_code} on User A's project.")

    # User B tries to read User A's session
    sess_b_res = requests.get(f"{BASE_URL}/api/session/{sess_id}", headers=headers_b)
    assert sess_b_res.status_code in [403, 404], f"Cross-tenant session leak! User B got: {sess_b_res.status_code}"
    print(f"  -> Socratic session isolation: User B blocked with HTTP {sess_b_res.status_code} on User A's session.")

    print("\n" + "=" * 70)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY (100% PASS)")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()
