# Pod-Siksha — Live Demo Script & Walkthrough Guide

Use this script for competition demonstrations and evaluation walkthroughs.

---

## 1. Opening Narrative (30 seconds)
> "Textbooks don't listen, and traditional educational podcasts are one-way monologues. If a student gets confused at minute 3, they get lost for the rest of the lecture.  
> **Pod-Siksha** is an interactive, interruptible AI classroom podcast. Two AI hosts—Yash and Priya—teach any uploaded chapter in the student's mother tongue. When a student doesn't understand, they don't have to raise their hand or wait: they press **HOLD TO ASK** or hold their **Spacebar**. The podcast pauses instantly, listens in their regional language, explains the concept with a progressive hint ladder, and resumes right from where they stopped. Meanwhile, the teacher sees exactly which concepts triggered friction."

---

## 2. Walkthrough Steps

### Step 1: Launch Application
- Start server:
  ```powershell
  cd C:\Users\jvris\Downloads\pod-siksha
  python server.py
  ```
- Open browser: `http://localhost:8008`
- Point out the **Saffron Frequency** aesthetic: Ivory Paper (`#F7F3E9`), Terracotta (`#E8794F`), Saffron Gold (`#E8B94F`).
- Emphasize the English-only visual transcript and the regional spoken audio.

### Step 2: Upload Chapter & Select Language
- Select **Telugu (తెలుగు)** (or Hindi / Tamil / Kannada / Marathi / Bengali).
- Choose the provided `sample_chapter.pdf` or keep the default Photosynthesis text.
- Click **"Generate 14-Turn Podcast Dialogue"**.
- Watch Gemini 3.5 generate a structured 14-turn dialogue between Host A (Yash) and Host B (Priya).

### Step 3: Experience Two-Host Playback
- Turn 1 begins playing automatically with **Gnani Timbre TTS** (`Shivani` voice for Host A).
- Host A card illuminates in Terracotta with animated speaking bars.
- In-memory prefetch retrieves Turn 2 (`Yashraj` voice for Host B) in the background so transitions are instant.
- Point out the English transcript in the teleprompter while the voice speaks Telugu code-mixed with science terms.

### Step 4: The Core Moment — Hold To Ask Interruption
- While Turn 2 or Turn 3 is playing, press and hold the **Spacebar** (or mouse down on the big tactile **"Hold to Ask"** button).
- Observe that playback pauses within ~200ms and the timestamp is saved.
- Speak a doubt into the microphone:
  *"How does water splitting produce oxygen?"* or *"వాటర్ స్ప్లిట్టింగ్ ఎలా జరుగుతుంది?"*
- Release the Spacebar.
- The system transcribes the question with **Gnani Prisma STT v3.0**, grounds it in the uploaded chapter using **Gemini 3.5**, identifies the concept (*Water Photolysis*), selects **Hint Level 1**, and Host A speaks the answer.
- Once answered, click **Resume Podcast Playback** (or let it auto-resume).
- Observe that the podcast resumes from the exact saved millisecond!

### Step 5: Comprehension Quiz & Teacher Observatory
- At the end of the episode (or by navigating to `/teacher`), show the **Teacher Observatory**.
- Show the **Concept Confusion Radar** ranking concepts by friction score ($2 \times \text{doubts} + 3 \times \text{quiz errors}$).
- Open the session transcript to review student questions and AI explanations.
