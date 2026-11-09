# Pod-Siksha — A Classroom Podcast That Listens

> **Tagline:** A classroom podcast that listens. Students interrupt in their own language, and teachers see where the class got stuck.  
> **Technologies:** Gnani AI (Prisma STT v3.0, Timbre TTS v3.0), Google Gemini API (`gemini-3.5-flash-lite`), FastAPI, SQLite3, Vanilla JavaScript, Web Audio API.  
> **Design Identity:** Saffron Frequency (Strict Light Theme).

---

## Overview

Pod-Siksha is a multilingual, interruptible, two-host AI classroom podcast that:
1. **Teaches uploaded textbook chapters** (PDF or text) through natural 14-turn dialogues between two distinct AI hosts.
2. **Speaks in regional Indic languages** (Telugu, Hindi, Tamil, Kannada, Marathi, Bengali) code-mixed with English scientific terminology using **Gnani Timbre TTS v3.0** (`Shivani` for Host A, `Yashraj` for Host B).
3. **Listens when students interrupt**: Holding the tactile **HOLD TO ASK** button or the **Spacebar** instantly pauses the audio playback (~200ms target) and records student doubts via Web Audio API.
4. **Transcribes and grounds doubts**: Spoken questions are transcribed with **Gnani Prisma STT v3.0** (`https://api.vachana.ai/stt/v3`), analyzed against the chapter using **Google Gemini 3.5**, and answered warmly with a progressive 3-level hint ladder.
5. **Exact resume**: The podcast resumes playback from the exact millisecond where it paused.
6. **Teacher Observatory**: Provides educators with live concept confusion radars, friction scores ($2 \times \text{doubts} + 3 \times \text{quiz mistakes}$), and downloadable session study transcripts.

---

## Architecture

```
Student Browser (Vanilla JS + Web Audio API)
       │
       ├─ [Space / Hold to Ask] ──────> 200ms Audio Pause + 16kHz PCM WAV Recording
       │
       ▼
FastAPI Backend (server.py, port 8008)
       │
       ├─► Gnani Prisma STT v3.0 (vachana.ai/stt/v3) ────► Transcribes student doubt
       ├─► Google Gemini 3.5 (gemini-3.5-flash-lite) ────► Grounds answer in chapter + Hint Ladder
       ├─► Gnani Timbre TTS v3.0 (vachana.ai/.../tts) ───► Host A (Shivani) / Host B (Yashraj)
       └─► SQLite (pod_siksha.db) ───────────────────────► Anonymous telemetry (Zero audio on disk)
```

---

## Local Run Instructions

### 1. Requirements & Setup
```bash
cd C:\Users\jvris\Downloads\pod-siksha
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Make sure `.env` contains:
```env
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-3.5-flash-lite
GNANI_API_KEY=your_gnani_api_key
GNANI_STT_URL=https://api.vachana.ai/stt/v3
GNANI_TTS_URL=https://api.vachana.ai/api/v1/tts/inference
GNANI_VOICE_A=Shivani
GNANI_VOICE_B=Yashraj
GNANI_STT_FILE_FIELD=audio_file
GNANI_STT_LANG_FIELD=language_code
PORT=8008
```

### 3. Launch Backend & Frontend Server
```bash
python server.py
```
Open your browser at:
- **Student Podcast Studio:** [http://localhost:8008](http://localhost:8008)
- **Teacher Observatory:** [http://localhost:8008/teacher](http://localhost:8008/teacher)

### 4. Run Automated Test Suite
```bash
pytest tests/test_p0.py -v
```

---

## Sample Chapter Included
- Text format: `sample_chapter.txt` (~400 words on Photosynthesis, light reactions, Calvin cycle, ATP/NADPH, stomata).
- PDF format: `sample_chapter.pdf` (Formatted letter PDF ready for upload).
