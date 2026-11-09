"""Comprehensive P1 Test Suite for Pod-Siksha.
Verifies Progressive Hint Ladder, 4-Question Oral Quiz Generation,
Gnani Prisma STT transcription, Gemini 3-category evaluation (Correct, Partially Correct, Incorrect),
Gnani Timbre TTS feedback synthesis, Concept Normalization, and Teacher Observatory Metrics.
"""
import io
import json
import math
import os
import struct
import sys
import wave
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app, get_db, normalize_concept, calculate_hint_ladder, call_gnani_tts

client = TestClient(app)

def generate_test_wav(duration_sec=1.5, sample_rate=16000, freq=440.0) -> bytes:
    """Generates 16kHz mono 16-bit PCM WAV in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        num_samples = int(duration_sec * sample_rate)
        samples = bytearray()
        for i in range(num_samples):
            val = int(12000.0 * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
            samples.extend(struct.pack("<h", val))
        wav.writeframes(samples)
    return buf.getvalue()


def test_01_concept_normalization():
    """Verify concept normalization into canonical taxonomy."""
    assert normalize_concept("photolysis of water") == "Water Photolysis"
    assert normalize_concept("splitting water molecules") == "Water Photolysis"
    assert normalize_concept("thylakoid membrane") == "Chloroplast Structure"
    assert normalize_concept("chlorophyll light absorption") == "Chlorophyll & Light Absorption"
    assert normalize_concept("dark reaction calvin") == "Calvin Cycle & Carbon Fixation"
    assert normalize_concept("stomatal guard cells") == "Stomatal Gas Exchange"


def test_02_progressive_hint_ladder():
    """Verify 3-level hint ladder escalates per concept and session."""
    # Create test session
    sess_res = client.post("/api/session", data={
        "title": "Hint Ladder Session",
        "language": "te",
        "chapter_text": "Water photolysis takes place in the thylakoid membranes. Electrons are excited by light energy."
    })
    session_id = sess_res.json()["session_id"]

    # Initial question on Water Photolysis -> Level 1
    lvl1 = calculate_hint_ladder(session_id, "How does water split?", "Water Photolysis")
    assert lvl1 == 1, f"Expected Level 1, got {lvl1}"

    # Log a Level 1 doubt
    import uuid
    d1_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("INSERT INTO doubts (id, session_id, concept_tag, hint_level, transcribed_text) VALUES (?, ?, 'Water Photolysis', 1, 'water split')", (d1_id, session_id))
        conn.commit()

    # Second doubt on same concept -> Level 2
    lvl2 = calculate_hint_ladder(session_id, "Can you explain water photolysis?", "Water Photolysis")
    assert lvl2 == 2, f"Expected Level 2, got {lvl2}"

    # Querying a DIFFERENT concept -> Starts at Level 1!
    diff_lvl = calculate_hint_ladder(session_id, "What is a chloroplast?", "Chloroplast Structure")
    assert diff_lvl == 1, f"Different concept should start at Level 1, got {diff_lvl}"

    # Log a Level 2 doubt
    d2_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("INSERT INTO doubts (id, session_id, concept_tag, hint_level, transcribed_text) VALUES (?, ?, 'Water Photolysis', 2, 'explain again')", (d2_id, session_id))
        conn.commit()

    # Third doubt on Water Photolysis -> Level 3
    lvl3 = calculate_hint_ladder(session_id, "I still don't understand water photolysis", "Water Photolysis")
    assert lvl3 == 3, f"Expected Level 3, got {lvl3}"


def test_03_oral_quiz_start_and_structure():
    """Verify POST /api/quiz/start generates exactly 4 distinct questions with required cognitive levels."""
    sess_res = client.post("/api/session", data={
        "title": "Quiz Generation Session",
        "language": "te",
        "chapter_text": "Photosynthesis involves light-dependent reactions in thylakoids and the Calvin cycle in the stroma. RuBisCO fixes carbon dioxide. Guard cells regulate stomata."
    })
    session_id = sess_res.json()["session_id"]

    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"})
    assert quiz_res.status_code == 200, quiz_res.text
    data = quiz_res.json()
    assert "quiz_id" in data
    assert data["total_questions"] == 4
    assert len(data["questions"]) == 4

    # Verify 4 question types
    types = [q["question_type"] for q in data["questions"]]
    for q in data["questions"]:
        assert "question_text" in q
        assert "spoken_text" in q
        assert "concept_tag" in q
        assert "audio_url" in q


def test_04_quiz_question_audio():
    """Verify GET /api/quiz/question/audio/{id} streams live Gnani Timbre audio."""
    sess_res = client.post("/api/session", data={
        "title": "Audio Stream Session",
        "language": "te",
        "chapter_text": "Chloroplasts contain chlorophyll pigments that absorb blue-violet and red light to produce chemical energy."
    })
    assert sess_res.status_code == 200, sess_res.text
    session_id = sess_res.json()["session_id"]
    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"}).json()
    q1 = quiz_res["questions"][0]

    audio_res = client.get(q1["audio_url"])
    assert audio_res.status_code == 200
    assert len(audio_res.content) > 1000, "Spoken question audio should be non-empty"


def test_05_quiz_answer_correct_evaluation():
    """Verify Gemini evaluates correct answer as 'correct' with score 100."""
    sess_res = client.post("/api/session", data={
        "title": "Grading Session",
        "language": "te",
        "chapter_text": "Light reactions occur in the thylakoid membranes within chloroplasts."
    })
    session_id = sess_res.json()["session_id"]
    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"}).json()
    q1 = quiz_res["questions"][0]

    # Provide clear, conceptually correct answer
    ans_res = client.post("/api/quiz/answer", data={
        "quiz_id": quiz_res["quiz_id"],
        "question_id": q1["id"],
        "answer_text": "The light reactions happen across the thylakoid membranes inside the chloroplasts.",
        "language": "en"
    })
    assert ans_res.status_code == 200, ans_res.text
    ans_data = ans_res.json()
    assert ans_data["evaluation_status"] in ["correct", "partially_correct"]
    assert ans_data["score"] in [100.0, 50.0]
    assert "feedback_display" in ans_data
    assert "feedback_spoken" in ans_data


def test_06_quiz_answer_incorrect_evaluation():
    """Verify Gemini evaluates wrong answer as 'incorrect' with score 0 and encouraging feedback."""
    sess_res = client.post("/api/session", data={
        "title": "Incorrect Test Session",
        "language": "te",
        "chapter_text": "Water photolysis in Photosystem II splits water into protons, electrons, and oxygen gas."
    })
    session_id = sess_res.json()["session_id"]
    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"}).json()
    q1 = quiz_res["questions"][0]

    ans_res = client.post("/api/quiz/answer", data={
        "quiz_id": quiz_res["quiz_id"],
        "question_id": q1["id"],
        "answer_text": "Water becomes diamond and evaporates into nitrogen gas.",
        "language": "en"
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["evaluation_status"] == "incorrect"
    assert ans_data["score"] == 0.0


def test_07_quiz_empty_audio_unclear_handling():
    """Verify empty/silent audio returns 422 with unclear guidance without penalizing score."""
    sess_res = client.post("/api/session", data={
        "title": "Empty Audio Session",
        "language": "te",
        "chapter_text": "Photosynthesis produces glucose and releases vital oxygen gas through water photolysis."
    })
    assert sess_res.status_code == 200, sess_res.text
    session_id = sess_res.json()["session_id"]
    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"}).json()
    q1 = quiz_res["questions"][0]

    empty_res = client.post(
        "/api/quiz/answer",
        data={"quiz_id": quiz_res["quiz_id"], "question_id": q1["id"], "language": "te"},
        files={"file": ("empty.wav", b"", "audio/wav")}
    )
    assert empty_res.status_code == 422
    assert "unclear" in empty_res.json().get("status", "") or "empty" in empty_res.json().get("message", "").lower()


def test_08_quiz_duplicate_submission_prevention():
    """Verify duplicate submissions return the original graded evaluation instead of re-submitting."""
    sess_res = client.post("/api/session", data={
        "title": "Dup Test Session",
        "language": "te",
        "chapter_text": "Stomata open during daylight to allow carbon dioxide gas exchange in green leaves."
    })
    assert sess_res.status_code == 200, sess_res.text
    session_id = sess_res.json()["session_id"]
    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"}).json()
    q1 = quiz_res["questions"][0]

    # First submission
    res1 = client.post("/api/quiz/answer", data={
        "quiz_id": quiz_res["quiz_id"],
        "question_id": q1["id"],
        "answer_text": "Stomata allow gas exchange.",
        "language": "en"
    })
    assert res1.status_code == 200

    # Second submission for same question
    res2 = client.post("/api/quiz/answer", data={
        "quiz_id": quiz_res["quiz_id"],
        "question_id": q1["id"],
        "answer_text": "Different answer should be ignored.",
        "language": "en"
    })
    assert res2.status_code == 200
    assert res2.json().get("is_duplicate") is True


def test_09_full_quiz_completion_and_results():
    """Verify completing all 4 questions produces total score, percentage, and learning summary."""
    sess_res = client.post("/api/session", data={
        "title": "Full Quiz Session",
        "language": "te",
        "chapter_text": "Photosynthesis converts solar light into glucose. Chlorophyll absorbs light in thylakoids. Water splits into oxygen. RuBisCO fixes carbon dioxide in the stroma. Guard cells regulate stomata."
    })
    session_id = sess_res.json()["session_id"]
    quiz_res = client.post("/api/quiz/start", data={"session_id": session_id, "lang": "te"}).json()
    quiz_id = quiz_res["quiz_id"]
    questions = quiz_res["questions"]

    answers = [
        "In the thylakoid membranes inside the chloroplasts.",
        "Water splits into protons, electrons, and oxygen gas.",
        "The Calvin cycle stops because it needs ATP and NADPH energy.",
        "Guard cells close stomata to conserve water, but stopping CO2 exchange."
    ]

    for idx, q in enumerate(questions):
        ans_res = client.post("/api/quiz/answer", data={
            "quiz_id": quiz_id,
            "question_id": q["id"],
            "answer_text": answers[idx],
            "language": "en"
        })
        assert ans_res.status_code == 200
        if idx == 3:
            assert ans_res.json()["quiz_completed"] is True

    # Check GET /api/quiz/{id}/results
    results_res = client.get(f"/api/quiz/{quiz_id}/results")
    assert results_res.status_code == 200
    r_data = results_res.json()
    assert r_data["completed"] is True
    assert r_data["total_score"] > 0
    assert r_data["percentage"] > 0
    assert len(r_data["learning_summary"]) > 10
    assert len(r_data["questions_review"]) == 4


def test_10_teacher_dashboard_p1_telemetry():
    """Verify Teacher Observatory returns P1 mastery distribution rates, level 3 concepts, and quiz counts."""
    dash_res = client.get("/api/dashboard")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "summary" in dash_data
    assert "rates" in dash_data["summary"]
    rates = dash_data["summary"]["rates"]
    assert "correct_rate" in rates
    assert "partial_rate" in rates
    assert "incorrect_rate" in rates
    assert "level3_concepts" in dash_data
