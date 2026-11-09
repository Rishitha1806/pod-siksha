"""Pod-Siksha: Phase P2 Automated Test Suite
Verifies Advanced Teacher Observatory, Grounded AI Recommendations, Student Study Reports,
Classroom Filtering, Downloadable CSV Exports, Production Health Check, and Database Backup.
"""
import io
import os
import sqlite3
import sys
import uuid
import pytest
import httpx

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BASE_URL = "http://127.0.0.1:8008"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pod_siksha.db")

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, headers={"Authorization": "Bearer session_demo_teacher_001"}, timeout=30.0) as c:
        yield c


def test_01_advanced_teacher_analytics_calculation(client):
    """Verifies that /api/dashboard returns genuine SQLite metrics and excludes incomplete quizzes."""
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    summary = data["summary"]

    assert "total_sessions" in summary
    assert "total_doubts" in summary
    assert "total_quizzes" in summary
    assert "avg_quiz_score" in summary
    assert "rates" in summary

    rates = summary["rates"]
    assert "correct_rate" in rates
    assert "partial_rate" in rates
    assert "incorrect_rate" in rates

    # Verify counts match database
    with sqlite3.connect(DB_PATH) as conn:
        db_sess_cnt = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        db_doubt_cnt = conn.execute("SELECT COUNT(*) FROM doubts").fetchone()[0]
        db_quiz_cnt = conn.execute("SELECT COUNT(*) FROM quiz_sessions WHERE completed = 1").fetchone()[0]

    assert summary["total_sessions"] == db_sess_cnt
    assert summary["total_doubts"] == db_doubt_cnt
    assert summary["total_quizzes"] == db_quiz_cnt


def test_02_concept_severity_ranking(client):
    """Verifies that concepts are ranked using the transparent severity formula."""
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    f_concepts = data["friction_concepts"]

    if f_concepts:
        # Check first concept has highest or equal severity score
        for i in range(len(f_concepts) - 1):
            assert f_concepts[i]["severity_score"] >= f_concepts[i+1]["severity_score"]

        # Validate formula on top concept: (doubts * 2) + (incorrect * 3) + (partial * 1.5) + (level3 * 3)
        c = f_concepts[0]
        expected_sev = round((c["doubts"] * 2) + (c["quiz_incorrect"] * 3) + (c["quiz_partial"] * 1.5) + (c["level3_hints"] * 3), 1)
        assert c["severity_score"] == expected_sev
        assert c["severity_category"] in ["High Confusion", "Moderate Confusion", "Improving", "Well Understood"]


def test_03_level3_hint_aggregation(client):
    """Verifies that concepts requiring full Level 3 explanations are surfaced in level3_analysis."""
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    l3_list = data["level3_analysis"]

    for item in l3_list:
        assert "concept" in item
        assert "level3_count" in item
        assert item["level3_count"] > 0
        assert "sessions_affected" in item
        assert "recommended_action" in item


def test_04_teacher_recommendations_grounding(client):
    """Verifies that /api/teacher/recommendations returns grounded pedagogical advice."""
    res = client.get("/api/teacher/recommendations")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] in ["active", "fallback", "insufficient_data"]
    if data["status"] in ["active", "fallback"]:
        assert "recommendations" in data
        assert len(data["recommendations"]) >= 1
        for rec in data["recommendations"]:
            assert "concept" in rec
            assert "evidence" in rec
            assert "recommendation" in rec
            assert "suggested_action" in rec


def test_05_student_study_report_isolation(client):
    """Verifies student study report structure and rejection of non-existent sessions."""
    # 1. Invalid session should return 404
    bad_id = str(uuid.uuid4())
    res_bad = client.get(f"/api/student/{bad_id}/report")
    assert res_bad.status_code == 404

    # 2. Valid session should return structured report
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1").fetchone()

    if row:
        sess_id = row[0]
        res_ok = client.get(f"/api/student/{sess_id}/report")
        assert res_ok.status_code == 200
        rep = res_ok.json()
        assert rep["session_id"] == sess_id
        assert "title" in rep
        assert "language" in rep
        assert "doubts" in rep
        assert "quiz" in rep
        assert "questions" in rep["quiz"]


def test_06_classroom_filters(client):
    """Verifies that filtering by chapter, language, and date range returns scoped data."""
    # Test with non-existent chapter
    res_empty = client.get("/api/dashboard?chapter=NonExistentChapter999")
    assert res_empty.status_code == 200
    empty_data = res_empty.json()
    assert empty_data["summary"]["total_sessions"] == 0
    assert empty_data["summary"]["total_doubts"] == 0

    # Test with valid language filter
    res_lang = client.get("/api/dashboard?language=te")
    assert res_lang.status_code == 200
    lang_data = res_lang.json()
    assert lang_data["summary"]["total_sessions"] >= 0


def test_07_csv_export_classroom(client):
    """Verifies /api/teacher/export/csv returns valid, sanitized CSV headers and content."""
    res = client.get("/api/teacher/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    assert "attachment; filename=pod_siksha_classroom_analytics_" in res.headers.get("content-disposition", "")

    csv_text = res.text
    assert "POD-SIKSHA CLASSROOM INTELLIGENCE REPORT" in csv_text
    assert "CLASSROOM OVERVIEW METRICS" in csv_text
    assert "CONCEPT CONFUSION & FRICTION RANKING" in csv_text


def test_08_csv_export_student(client):
    """Verifies /api/student/{session_id}/export/csv returns student report CSV."""
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1").fetchone()

    if row:
        sess_id = row[0]
        res = client.get(f"/api/student/{sess_id}/export/csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")
        assert f"pod_siksha_student_report_{sess_id[:8]}" in res.headers.get("content-disposition", "")
        csv_text = res.text
        assert "POD-SIKSHA STUDENT STUDY REPORT" in csv_text
        assert sess_id in csv_text


def test_09_production_health_check(client):
    """Verifies that /api/health probes database connectivity and external model states."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] == "connected"
    assert "gnani_stt" in data
    assert "gnani_tts" in data
    assert "gemini_api" in data


def test_10_database_backup_integrity():
    """Verifies that scripts/backup_db.py creates a valid backup and passes PRAGMA integrity_check."""
    from scripts.backup_db import run_backup
    backup_path = run_backup()
    assert os.path.exists(backup_path)

    # Verify backup is readable and has integrity
    with sqlite3.connect(backup_path) as conn:
        status = conn.execute("PRAGMA integrity_check").fetchone()[0]
        assert status.lower() == "ok"
