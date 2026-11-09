# Pod-Siksha — Phase P2 Implementation Plan
## Teacher Intelligence, Learning Analytics & Public Deployment

**Project Directory:** `C:\Users\jvris\Downloads\pod-siksha`  
**Current Accepted Baseline:** Phase P0 (15/15 Acceptance Criteria Passed) & Phase P1 (20/20 Pytest Suite Passed, 7/7 Browser Steps Passed)  
**Baseline Verification Result:** `20 passed, 1 warning in 127.76s` (0 regressions).

---

## 1. Architectural Architecture & Objectives

Pod-Siksha Phase P2 extends the dual-host interruptible classroom podcast and oral quiz platform into a comprehensive, production-grade learning intelligence and public deployment ecosystem:

```
+---------------------------------------------------------------------------------------------------+
|                                       STUDENT APPLICATION                                         |
|  - 14-turn dual-host audio podcast (Shivani & Yashraj)                                            |
|  - Spacebar / Tap interruption with in-memory 16kHz WAV STT                                       |
|  - 4-Question oral quiz with 3-level progressive hint ladder                                      |
|  - NEW: Individual Anonymous Student Study Report Screen (/report?session_id=...)                 |
|  - NEW: Student Study Report PDF / CSV Export                                                     |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                      POD-SIKSHA BACKEND                                           |
|  - FastAPI (Python 3.10/3.11) with Uvicorn                                                        |
|  - Database: SQLite (pod_siksha.db) with parameterized queries, indexes, and additive tables     |
|  - Live Integrations:                                                                             |
|      * Gnani Prisma STT v3.0 (codemix voice-to-text in-memory)                                    |
|      * Gnani Timbre TTS v3.0 (Shivani Host A & Yashraj Host B linear PCM streaming)               |
|      * Google Gemini (gemini-3.5-flash-lite / gemini-2.5-flash)                                   |
|  - NEW Endpoints:                                                                                 |
|      * GET /api/teacher/analytics (Deep concept confusion, severity scoring, filters)             |
|      * GET /api/teacher/recommendations (Grounded Gemini pedagogical interventions)                |
|      * GET /api/teacher/export/csv (Classroom overview, concept friction & quiz summary)           |
|      * GET /api/student/{session_id}/report (Comprehensive anonymous session report)              |
|      * GET /api/student/{session_id}/export/csv (Individual student doubt & quiz history CSV)     |
|      * GET /api/health (Production readiness & telemetry probe)                                   |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                  ENHANCED TEACHER OBSERVATORY                                     |
|  - Full Classroom Overview (Real metrics, completed quiz counts, accuracy rates)                  |
|  - Concept Confusion Intelligence (Severity formula, doubt count, error count, hint escalation)   |
|  - Saffron Learning Friction Radar (Color-coded friction quadrants)                               |
|  - Level 3 Hint Bottleneck Analysis (Specific pedagogical remediation recommendations)            |
|  - Grounded AI Recommendations (Explicit citation of supporting database counts)                  |
|  - Downloadable Classroom CSV Reports (One-click sanitized download)                              |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Database Schema & Migration Requirements (Additive Only)

### Existing Tables (Preserved):
- `sessions`: Uploaded chapter content, 14-turn script JSON, selected language, timestamps.
- `doubts`: Transcribed doubt, playback position, concept tag, hint level (1, 2, 3), answered text.
- `quiz_results`: Legacy quiz answer items.
- `quiz_sessions`: Oral quiz instance, total score (/400), completed flag (0/1), learning summary.
- `quiz_questions`: 4 questions per quiz (Basic, Conceptual, Application, Reasoning), ideal answer, concept.
- `quiz_answers`: Student transcript, evaluation status (`correct`, `partially_correct`, `incorrect`), score, feedback.
- `concept_events`: Normalized events log for doubts and quiz responses.

### P2 Additive Schema & Optimization:
1. **Teacher Recommendation Cache Table (`teacher_recommendations`)**:
   ```sql
   CREATE TABLE IF NOT EXISTS teacher_recommendations (
       id TEXT PRIMARY KEY,
       chapter_filter TEXT DEFAULT 'all',
       concept TEXT NOT NULL,
       recommendation TEXT NOT NULL,
       evidence TEXT NOT NULL,
       action TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```
2. **Query Performance Indexes**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_doubts_session ON doubts(session_id);
   CREATE INDEX IF NOT EXISTS idx_doubts_concept ON doubts(concept_tag);
   CREATE INDEX IF NOT EXISTS idx_quiz_answers_session ON quiz_answers(quiz_session_id);
   CREATE INDEX IF NOT EXISTS idx_quiz_answers_status ON quiz_answers(evaluation_status);
   CREATE INDEX IF NOT EXISTS idx_quiz_sessions_completed ON quiz_sessions(completed);
   CREATE INDEX IF NOT EXISTS idx_sessions_language ON sessions(language);
   CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);
   ```

---

## 3. Detailed Feature Design

### Feature A: Advanced Teacher Observatory (`/teacher`)
- **Classroom Overview Cards**:
  - Total learning sessions (count of `sessions`).
  - Total doubts asked (count of `doubts`).
  - Total completed quizzes (count of `quiz_sessions WHERE completed = 1` ONLY; strictly excludes abandoned attempts).
  - Average quiz score (average percentage over completed quizzes).
  - Accuracy breakdown: Correct %, Partially Correct %, Incorrect %.
  - Concepts requiring immediate attention (count of concepts with Severity Index $\ge 15$).
- **Concept Confusion Intelligence**:
  - Transparent severity formula:
    $$\text{Severity Index} = (\text{Doubts} \times 2) + (\text{Incorrect} \times 3) + (\text{Partial} \times 1.5) + (\text{Level 3 Hints} \times 3)$$
  - Severity classification:
    - *High Confusion* ($\ge 15$)
    - *Moderate Confusion* ($7 - 14$)
    - *Improving* ($3 - 6$)
    - *Well Understood* ($< 3$)
  - Details per concept: Total doubts, incorrect answers, partial answers, correct answers, average hint level reached, distinct sessions affected, and primary confusion reason.
- **Learning Friction Radar**:
  - Interactive grid categorized into the 4 severity quadrants matching the Saffron Frequency palette (Terracotta `#E8794F`, Saffron Gold `#E8B94F`, Botanical Sage `#8BA99A`, Forest Ink `#263C35`).
- **Level 3 Hint Analysis**:
  - Filtered table isolating concepts where students required a complete explanation after struggling through Levels 1 and 2.
  - Generates concrete pedagogical suggestions (e.g. "Revisit Calvin cycle carbon fixation equation in stroma").
- **Recent Classroom Activity Table**:
  - Anonymous session ID preview (`sess-31be...`), chapter title, selected language, doubt count, quiz completion status badge, score badge, and relative timestamp.
  - Zero PII exposed.

### Feature B: Grounded Teacher Recommendations (Gemini AI)
- Grounded strictly in aggregated SQLite statistics.
- Distinguishes observed empirical facts from AI suggestions:
  - *Observed Evidence*: "6 students asked doubts on Water Photolysis, 4 reached Level 3, and quiz error rate was 75%."
  - *Actionable Suggestion*: "Demonstrate the Z-scheme electron transport diagram and emphasize why photosystem II requires continuous electron replenishment from H2O splitting."
- Caching: Recommendations cached in memory / SQLite for 10 minutes to minimize redundant LLM calls; regenerable on demand via a "Refresh Insights" button.
- Empty State: If fewer than 2 student events exist, returns a clear, transparent empty state: *"Insufficient classroom data to generate reliable recommendations. Encourage at least two students to complete the podcast or oral quiz."*

### Feature C: Individual Student Study Report (`/static/report.html` & API)
- Accessible via `/report?session_id=<UUID>` or directly linked from the podcast completion screen.
- Session Summary: Anonymous session ID, chapter studied, language used, date, turns completed, total doubts, quiz outcome.
- Doubt History: Timestamp, question asked, normalized concept tag, hint level escalated to, and answer text provided by tutor.
- Quiz Breakdown: 4 questions, cognitive type, student answer transcript, evaluation badge (`correct`, `partially_correct`, `incorrect`), score, and feedback text.
- Learning Progress: Dynamic categorization into **Mastered Concepts**, **Review Recommended**, and personalized next steps.
- Persistence: Hydrated directly from backend SQLite endpoints (`GET /api/student/{session_id}/report`). Survives browser storage clearing and device switching.

### Feature D: Classroom Performance Comparison & Filters
- Interactive filters on the Teacher Observatory:
  - Chapter filter (dynamic list of distinct session titles).
  - Language filter (`All`, `Telugu`, `Hindi`, `English`, etc.).
  - Date filter (`All Time`, `Today`, `Last 7 Days`).
- Comparative concept chart/table displaying:
  - Concept-wise average score.
  - Concept-wise error rate.
  - Doubt frequency.
  - Sample size warning: If a concept has fewer than 3 responses, flags with a *"Small Sample"* badge to prevent premature teacher conclusions.

### Feature E: Downloadable Reports (CSV)
- **Classroom Summary CSV (`/api/teacher/export/csv`)**:
  - File name: `pod_siksha_classroom_analytics_YYYYMMDD.csv`
  - Columns: `Concept`, `Severity_Category`, `Severity_Score`, `Total_Doubts`, `Quiz_Correct`, `Quiz_Partial`, `Quiz_Incorrect`, `Level3_Escalations`, `Sessions_Affected`, `Primary_Friction_Reason`.
  - Sanitization: All string fields sanitized against CSV injection (`=`, `+`, `-`, `@` escaped with single quote).
- **Individual Student Study Report CSV (`/api/student/{session_id}/export/csv`)**:
  - File name: `pod_siksha_student_report_{session_id[:8]}.csv`
  - Columns: `Type` (Doubt/Quiz), `Index`, `Concept`, `Prompt_Or_Question`, `Student_Input`, `Evaluation_Or_Hint_Level`, `Score`, `Timestamp`.

---

## 4. Production Deployment & Persistence Strategy

### Evaluation of Hosting Providers:
1. **Option A: Public HTTPS Tunnel (Cloudflare Tunnel / Cloudflared)**
   - *Pros*: Zero cold starts, 100% native access to the running Python 3.10 backend, local persistent SQLite database (`pod_siksha.db`) preserves all records with 0 risk of cloud ephemeral disk wiping, zero costs, instant deployment with valid SSL/TLS HTTPS certificate on `trycloudflare.com`.
   - *Cons*: Dependent on local host uptime.
2. **Option B: Railway / Render**
   - *Pros*: Hosted in the cloud.
   - *Cons*: Free tiers on Render do NOT support persistent disks for SQLite (ephemeral filesystem wipes `pod_siksha.db` on restart); Railway requires a paid subscription ($5/mo) for persistent volumes.
3. **Recommended Hybrid Production Deployment**:
   - Primary: Stand up a dedicated, persistent **Cloudflare HTTPS Public Tunnel** via `cloudflared` to expose the FastAPI service publicly at a secure HTTPS URL.
   - Prepare full production container assets (`Dockerfile`, `docker-compose.yml`, `Procfile`, `requirements.txt`, `.env.example`, `gunicorn_conf.py`) for cloud portability.

---

## 5. Security & Privacy Hardening

1. **Session Isolation**: Student report endpoints strictly validate `session_id` against the database; no enumeration of other students' data.
2. **Audio Ephemerality**: Student voice recordings are streamed as in-memory WAV buffers to Gnani Prisma STT and discarded immediately after transcription. Zero audio bytes written to disk.
3. **No PII**: All database records and logs use random UUIDv4 identifiers. Zero names, phone numbers, emails, or student IDs collected.
4. **CORS & Input Validation**: Strict payload bounds on file uploads (max 10MB for PDFs, max 5MB for WAVs).
5. **No Secrets Exposed**: Frontend scripts query server endpoints; API keys (`GNANI_API_KEY`, `GEMINI_API_KEY`) remain strictly in server environment variables.

---

## 6. Testing & Quality Assurance Matrix

1. **Regression Testing**:
   - Re-run `tests/test_p0.py` (10 tests).
   - Re-run `tests/test_p1.py` (10 tests).
2. **New Phase P2 Automated Test Suite (`tests/test_p2.py`)**:
   - `test_01_advanced_teacher_analytics_calculation`: Verifies accurate counts, exclusion of incomplete quizzes, and correct rate math.
   - `test_02_concept_severity_ranking`: Verifies transparent weighting formula.
   - `test_03_level3_hint_aggregation`: Verifies identification of Level 3 bottleneck concepts.
   - `test_04_teacher_recommendations_grounding`: Verifies that Gemini recommendations cite genuine database counts and handle empty state gracefully.
   - `test_05_student_study_report_isolation`: Verifies that `/api/student/{session_id}/report` returns full history and rejects invalid IDs.
   - `test_06_classroom_filters`: Tests chapter, language, and date range filters.
   - `test_07_csv_export_classroom`: Tests CSV header integrity, values matching SQLite, and filename safety.
   - `test_08_csv_export_student`: Tests individual student CSV download.
   - `test_09_production_health_check`: Tests `/api/health` probe.
   - `test_10_database_backup_integrity`: Tests automated database backup script and file verification.
3. **End-to-End Acceptance Audit (`tests/run_p2_acceptance_audit.py`)**:
   - Automated Selenium Chrome suite validating the full live journey on the public HTTPS URL.
   - Captures all required screenshots in `docs/screenshots/`.
