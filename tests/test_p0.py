"""Comprehensive P0 Verification Suite for Pod-Siksha.
Tests PDF extraction, Gemini 14-turn podcast generation, Gnani Timbre TTS (Host A and B),
Gnani Prisma STT doubt transcription, progressive hint ladder, and audio privacy.
"""
import io
import math
import os
import struct
import sys
import wave
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app, get_db, extract_text_from_pdf, call_gnani_tts, call_gnani_stt, call_gemini

client = TestClient(app)
client.headers["Authorization"] = "Bearer session_demo_learner_001"

def generate_test_wav(duration_sec=1.5, sample_rate=16000, freq=440.0) -> bytes:
    """Creates a valid 16kHz mono 16-bit PCM WAV in memory."""
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


def test_01_database_tables():
    """Verify SQLite database schema and tables."""
    with get_db() as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t["name"] for t in tables]
        assert "sessions" in table_names
        assert "doubts" in table_names
        assert "quiz_results" in table_names


def test_02_pdf_text_extraction():
    """Verify pypdf extraction from sample_chapter.pdf."""
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_chapter.pdf")
    assert os.path.exists(pdf_path), "sample_chapter.pdf should exist"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    extracted = extract_text_from_pdf(pdf_bytes)
    assert len(extracted) > 100
    assert "Photosynthesis" in extracted
    assert len(extracted) <= 14000


def test_03_create_session_from_text():
    """Verify 14-turn podcast generation via Gemini."""
    res = client.post("/api/session", data={
        "title": "Photosynthesis Basics",
        "language": "te",
        "chapter_text": "Photosynthesis transforms solar light energy into chemical energy inside chloroplasts. Chlorophyll absorbs blue-violet and red light. Water photolysis in thylakoid membranes releases oxygen. ATP and NADPH drive the Calvin cycle in the stroma to produce glucose."
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert "session_id" in data
    assert len(data["turns"]) == 14
    
    # Check turn constraints
    turns = data["turns"]
    for t in turns:
        assert t["speaker"] in ["A", "B"]
        assert "spoken_text" in t
        assert len(t["spoken_text"]) <= 220, f"Turn {t['turn_index']} exceeded 220 chars: {len(t['spoken_text'])}"
        assert "display_text" in t
        assert len(t["display_text"]) > 0
        assert "concept_tag" in t


def test_04_create_session_from_pdf():
    """Verify session creation by uploading PDF file."""
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_chapter.pdf")
    with open(pdf_path, "rb") as f:
        res = client.post(
            "/api/session",
            data={"language": "te", "title": "Photosynthesis PDF Test"},
            files={"file": ("sample_chapter.pdf", f, "application/pdf")}
        )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total_turns"] == 14


def test_05_gnani_timbre_tts_host_a():
    """Verify live Gnani Timbre TTS for Host A (Shivani voice)."""
    text = "నమస్కారం! ఈరోజు క్లాస్‌లో మనం ఫోటోసింథసిస్ గురించి నేర్చుకుందాం."
    audio = call_gnani_tts(text, language="te", speaker="A")
    assert len(audio) > 1000, "TTS audio bytes should be non-empty"
    assert audio.startswith(b"RIFF") or b"WAVE" in audio[:32] or len(audio) > 5000


def test_06_gnani_timbre_tts_host_b():
    """Verify live Gnani Timbre TTS for Host B (Yashraj voice)."""
    text = "అవును సర్, అసలు క్లోరోప్లాస్ట్‌లో లైట్ ఎనర్జీ ఎలా ట్రాప్ అవుతుందో చెప్పండి?"
    audio = call_gnani_tts(text, language="te", speaker="B")
    assert len(audio) > 1000, "TTS audio bytes should be non-empty"


def test_07_api_tts_endpoint():
    """Verify /api/tts endpoint response format."""
    res = client.post("/api/tts", json={
        "text": "Photosynthesis operates in two stages: light reactions and Calvin cycle.",
        "language": "en",
        "speaker": "A"
    })
    assert res.status_code == 200
    assert "audio/" in res.headers.get("content-type", "") or len(res.content) > 1000


def test_08_ask_doubt_interruption():
    """Verify doubt handling: STT transcription + chapter-grounded answer + TTS."""
    # First create a session
    sess_res = client.post("/api/session", data={
        "title": "Doubt Test Chapter",
        "language": "te",
        "chapter_text": "Water photolysis occurs when light strikes photosystem II. Water molecules are split into protons, electrons, and oxygen gas: 2H2O -> 4H+ + 4e- + O2."
    })
    session_id = sess_res.json()["session_id"]

    # Generate synthesized speech as input audio to guarantee valid speech
    question_audio = call_gnani_tts("వాటర్ స్ప్లిట్టింగ్ ఎలా జరుగుతుంది?", language="te", speaker="B")

    # Call /api/ask
    ask_res = client.post(
        "/api/ask",
        data={
            "session_id": session_id,
            "turn_index": 3,
            "playback_ms": 14200,
            "language": "te"
        },
        files={"file": ("student_doubt.wav", question_audio, "audio/wav")}
    )
    assert ask_res.status_code == 200, ask_res.text
    ans = ask_res.json()
    assert "transcript" in ans
    assert "display_text" in ans
    assert "spoken_text" in ans
    assert "concept_tag" in ans
    assert ans["hint_level"] in [1, 2, 3]


def test_09_audio_privacy_compliance():
    """Verify zero raw student audio files are saved on disk."""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    disallowed_files = []
    for root, _, files in os.walk(project_dir):
        if "venv" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith((".webm", ".ogg")) or ("student" in f.lower() and f.endswith(".wav")):
                disallowed_files.append(f)
    assert len(disallowed_files) == 0, f"Raw student audio found on disk: {disallowed_files}"


def test_10_teacher_dashboard_api():
    """Verify Teacher Observatory API returns metrics and confusion radar."""
    res = client.get("/api/dashboard", headers={"Authorization": "Bearer session_demo_teacher_001"})
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "friction_concepts" in data
    assert "recent_sessions" in data
