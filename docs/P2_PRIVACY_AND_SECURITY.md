# Pod-Siksha: Privacy & Security Specification

## 1. Executive Privacy Principles
Pod-Siksha is built specifically for classroom and primary/secondary education environments. Student data protection, zero personally identifiable information (PII) retention, and in-memory audio ephemerality are built into the fundamental software architecture.

---

## 2. Audio Processing & Ephemerality Architecture
- **In-Memory Streaming**: Student speech captured via the Web Audio API (`AudioContext`) is sampled at 16kHz mono 16-bit PCM WAV purely inside client browser memory (RAM).
- **Direct Stream Upload**: The WAV byte buffer is streamed via multipart `FormData` directly to the `/api/ask` or `/api/quiz/answer` endpoints.
- **Zero Disk Persistence of Raw Voice**: The FastAPI backend routes the raw audio buffer directly to the live Gnani Prisma STT v3.0 API and discards the binary payload immediately after transcription. No microphone recordings or WAV files are ever saved to disk.
- **Microphone Permissions**: Explicit user authorization is required for every recording session. Visual status badges ("HOLDING TO RECORD", "RECORDING ORAL ANSWER") ensure complete transparency regarding active recording states.

---

## 3. Anonymity & PII Elimination
- **Zero Student Identity Collection**: Pod-Siksha does not require, collect, or store student names, email addresses, phone numbers, school roll numbers, or government IDs.
- **Anonymous Session UUIDs**: Every interaction is anchored to an ephemeral, randomly generated UUIDv4 (e.g. `8dca3a8a-b84d-4025-926a-d6aa20f6684b`).
- **Aggregated Teacher Observatory**: The `/teacher` analytics dashboard strictly displays aggregated cohort statistics (doubt frequencies, concept confusion indices, average quiz scores) and anonymous truncated session IDs (`sess-8dca...`).

---

## 4. API Security & Key Protection
- **Server-Side Key Storage**: External service credentials (`GNANI_API_KEY`, `GEMINI_API_KEY`) are maintained strictly within server-side environment variables (`.env`) and never exposed to client-side DOM, JavaScript bundles, or API response payloads.
- **Input Validation & Sanitization**:
  - File upload restrictions enforce strict MIME validation (PDF documents only, max 10MB; WAV audio only, max 5MB).
  - Parameterized SQL queries prevent SQL injection across all database interactions.
  - CSV exports sanitize all cell strings to escape formula-injection trigger characters (`=`, `+`, `-`, `@`).
- **CORS Configuration**: Configurable via environment variables for production domains with safe default methods.

---

## 5. Model Grounding & LLM Safety Boundaries
- **Strict Curriculum Grounding**: Gemini prompt templates strictly instruct the model to answer student questions and formulate oral quiz evaluations using *only* the contents of the uploaded chapter text.
- **Hallucination Prevention**: For teacher recommendations, Gemini is provided with explicit, verified database counts and strictly forbidden from inventing student interactions or metrics. If fewer than two interactions exist, the system returns an informative empty state.
