# Pod-Siksha 3.0 — Universal AI Educator
## 3–5 Minute Evaluation Demonstration Script

**Platform URL:** [https://pod-siksha-2.vercel.app](https://pod-siksha-2.vercel.app)  
**Demo Account:** `scholar@podsiksha.edu` / `TestPassword@123` (or register a fresh student account)  
**Target Audience:** Technical evaluators, product architects, and pedagogy specialists  
**Total Running Time:** 3 minutes 45 seconds  

---

## Act I: Entry & Authentication (0:00 – 0:45)

1. **Open the Platform:**
   - Navigate to `https://pod-siksha-2.vercel.app`.
   - *Observation:* The application enforces **login-first security**. Unauthenticated visitors cannot access studio workspaces or student records.
   - *Visual Aesthetics:* Notice the Aura Atelier design language—warm terracotta accents, muted parchment cards, and editorial typography.

2. **Authenticate:**
   - Click **Enter Learning Atelier**.
   - The user lands on the **Atelier Dashboard**, displaying recent journeys, mastery analytics, and active visual projects.

---

## Act II: Universal Dual-Entry Ingestion (0:45 – 1:30)

1. **Trigger Ingestion Modal:**
   - Click the prominent **+ New Learning Journey** button in the dashboard header.
   - The **Curriculum Ingestion Modal** opens with two clear entry point tabs:
     - **Tab 1: Upload Document (PDF / PPTX / DOCX / TXT)**
     - **Tab 2: Enter Topic Manually**

2. **Demonstrate Optional Paragraph Text:**
   - Switch to **Enter Topic Manually**.
   - In **Topic Title**, type: `Binary Search Trees in C++`.
   - Highlight the **Concept Notes / Syllabus Text** field: **It is completely optional**. Leave it blank!
   - Explain to the evaluators:
     > *"Unlike traditional wrappers that force students to copy-paste paragraphs, Pod-Siksha's AI Educator can construct a complete visual curriculum from a standalone topic title, or extract it from complex multimodal documents."*
   - Select destination **AI Animated Visual Stage**.

---

## Act III: Multimodal Document Intelligence & Concept DAG (1:30 – 2:30)

1. **Upload Document Demonstration:**
   - Upload any academic textbook or paper (e.g. `01_python_programming.pdf` or `05_biology_cell_energetics.pdf`).
   - The document is parsed through the asynchronous processing pipeline:
     - OCR processes rasterized pages with Gemini Multimodal Vision.
     - Code block extraction identifies syntax, algorithms, and preserves 4-space indentation.
     - Mathematical expressions are parsed into KaTeX-ready LaTeX formulas.
     - Pedagogical Concept Extractor constructs an open Directed Acyclic Graph (DAG) of prerequisites.
     - Teaching Strategy Engine selects the optimal cognitive method (`code_walkthrough`, `process_animation`, or `interactive_derivation`).

2. **Inspect the Document Intelligence Dossier:**
   - Open the **Document Intelligence Dossier Modal**.
   - Show the 5 structured tabs:
     - **Concepts & Graph:** Displays atomic concepts, Bloom's level, and diagnosed misconceptions.
     - **Teaching Strategies:** Explains why a specific visual method was recommended.
     - **Code Snippets:** Displays clean code blocks with syntax highlighting and algorithmic purpose.
     - **Formulas (LaTeX):** Displays formatted mathematical equations.
     - **Multimodal Diagrams:** Displays diagram callouts and structural explanations.

---

## Act IV: Adaptive Visual Stage Playback (2:30 – 3:15)

1. **Launch Animated Visual Lesson:**
   - Click **Learn with AI Educator** on the top concept (e.g., *"Recursive Functions"* or *"Photolysis of Water"*).
   - The platform transitions directly into the **Universal AI Visual Stage**.

2. **Verify Interactive Playback:**
   - Click **Play**.
   - *Observation:* The canvas renders real 2D animated educational objects (nodes, arrows, code terminals, callout badges, chemical molecules).
   - *Narration & Subtitles:* Synchronized multilingual audio plays in authentic Telugu (or English/Hindi) accompanied by timed subtitle banners.
   - *Checkpoint Questions:* The video automatically pauses at interactive checkpoints, asking the learner a conceptual question to assess understanding before proceeding.
   - *In-Video Doubt Resolution:* Pause the video and submit a spoken or typed question to receive immediate grounded explanations from the AI educator.

---

## Act V: Socratic Broadcast Studio & Teacher Observatory (3:15 – 3:45)

1. **Socratic Audio Podcast Studio:**
   - Switch to the **Socratic Broadcast Studio** view.
   - Show the 14-turn dialogue between Host A (Explainer) and Host B (Questioner).
   - Click play on any turn to verify instantaneous streaming audio with authenticated query tokens.

2. **Conclusion & Wrap-Up:**
   - Highlight the production stability: Neon PostgreSQL with 28 tables, zero data loss, strict tenant isolation, and live deployment on Vercel.
   - Thank the evaluation committee.
