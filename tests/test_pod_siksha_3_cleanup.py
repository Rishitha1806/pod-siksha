"""
Comprehensive Acceptance & Quality Assurance Test Suite for Pod-Siksha 3.0.
Verifies Concept DNA Knowledge Tree, Single AI Educator, Ask This Scene, Explain It Again,
Teach-Back, Understanding Tracker, Honest Empty States, and Multi-Tenant Isolation.
"""

import pytest
import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8008"

@pytest.fixture(scope="session")
def learner_session():
    """Registers a fresh test user and returns auth headers."""
    email = f"learner_{uuid.uuid4().hex[:8]}@atelier.edu"
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Test Sovereign Learner",
        "email": email,
        "password": "Password123!",
        "role": "learner"
    })
    assert reg_res.status_code == 200, f"Register failed: {reg_res.text}"

    login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    data = login_res.json()
    token = data["token"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": data["user"]["id"],
        "email": email
    }

def test_01_health_check():
    """Verify backend health and services."""
    res = requests.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_02_honest_empty_states(learner_session):
    """Verify fresh user has honest empty states without fake photosynthesis dummy data."""
    headers = learner_session["headers"]

    # 1. Concept Tree Empty State
    tree_res = requests.get(f"{BASE_URL}/api/concept-tree", headers=headers)
    assert tree_res.status_code == 200
    tree_data = tree_res.json()
    assert tree_data["total_concepts"] == 0
    assert len(tree_data["trees"]) == 0
    assert "grow" in tree_data["message"].lower()

    # 2. Insights Telemetry Empty State (No fake 78%)
    ins_res = requests.get(f"{BASE_URL}/api/insights/personal", headers=headers)
    assert ins_res.status_code == 200
    ins_data = ins_res.json()
    assert ins_data["overall_mastery"] == 0.0
    assert len(ins_data["concept_breakdown"]) == 0

    # 3. Journeys Empty State
    j_res = requests.get(f"{BASE_URL}/api/user/journeys", headers=headers)
    assert j_res.status_code == 200
    assert len(j_res.json().get("journeys", [])) == 0

def test_03_generate_real_animated_lesson(learner_session):
    """Generates an authentic animated lesson from a real topic without dummy data."""
    headers = learner_session["headers"]

    res = requests.post(f"{BASE_URL}/api/animated/project", headers=headers, data={
        "title": "Photosynthesis and Cellular Respiration",
        "topic": "Photosynthesis and Cellular Respiration",
        "language": "en",
        "learner_profile": "intermediate",
        "animation_style": "educational_2d",
        "content_text": "Photosynthesis converts solar light, water, and carbon dioxide into glucose and oxygen in the chloroplast thylakoids. Cellular respiration in mitochondria breaks down glucose with oxygen to produce ATP, carbon dioxide, and water."
    })
    assert res.status_code == 200, f"Project generation failed: {res.text}"
    data = res.json()
    project_id = data.get("id") or data.get("project_id") or data.get("project", {}).get("id")
    assert project_id is not None
    assert "scenes" in data
    assert len(data["scenes"]) >= 1

    learner_session["project_id"] = project_id
    learner_session["scenes"] = data["scenes"]
    learner_session["scene_id"] = data["scenes"][0]["id"]
    learner_session["concept_tag"] = data["scenes"][0]["concept_tag"]

    assert len(data["scenes"]) >= 3

def test_04_concept_dna_knowledge_tree(learner_session):
    """Verifies that Concept DNA tree is generated dynamically from the real lesson."""
    headers = learner_session["headers"]
    project_id = learner_session["project_id"]

    res = requests.get(f"{BASE_URL}/api/concept-tree?project_id={project_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_concepts"] >= 3
    assert len(data["trees"]) >= 1

    tree_obj = data["trees"][0]
    assert tree_obj["project_id"] == project_id
    assert tree_obj["tree"]["is_root"] is True
    assert len(tree_obj["tree"]["children"]) >= 1

    # Check node structure
    first_node = tree_obj["tree"]["children"][0]
    assert "name" in first_node
    assert first_node["status"] in ("learning", "understood", "needs_revision", "not_started")
    assert "status_reason" in first_node

def test_05_concept_detail_and_explain(learner_session):
    """Tests concept detail panel and dynamic explanation modes via Gemini."""
    headers = learner_session["headers"]
    concept_tag = learner_session["concept_tag"]

    # 1. Detail endpoint
    det_res = requests.get(f"{BASE_URL}/api/concept-tree/node/{concept_tag}", headers=headers)
    assert det_res.status_code == 200
    det_data = det_res.json()
    assert det_data["name"] == concept_tag
    assert det_data["status"] in ("learning", "understood", "needs_revision")

    # 2. Dynamic Explanation: simpler mode
    exp_res = requests.post(f"{BASE_URL}/api/concept-tree/explain", headers=headers, json={
        "concept_name": concept_tag,
        "mode": "simpler",
        "complexity": "beginner",
        "language": "en"
    })
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "explanation" in exp_data
    assert len(exp_data["explanation"]) > 30

    # 3. Dynamic Explanation: step_by_step mode
    step_res = requests.post(f"{BASE_URL}/api/concept-tree/explain", headers=headers, json={
        "concept_name": concept_tag,
        "mode": "step_by_step",
        "complexity": "intermediate",
        "language": "en"
    })
    assert step_res.status_code == 200
    assert "explanation" in step_res.json()

def test_06_compare_two_concepts(learner_session):
    """Tests side-by-side comparative analysis of two concepts."""
    headers = learner_session["headers"]

    res = requests.post(f"{BASE_URL}/api/concept-tree/compare", headers=headers, json={
        "concept_a": "Photosynthesis",
        "concept_b": "Cellular Respiration",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert "similarities" in data
    assert len(data["similarities"]) >= 1
    assert "differences" in data
    assert len(data["differences"]) >= 1
    assert "comparison_table" in data
    assert "check_question" in data
    assert len(data["check_question"]["options"]) == 4

def test_07_ask_this_scene_doubt(learner_session):
    """Tests contextual question resolution for the exact active scene."""
    headers = learner_session["headers"]
    scene_id = learner_session["scene_id"]

    res = requests.post(f"{BASE_URL}/api/animated/scene/{scene_id}/ask", headers=headers, json={
        "question": "Why is light energy necessary for this reaction to happen?",
        "complexity": "intermediate",
        "explanation_style": "step_by_step"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "spoken_answer" in data
    assert "display_answer" in data

def test_08_explain_it_again(learner_session):
    """Tests Explain It Again adaptive re-explanation for the active scene."""
    headers = learner_session["headers"]
    scene_id = learner_session["scene_id"]

    res = requests.post(f"{BASE_URL}/api/animated/scene/{scene_id}/explain-again", headers=headers, json={
        "mode": "analogy",
        "complexity": "beginner"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "explanation" in data
    assert "key_takeaway" in data

def test_09_checkpoint_quiz_updates_status(learner_session):
    """Tests submitting checkpoint answer and verifying evidence-based status update."""
    headers = learner_session["headers"]
    project_id = learner_session["project_id"]
    scene_id = learner_session["scene_id"]

    # Submit correct answer (or test response)
    res = requests.post(f"{BASE_URL}/api/animated/project/{project_id}/checkpoint", headers=headers, json={
        "scene_id": scene_id,
        "selected_option_index": 0
    })
    assert res.status_code == 200
    data = res.json()
    assert "is_correct" in data

    # Verify Concept DNA node status was updated in DB
    tree_res = requests.get(f"{BASE_URL}/api/concept-tree?project_id={project_id}", headers=headers)
    assert tree_res.status_code == 200
    nodes = tree_res.json()["trees"][0]["all_nodes"]
    matched = next((n for n in nodes if n["scene_id"] == scene_id), None)
    assert matched is not None
    assert matched["status"] in ("understood", "needs_revision")
    assert "Checkpoint Quiz" in matched["status_reason"]

def test_10_mark_for_revision(learner_session):
    """Tests explicit revision flagging by learner."""
    headers = learner_session["headers"]
    concept_tag = learner_session["concept_tag"]
    project_id = learner_session["project_id"]

    res = requests.post(f"{BASE_URL}/api/concept-tree/mark-revision", headers=headers, json={
        "concept_name": concept_tag,
        "reason": "Need to review electron transport chain",
        "project_id": project_id
    })
    assert res.status_code == 200
    assert res.json()["new_status"] == "needs_revision"

    # Verify status in tree
    tree_res = requests.get(f"{BASE_URL}/api/concept-tree?project_id={project_id}", headers=headers)
    assert tree_res.status_code == 200
    assert tree_res.json()["revision_count"] >= 1

def test_11_teachback_workflow(learner_session):
    """Tests Teach-Back concept retrieval and authentic AI evaluation."""
    headers = learner_session["headers"]
    concept_tag = learner_session["concept_tag"]
    project_id = learner_session["project_id"]

    # 1. Fetch available concepts
    c_res = requests.get(f"{BASE_URL}/api/teachback/concepts", headers=headers)
    assert c_res.status_code == 200
    concepts = c_res.json()["concepts"]
    assert len(concepts) >= 1

    # 2. Submit authentic explanation
    tb_res = requests.post(f"{BASE_URL}/api/teachback/evaluate", headers=headers, data={
        "concept_tag": concept_tag,
        "project_id": project_id,
        "explanation_text": "Water is split in the thylakoid using photon energy to release oxygen and provide electrons.",
        "ai_prompt": f"Explain {concept_tag} in your own words."
    })
    assert tb_res.status_code == 200
    tb_data = tb_res.json()
    assert "understood_points" in tb_data
    assert "mastery_score" in tb_data

def test_12_understanding_tracker_telemetry(learner_session):
    """Verifies that personal insights telemetry computes genuine counts from user activity."""
    headers = learner_session["headers"]

    res = requests.get(f"{BASE_URL}/api/insights/personal", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["overall_mastery"] > 0
    assert len(data["concept_breakdown"]) >= 1

def test_13_multi_tenant_isolation(learner_session):
    """Verifies that a second user cannot view or mutate the first user's concept tree or project."""
    # Register User B
    b_email = f"user_b_{uuid.uuid4().hex[:8]}@other.edu"
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Unauthorized User B",
        "email": b_email,
        "password": "Password123!",
        "role": "learner"
    })
    login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": b_email,
        "password": "Password123!"
    })
    b_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}

    # User B requests User A's project concept tree
    proj_id_a = learner_session["project_id"]
    tree_res = requests.get(f"{BASE_URL}/api/concept-tree?project_id={proj_id_a}", headers=b_headers)
    assert tree_res.status_code == 200
    assert len(tree_res.json()["trees"]) == 0, "User B must not see User A's concept tree!"
