# Pod-Siksha — Phase P1 Implementation Plan
## Progressive Learning, Oral Quiz & Concept Intelligence

**Date:** November 9, 2026  
**Status:** In Progress (Baseline P0: 10/10 Tests Passed, 15/15 Acceptance Criteria Verified)  
**Author:** Principal Software Architect & Lead AI Engineer  

---

## 1. Existing Architecture & Baseline Capabilities

### Current Stack:
- **Backend:** Python 3.11 / FastAPI / SQLite3 (standard library, zero ORM) / `pypdf` / `google-genai` / `httpx`.
- **Speech Engine:** Gnani Prisma STT v3.0 (`prisma-v3.0`), Gnani Timbre TTS v3.0 (`timbre-v3.0`, `Shivani` for Host A, `Yashraj` for Host B).
- **Reasoning Engine:** Google Gemini API (`gemini-3.5-flash-lite`, with fallback to `gemini-2.5-flash`).
- **Frontend:** Vanilla JavaScript, HTML5 Audio API, Web Audio API, CSS.
- **Theme:** "Saffron Frequency" (Strict Light Theme: Ivory Paper `#F7F3E9`, Forest Ink `#263C35`, Terracotta `#E8794F`, Saffron Gold `#E8B94F`).
- **Privacy:** In-memory audio processing; zero student microphone recordings on disk.

### P0 Verified Functionality:
- 14-turn podcast generation from PDF/text.
- Dual-voice playback with next-turn in-memory prefetch.
- Tactile "Hold to Ask" and Spacebar interruption with 1ms pause latency and exact millisecond resume.
- Chapter-grounded doubt resolution with live Prisma STT transcription and Host A Timbre spoken explanations.

---

## 2. Proposed Additive Database Schema

To support structured oral quizzes, per-concept hint ladders, and teacher concept intelligence without breaking existing records, we introduce clean additive SQLite tables:

### Table 1: `quiz_sessions`
- `id` TEXT PRIMARY KEY
- `session_id` TEXT (FOREIGN KEY `sessions.id`)
- `language` TEXT
- `total_questions` INTEGER DEFAULT 4
- `total_score` REAL DEFAULT 0.0
- `percentage` REAL DEFAULT 0.0
- `completed` INTEGER DEFAULT 0
- `learning_summary` TEXT
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `completed_at` TIMESTAMP

### Table 2: `quiz_questions`
- `id` TEXT PRIMARY KEY
- `quiz_session_id` TEXT (FOREIGN KEY `quiz_sessions.id`)
- `question_number` INTEGER (1 to 4)
- `question_type` TEXT ('basic', 'conceptual', 'application', 'reasoning')
- `question_text` TEXT (English visible text)
- `spoken_text` TEXT (Regional language text)
- `expected_answer` TEXT
- `concept_tag` TEXT
- `difficulty` TEXT
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Table 3: `quiz_answers`
- `id` TEXT PRIMARY KEY
- `quiz_question_id` TEXT (FOREIGN KEY `quiz_questions.id`)
- `quiz_session_id` TEXT
- `transcript` TEXT
- `evaluation_status` TEXT ('correct', 'partially_correct', 'incorrect')
- `score` REAL (100, 50, 0)
- `feedback_display` TEXT
- `feedback_spoken` TEXT
- `correct_points` TEXT (JSON array)
- `missing_points` TEXT (JSON array)
- `concept_tag` TEXT
- `ideal_answer` TEXT
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Table 4: `concept_events`
- `id` TEXT PRIMARY KEY
- `session_id` TEXT
- `concept_tag` TEXT
- `normalized_tag` TEXT
- `event_type` TEXT ('doubt', 'quiz')
- `hint_level` INTEGER
- `quiz_status` TEXT
- `score` REAL
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 3. Detailed Feature Specifications

### Feature A — Progressive Hint Ladder
- **Concept-Specific Tracking:** Each session maintains a separate ladder for each concept tag (e.g. `Water Photolysis` vs `Calvin Cycle`).
- **Level 1 (Guiding Question):** Encourages active recall, zero spoilers.
- **Level 2 (Meaningful Hint):** Supplies an analogy or structural clue.
- **Level 3 (Complete Explanation):** Crystal-clear explanation with scientific terms, followed by a comprehension check question.
- **Escalation Trigger:** Consecutive doubts on the same concept, or expressions of confusion ("still don't get it"), automatically escalate $L_1 \to L_2 \to L_3$.
- **Persistence:** Saved in `doubts` and `concept_events`.

### Feature B — 4-Question Spoken Oral Quiz
- Generated from the uploaded chapter by Gemini, containing:
  1. *Basic understanding*
  2. *Conceptual understanding*
  3. *Application-based*
  4. *Reasoning / explanation*
- Spoken by Host A (`Shivani`) using Gnani Timbre.
- Student answers via microphone (16kHz mono WAV encoded in memory via Web Audio).
- Spoken question audio pre-synthesized or streamed.

### Feature C — AI Answer Evaluation
- Transcribed via Gnani Prisma STT v3.0 (`audio_file`, `language_code`).
- Evaluated by Gemini with 3 strict categories:
  - `correct` (score: 100)
  - `partially_correct` (score: 50)
  - `incorrect` (score: 0)
- Conceptual understanding evaluated; ignores accent, dialect, or minor grammar slips.
- Spoken feedback synthesized via Gnani Timbre and played to student.
- Duplicate submission prevention: disables recording/submitting while in-flight.
- Empty audio handling: prompts student to repeat their answer without penalizing score.

### Feature D — Concept Intelligence & Normalization
- Concept Normalizer: Gemini or rule-based canonical mapping maps variants ("water splitting", "photolysis of water") to canonical concept `"Water Photolysis"`.
- Recorded in `concept_events`.

### Feature E — Student Quiz Results & Learning Summary
- Displayed immediately upon Question 4 completion:
  - Total score out of 400 & percentage
  - Breakdown: Correct, Partially Correct, Incorrect counts
  - Strong Concepts list vs Needs Revision list
  - Gemini-generated personalized Learning Summary
  - Action buttons: "Review Answers", "Replay Podcast", "Return to Session"
- Persisted in SQLite; survives full page reload.

### Feature F — Teacher Observatory Integration
- Enhanced `/api/dashboard` and `teacher.html`:
  - Total quiz attempts & average class score.
  - Correct / Partial / Incorrect rate meters.
  - Most misunderstood concepts (quiz errors) vs most interrupted concepts (doubts).
  - High friction indicator (concepts requiring Level 3 hints).
  - Recent anonymous quiz records table.

---

## 4. Implementation Sequence

1. **Database Schema Setup:** Add `quiz_sessions`, `quiz_questions`, `quiz_answers`, and `concept_events` in `server.py:init_db()`.
2. **Concept Intelligence & Hint Ladder:** Implement normalized concept mapping and per-concept ladder escalation in `POST /api/ask`.
3. **Oral Quiz Generation:** Implement `POST /api/quiz/start`.
4. **Oral Answer Evaluation & Feedback:** Implement `POST /api/quiz/answer` with Prisma STT, Gemini grading, Timbre TTS feedback, and idempotency protection.
5. **Quiz Results API & Persistence:** Implement `GET /api/quiz/{quiz_id}/results`.
6. **Frontend Experience:** Upgrade `static/index.html` with the radio-style oral quiz studio and results card.
7. **Teacher Observatory Upgrade:** Upgrade `static/teacher.html` with P1 diagnostic cards.
8. **Automated & Browser Verification:** Run test suite and Selenium audit.

---

## 5. Regression Mitigation

- All P0 endpoints (`POST /api/session`, `POST /api/tts`, `POST /api/ask`, `GET /api/dashboard`) retain exact backward compatibility.
- Zero changes to P0 audio queue, prefetch mechanism, Space interruption, or Saffron Frequency styling.
- Baseline P0 tests (`tests/test_p0.py`) will be executed after each stage to guarantee 100% regression freedom.
