# Pod-Siksha: Phase P1 API Reference

This document provides complete request and response specifications for all Phase P1 endpoints in Pod-Siksha.

---

## 1. Start Oral Quiz
**`POST /api/quiz/start`**

Generates a structured 4-question oral quiz across 4 cognitive domains (Basic, Conceptual, Application, Reasoning) grounded strictly in the session's textbook chapter. Pre-synthesizes Question 1 audio via Gnani Timbre TTS (Shivani).

### Request
- **Content-Type:** `application/json`
```json
{
  "session_id": "string (UUID)"
}
```

### Response
- **Status:** `200 OK`
```json
{
  "quiz_id": "84c20131-e287-46fb-ab0f-d779475ade5e",
  "session_id": "31be9fa3-a81e-450a-b328-3e4b787595c5",
  "total_questions": 4,
  "questions": [
    {
      "id": "q1-uuid",
      "index": 1,
      "cognitive_type": "Basic",
      "concept": "Photosynthesis Overview",
      "question_text": "What are the primary reactants and products in the overall equation of photosynthesis?",
      "audio_url": "/api/quiz/question/audio/q1-uuid"
    },
    {
      "id": "q2-uuid",
      "index": 2,
      "cognitive_type": "Conceptual",
      "concept": "Water Photolysis",
      "question_text": "Why is water photolysis essential for the continuous flow of electrons in the thylakoid membrane?",
      "audio_url": "/api/quiz/question/audio/q2-uuid"
    },
    {
      "id": "q3-uuid",
      "index": 3,
      "cognitive_type": "Application",
      "concept": "Light Reactions",
      "question_text": "If a plant is kept in total darkness, which specific phase of photosynthesis halts immediately and why?",
      "audio_url": "/api/quiz/question/audio/q3-uuid"
    },
    {
      "id": "q4-uuid",
      "index": 4,
      "cognitive_type": "Reasoning",
      "concept": "Dark Reactions (Calvin Cycle)",
      "question_text": "Evaluate why calling the Calvin cycle a 'dark reaction' can be misleading despite not directly absorbing photons.",
      "audio_url": "/api/quiz/question/audio/q4-uuid"
    }
  ]
}
```

---

## 2. Stream Question Audio
**`GET /api/quiz/question/audio/{question_id}`**

Fetches or on-demand synthesizes the spoken question audio using Gnani Timbre TTS Host A (`Shivani`).

### Request
- **Path Parameter:** `question_id` (string)

### Response
- **Status:** `200 OK`
- **Content-Type:** `audio/wav`
- **Body:** Binary WAV audio stream (24kHz linear PCM)

---

## 3. Submit Spoken Quiz Answer
**`POST /api/quiz/answer`**

Transcribes student spoken answer using Gnani Prisma STT v3 (Telugu-English codemix support), evaluates comprehension with Google Gemini, assigns points (100, 50, or 0), and returns spoken audio feedback via Gnani Timbre TTS.

### Request
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `quiz_id`: string (UUID)
  - `question_id`: string (UUID)
  - `audio_file`: binary file (16kHz mono WAV), OR
  - `transcript_text`: string (optional fallback/direct input)

### Response
- **Status:** `200 OK`
```json
{
  "answer_id": "ans-uuid",
  "quiz_id": "84c20131-e287-46fb-ab0f-d779475ade5e",
  "question_id": "q1-uuid",
  "student_transcript": "Water and carbon dioxide are the reactants, and glucose and oxygen are the products.",
  "evaluation": "correct",
  "score": 100,
  "feedback_text": "Spot on! You accurately identified water and CO2 as inputs, yielding glucose and oxygen.",
  "feedback_audio_url": "/api/tts?speaker=Shivani&text=Spot+on%21+You+accurately+identified...",
  "completed_questions": 1,
  "total_questions": 4,
  "is_completed": false
}
```

### Error Responses
- **422 Unprocessable Entity:** When neither `audio_file` nor `transcript_text` is provided or audio is empty.
- **400 Bad Request:** If the question has already been answered in this quiz session.

---

## 4. Get Quiz Results
**`GET /api/quiz/{quiz_id}/results`**

Returns comprehensive performance metrics, score out of 400, percentage, conceptual mastery breakdown, and an actionable AI-generated learning summary.

### Request
- **Path Parameter:** `quiz_id` (string)

### Response
- **Status:** `200 OK`
```json
{
  "quiz_id": "84c20131-e287-46fb-ab0f-d779475ade5e",
  "session_id": "31be9fa3-a81e-450a-b328-3e4b787595c5",
  "total_score": 350,
  "max_score": 400,
  "percentage": 87.5,
  "status": "completed",
  "strong_concepts": ["Water Photolysis", "Light Reactions", "Photosynthesis Overview"],
  "needs_revision": ["Dark Reactions (Calvin Cycle)"],
  "learning_summary": "Great conceptual grasp of the light-dependent reactions and energetic equations! Focus next on review of ATP/NADPH consumption during carbon fixation in the stroma.",
  "answers": [
    {
      "question_id": "q1-uuid",
      "cognitive_type": "Basic",
      "concept": "Photosynthesis Overview",
      "score": 100,
      "evaluation": "correct",
      "student_transcript": "Water and CO2 react to form glucose and oxygen."
    }
  ]
}
```

---

## 5. Ask Doubt with 3-Level Progressive Hint Ladder
**`POST /api/ask`** (Enhanced in P1)

When a student interrupts or asks a doubt, the system identifies the concept, consults the session's doubt history for that concept, and serves the appropriate tier:
- **Level 1 (First doubt):** Guiding question pointing student toward self-discovery.
- **Level 2 (Second doubt / persistent confusion):** Concrete hints and partial analogies.
- **Level 3 (Third doubt / deep struggle):** Complete, explicit explanation.

### Request
- **Content-Type:** `multipart/form-data`
  - `session_id`: string
  - `audio_file`: binary file (optional)
  - `text`: string (optional)
  - `language`: string (e.g. `te`, `hi`, `en`)

### Response
- **Status:** `200 OK`
```json
{
  "doubt_id": "doubt-uuid",
  "query_text": "water splitting ela jarugutundi?",
  "concept": "Water Photolysis",
  "hint_level": 1,
  "answer_text": "Think about what provides the initial energy inside photosystem II to split water molecules. What absorbs the light photons?",
  "audio_url": "/api/tts?speaker=Shivani&text=..."
}
```

---

## 6. Enhanced Teacher Observatory Dashboard
**`GET /api/dashboard`**

Aggregates class-wide comprehension telemetry, concept friction, mastery rates, and Level 3 escalations.

### Response
- **Status:** `200 OK`
```json
{
  "total_sessions": 12,
  "total_doubts": 34,
  "total_quizzes": 8,
  "average_quiz_score": 287.5,
  "mastery_distribution": {
    "correct_rate": 62.5,
    "partial_rate": 25.0,
    "incorrect_rate": 12.5
  },
  "level3_concepts": [
    {"concept": "Dark Reactions (Calvin Cycle)", "count": 5},
    {"concept": "Water Photolysis", "count": 2}
  ],
  "confusion_radar": [
    {"concept": "Dark Reactions (Calvin Cycle)", "friction_score": 18},
    {"concept": "Water Photolysis", "friction_score": 11},
    {"concept": "Photosynthesis Overview", "friction_score": 4}
  ],
  "recent_quizzes": [
    {
      "id": "quiz-uuid",
      "session_id": "sess-uuid",
      "score": 350,
      "max_score": 400,
      "percentage": 87.5,
      "status": "completed",
      "created_at": "2026-11-09T21:15:00"
    }
  ]
}
```
