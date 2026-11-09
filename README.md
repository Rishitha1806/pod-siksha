# Pod-Siksha 2.0 — Aura Atelier (Voice-First AI Learning Platform)

> **Tagline:** A classroom podcast that listens. Students interrupt in their own language, explain concepts back, and master ideas with cognitive telemetry.  
> **Technologies:** Gnani AI (Prisma STT v3.0, Timbre TTS v3.0), Google Gemini API (`gemini-3.5-flash-lite`), FastAPI, SQLite3, HTML5 / Web Audio API.  
> **Design Identity:** Aura Atelier / Vedic Lumina (Museum Parchment, Kalamkari Emerald-Black, Surya Gold, Terracotta Ochre, Nilgiri Celadon). Strict Light Theme.  
> **Status:** Live & Production Ready (42/42 Tests Passing).

---

## 1. Overview & Vision

Pod-Siksha 2.0 is an autonomous, multilingual, voice-first learning platform built for the **Gnani AI Internship Challenge 2026**. It transforms static textbooks into an interactive Socratic dialogue between two distinct AI hosts, listens when learners interrupt, and introduces deep cognitive feedback loops:

1. **Authentic 14-Turn Socratic Dialogue**: Generates engaging two-host dialogue from uploaded PDFs or chapter text. Host A (Yash / Explainer) and Host B (Priya / Inquisitive Co-Host) speak using distinct Gnani Timbre voices (`Shivani` and `Yashraj`).
2. **Tactile Spacebar Interruption (~180ms Latency)**: Pressing and holding Spacebar or the on-screen mic immediately halts the podcast audio, captures student doubts in regional languages (Telugu, Hindi, Tamil, Kannada, Marathi, Bengali), transcribes via Gnani Prisma STT, answers via Gemini grounded exclusively in textbook evidence, and resumes audio at the exact millisecond.
3. **Physical Audio Playback Engine**: Solved the silent playback issue by sanitizing streaming WAV headers (`len-8` and `len-44` linear PCM recalculation) and implementing dedicated streaming GET/POST endpoints. Includes a 3-tone Web Audio harmonic chime test to physically verify laptop speakers.
4. **Concept DNA Knowledge Topology**: Extracts concept dependency graphs cached in SQLite, mapping prerequisite paths and real-time mastery scores computed from learner interactions.
5. **Teach-Back Mode**: Prompts students to explain concepts back in their own words. An educational diagnostic evaluates semantic comprehension, categorizing understood concepts, diagnosing false mental models, and quantifying mastery deltas.
6. **Misconception Radar & Memory Loop**: Diagnoses specific student misconceptions and schedules adaptive spaced revision intervals (24h, 72h, 168h) to resolve conceptual friction.
7. **Sovereign Learner Authentication**: Built-in authentication using PBKDF2-HMAC-SHA256 password hashing with per-user salt, persistent token sessions, user-level data isolation, and secure password recovery.

---

## 2. Architecture Diagram

```
                        POD-SIKSHA 2.0 ARCHITECTURE
                        
      +---------------------------------------------------------------+
      |             Learner Browser (Aura Atelier UI)                 |
      |   HTML5 Linear PCM Audio • Web Audio API • Tactile Spacebar   |
      +---------------------------------------------------------------+
                                      |
       REST API / Web Audio Stream    |    Bearer Token Session
                                      v
      +---------------------------------------------------------------+
      |                 FastAPI Server (server.py:8008)               |
      +---------------------------------------------------------------+
           |                     |                      |
           v                     v                      v
  +-----------------+   +------------------+   +-------------------+
  |   Gnani AI      |   |  Google Gemini   |   |   SQLite Database |
  | Prisma STT v3.0 |   | 3.5 Flash Lite   |   |   (pod_siksha.db) |
  | Timbre TTS v3.0 |   | Socratic Hints   |   | Sessions, Users,  |
  | Shivani/Yashraj |   | Semantic Eval    |   | DNA, Teach-Back,  |
  | Sanitized WAV   |   | Concept DNA      |   | Misconceptions    |
  +-----------------+   +------------------+   +-------------------+
```

---

## 3. The 9 Approved Production Screens

1. **Landing Sanctuary** (`/` -> `#landing`): Editorial overview of the Vedic Lumina architecture, live audio verification chime, and cognitive loop steps.
2. **Learner Login** (`#login`): Clean authentication panel with show/hide password toggle and secure session creation.
3. **Account Registration** (`#register`): Seamless learner onboarding with language preference selection.
4. **Personal Learning Atelier** (`#home`): Dashboard showing resume episode cards, active sessions, and quick chapter upload.
5. **Personal Learning Insights** (`#insights`): Real-time cognitive telemetry featuring an SVG circular mastery ring, concept breakdown tracks, misconception radar, and spaced repetition queue.
6. **Learning Studio** (`#studio`): The acoustic stage featuring dual-host audio playback, 14-turn segmented timeline, synchronized transcript teleprompter, and tactile Spacebar interruption.
7. **Cognitive Desk** (`#workspace`): Side-by-side textbook citations with interactive oral quiz questions.
8. **Concept DNA** (`#concept-dna`): Interactive visual topology graph linking prerequisites, dependencies, and mastery indicators.
9. **Teach-Back Mode** (`#teachback`): Socratic challenge console where learners explain ideas back to Host B with structured semantic diagnostics.

---

## 4. Getting Started & Running Locally

### Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

### Installation
```bash
git clone https://github.com/your-org/pod-siksha.git
cd pod-siksha

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Configure your `.env` file (keys are already pre-configured for testing):
```ini
GNANI_API_KEY=your_gnani_api_key
GEMINI_API_KEY=your_gemini_api_key
PORT=8008
```

### Running the Server
```bash
python server.py
```
Open **`http://127.0.0.1:8008/`** in your browser.

---

## 5. Automated Test Suite

Pod-Siksha 2.0 maintains a 100% passing test suite across all 4 modules:

```bash
# Run all tests
pytest tests/ -v
```

- **`tests/test_p0.py`** (10/10): Database schema, PDF extraction, 14-turn generation, Gnani Timbre TTS, Gnani Prisma STT, interruption audio privacy.
- **`tests/test_p1.py`** (10/10): Concept normalization, progressive hint ladder, oral quiz runner, spoken feedback, duplicate submission prevention.
- **`tests/test_p2.py`** (10/10): Teacher observatory, concept severity ranking, classroom filtering, downloadable CSV exports, production health check.
- **`tests/test_v2_features.py`** (12/12): PBKDF2 authentication, token sessions, data isolation, Concept DNA graph, Teach-Back semantic evaluation, Misconception Radar, Memory Loop, and linear PCM WAV header sanitization.

**Total: 42/42 tests passing.**

---

## 6. Deployment Configurations

- **Cloudflare Tunnel:** Active public HTTPS endpoint routing to local server.
- **Vercel Serverless:** Configured with `vercel.json` and ASGI handler `api/index.py`.
- **Hot Backup Utility:** Run `python scripts/backup_db.py` to produce a verified SQLite database snapshot.
