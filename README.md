# Pod-Siksha 2.0 — Aura Atelier (Voice-First AI Learning Platform)

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Production_Live-black?style=for-the-badge&logo=vercel)](https://pod-siksha-2.vercel.app)
[![Neon Database](https://img.shields.io/badge/Neon-PostgreSQL_Connected-00E599?style=for-the-badge&logo=postgresql)](https://pod-siksha-2.vercel.app/api/health)
[![Gnani AI](https://img.shields.io/badge/Gnani_AI-Prisma_STT_%26_Timbre_TTS-orange?style=for-the-badge)](https://pod-siksha-2.vercel.app)
[![Gemini API](https://img.shields.io/badge/Google_Gemini-Socratic_Dialogue-4285F4?style=for-the-badge&logo=google)](https://pod-siksha-2.vercel.app)
[![Tests Passing](https://img.shields.io/badge/Tests-12%2F12_Prod_Passing-brightgreen?style=for-the-badge)](https://pod-siksha-2.vercel.app/api/health)

> 🌐 **Live Public Application:** **[https://pod-siksha-2.vercel.app](https://pod-siksha-2.vercel.app)**  
> 🩺 **Backend Health API:** **[https://pod-siksha-2.vercel.app/api/health](https://pod-siksha-2.vercel.app/api/health)**  
> 🏷️ **Tagline:** A classroom podcast that listens. Students interrupt in their own language, explain concepts back, and master ideas with cognitive telemetry.  
> 🛠️ **Technologies:** Gnani AI (Prisma STT v3.0, Timbre TTS v3.0), Google Gemini API (`gemini-3.5-flash-lite`), FastAPI, Neon Serverless PostgreSQL, HTML5 / Web Audio API.  
> 🎨 **Design Identity:** Aura Atelier / Vedic Lumina (Museum Parchment, Kalamkari Emerald-Black, Surya Gold, Terracotta Ochre, Nilgiri Celadon). Strict Light Theme.  
> 🛡️ **Status:** Fully Deployed & Production Ready.

---

## 1. Overview & Vision

Pod-Siksha 2.0 is an autonomous, multilingual, voice-first learning platform built for the **Gnani AI Internship Challenge 2026**. It transforms static textbooks into an interactive Socratic dialogue between two distinct AI hosts, listens when learners interrupt, and introduces deep cognitive feedback loops:

1. **Authentic 14-Turn Socratic Dialogue**: Generates engaging two-host dialogue from uploaded PDFs or chapter text. Host A (Yash / Explainer) and Host B (Priya / Inquisitive Co-Host) speak using distinct Gnani Timbre voices (`Shivani` and `Yashraj`).
2. **Tactile Spacebar Interruption (~180ms Latency)**: Pressing and holding Spacebar or the on-screen mic immediately halts the podcast audio, captures student doubts in regional languages (Telugu, Hindi, Tamil, Kannada, Marathi, Bengali), transcribes via Gnani Prisma STT, answers via Gemini grounded exclusively in textbook evidence, and resumes audio at the exact millisecond.
3. **Physical Audio Playback Engine**: Solved the silent playback issue by sanitizing streaming WAV headers (`len-8` and `len-44` linear PCM recalculation) and implementing dedicated streaming GET/POST endpoints. Includes a 3-tone Web Audio harmonic chime test to physically verify laptop speakers.
4. **Concept DNA Knowledge Topology**: Extracts concept dependency graphs cached in Neon PostgreSQL, mapping prerequisite paths and real-time mastery scores computed from learner interactions.
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
      |             FastAPI Serverless on Vercel Production           |
      +---------------------------------------------------------------+
           |                     |                      |
           v                     v                      v
  +-----------------+   +------------------+   +-------------------+
  |   Gnani AI      |   |  Google Gemini   |   |  Neon PostgreSQL  |
  | Prisma STT v3.0 |   | 3.5 Flash Lite   |   | (Serverless Cloud)|
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
8. **Concept DNA Atlas** (`#atlas`): Graph visualization of conceptual prerequisites with color-coded mastery status.
9. **Teacher Observatory** (`#observatory`): Class-wide telemetry, misconception trends, and one-click CSV report exports.

---

## 4. Verification & Testing

Run the automated live production verification suite:
```bash
python scripts/verify_production_suite.py
```

All 12 production test scenarios verify:
1. Health check & Neon PostgreSQL connectivity
2. Unauthenticated root landing (`/` redirects to `#login`)
3. Strict API route protection (401 Unauthorized)
4. User registration (Neon PostgreSQL write)
5. User authentication & session token issuance
6. Session identity validation (`/api/auth/me`)
7. User-level data isolation
8. Gnani Timbre TTS live audio stream synthesis
9. Gnani Prisma STT voice interruption & Q&A
10. Concept DNA, Misconception Radar, and Memory Loop
11. Teacher Observatory recommendations & CSV export
12. Logout & server-side session revocation
