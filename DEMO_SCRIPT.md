# Pod-Siksha 3.0 — Universal AI Educator
## 4-Minute Video Demonstration Script & Evaluation Guide

**Platform Production URL:** [https://pod-siksha-2.vercel.app](https://pod-siksha-2.vercel.app)  
**Demo Account:** `scholar@podsiksha.edu` / `TestPassword@123` (or register a fresh learner account)  
**Target Audience:** Evaluation committee, technical assessors, and product judges  
**Total Target Duration:** 3 minutes 45 seconds to 4 minutes 15 seconds  

---

## Act I: Product Identity, Universal Navigation & Honest Empty State (0:00 – 0:45)

1. **Open the Platform:**
   - Navigate to `https://pod-siksha-2.vercel.app`.
   - *Observation:* Clean, login-first authentication protecting learner privacy and isolated data.
   - Click **Sign In** (or register a brand-new test learner to demonstrate the fresh experience).

2. **Demonstrate Universal 6-Item Navigation:**
   - Point out the unified, uncluttered navigation header:
     - **Home**
     - **Learn**
     - **Library**
     - **Concept DNA**
     - **Insights**
     - **Profile**
   - *Key Message:* *"We eliminated all legacy age-segmented sub-menus. Learners can now customize their explanation complexity directly across Beginner, Intermediate, and Advanced."*

3. **Demonstrate Honest Empty State (Zero Dummy Data):**
   - Show the newly registered learner dashboard.
   - Point out that there are **no hardcoded lessons, no fake 78% mastery metrics, and no mock Chloroplast trees**.
   - Instead, the learner sees an honest, encouraging prompt: *"No learning journeys yet. Upload your first document or enter a topic to begin."*

---

## Act II: Learning Initiation & Multi-Modal Ingestion (0:45 – 1:30)

1. **Trigger Learning Modal:**
   - Click **+ New Learning Journey** in the header.
   - Show the dual-entry tabs:
     - **Tab 1: Upload Document (PDF / PPTX / DOCX / TXT)**
     - **Tab 2: Enter Topic Manually**

2. **Demonstrate Standalone Topic-Only Learning:**
   - Switch to **Enter Topic Manually**.
   - Enter Topic: `Photosynthesis and Cellular Respiration`.
   - Note that **Concept Notes / Syllabus Text is 100% optional**.
   - Select Explanation Complexity: `Intermediate`.
   - Click **Generate Animated Lesson**.
   - The AI Educator compiles the storyboard, extracts atomic concepts, and transitions straight into the visual stage.

---

## Act III: The Single AI Visual Educator Experience (1:30 – 2:40)

1. **One AI Educator (No Podcast Banter):**
   - The learner enters the **Universal AI Visual Stage**.
   - One educator explains the topic continuously and methodically with Indian-accented speech (Gnani TTS) and synchronized English subtitles.
   - The interactive canvas renders dynamic visual mechanisms (e.g. chloroplast light-harvesting, photon photolysis of water, electron flows).

2. **Contextual In-Scene Doubt Resolution ("Ask This Scene"):**
   - While the video is playing, click **Ask This Scene**.
   - Type or speak: *"Why is oxygen released during the light reaction?"*
   - The AI Educator responds with a direct, contextual answer focused on the active scene, synthesized with voice and subtitles without losing the learner's place.

3. **Adaptive Re-Explanation ("Explain It Again"):**
   - Click **Explain It Again**.
   - Select **Analogy** or **Step-by-Step**.
   - The educator re-explains the current scene's concept using a vivid real-world metaphor (e.g. water as the solar battery recharge) without restarting the entire lesson.

4. **Interactive Checkpoint Quiz:**
   - Complete the checkpoint question displayed below the visual canvas.
   - Click the correct option.
   - Point out that answering the checkpoint updates the concept's status from `learning` to `understood` directly in the database.

---

## Act IV: Concept DNA Knowledge Tree (2:40 – 3:35)

1. **Navigate to Concept DNA:**
   - Click **Concept DNA** in the top navigation bar.
   - Show the interactive SVG knowledge tree:
     - **Root Node:** Main lesson topic (*Photosynthesis and Plant Metabolism*).
     - **Branch Nodes:** Extracted concepts (*Foundation*, *Thylakoid Photolysis*, *Calvin Cycle*, *Cellular Respiration*).
     - **Prerequisite Links:** Directed curved arrows indicating learning order.
     - **Status Badges:** Color-coded for `learning` (blue), `understood` (emerald), and `needs_revision` (terracotta).

2. **Inspect Concept Detail Drawer:**
   - Click on any concept node in the tree.
   - The sliding **Concept Detail Drawer** opens on the right, providing 6 actionable pathways:
     1. **Explain Concept:** Dynamic explanations powered by Gemini in 4 modes (*Simpler*, *Step-by-Step*, *Analogy*, *Real-World*).
     2. **Watch Scene:** Jumps directly to the lesson scene covering this concept.
     3. **Prerequisites & Related Concepts:** Displays dependencies in the curriculum.
     4. **Practice Checkpoint:** Retakes the checkpoint question to reinforce retention.
     5. **Mark for Revision:** Flags the concept for revision and schedules it in the spaced retrieval loop.

3. **Demonstrate Side-by-Side Compare Concepts:**
   - Click **Compare Concepts** in the tree toolbar.
   - Select Concept A (*Photosynthesis*) and Concept B (*Cellular Respiration*).
   - Click **Analyze Comparison**.
   - View the generated structured comparison: similarities, key differences, side-by-side comparison matrix, and a discriminator test question.

---

## Act V: Understanding Tracker & Real Teach-Back Mode (3:35 – 4:15)

1. **Navigate to Insights:**
   - Click **Insights** in the top navigation bar.
   - Show the **Understanding Tracker**:
     - All metrics (Mastery Score, Concepts Understood, In Progress, In Revision) are strictly computed from persisted DB records in `user_concept_progress`.

2. **Demonstrate Authentic Teach-Back Evaluation:**
   - Select **Teach-Back Mode**.
   - The dropdown lists **only concepts the learner has actually studied**.
   - Select *Photolysis of Water*.
   - Provide an explanation: *"Water is split by photons in the thylakoid to release oxygen and provide electrons."*
   - Click **Evaluate Explanation**.
   - Gemini evaluates the explanation against textbook ground truth:
     - **Understood Points:** Correctly recognized that photolysis splits water into oxygen and electrons.
     - **Misconceptions:** Identifies any false cause-and-effect relationships.
     - **Missing Knowledge:** Points out missing nuances (e.g. Photosystem II).
     - **Next Step:** Recommends reviewing the relevant scene.
     - **Mastery Delta:** Updates the concept's status and mastery score in the database.

3. **Conclusion:**
   - *"Pod-Siksha 3.0 delivers a genuine Universal AI Educator: Upload anything, learn everything, backed by real pedagogical intelligence and zero fabricated data."*
