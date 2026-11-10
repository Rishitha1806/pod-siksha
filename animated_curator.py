"""
Pod-Siksha 2.0 — Universal AI Animated Learning Engine.
Orchestrates adaptive learner profiling, Gemini storyboard generation,
declarative visual specs, and scene-level synchronization.
"""

import json
import logging
import re
import uuid
from typing import Dict, Any, List, Optional

log = logging.getLogger("pod_siksha.animation")

LEARNER_PROFILES = {
    "child": {
        "label": "Child (Ages 5–12)",
        "tone": "warm, playful, storytelling, friendly, full of wonder and vivid everyday analogies",
        "visual_style": "cartoon",
        "vocabulary_level": "simple, accessible, engaging words without dense jargon",
        "pacing": "unhurried, expressive, high enthusiasm",
        "analogy_focus": "toys, animals, playgrounds, cartoons, daily kitchen or school objects"
    },
    "teen": {
        "label": "Teenager (Ages 13–17)",
        "tone": "curious, energetic, relatable, intellectually stimulating and clear",
        "visual_style": "educational_2d",
        "vocabulary_level": "foundational scientific & mathematical concepts with clear intuition",
        "pacing": "crisp, engaging, exam-friendly and conceptually lucid",
        "analogy_focus": "sports, gaming, gadgets, space, school laboratory experiments"
    },
    "university": {
        "label": "University & Research (Ages 18–25)",
        "tone": "academic, rigorous, analytical, deep-dive into first principles",
        "visual_style": "simulation",
        "vocabulary_level": "precise technical terminology, mathematical notation, formal proofs and mechanics",
        "pacing": "systematic, high information density with structural clarity",
        "analogy_focus": "state machines, vector calculus, physical dynamics, computational complexity"
    },
    "professional": {
        "label": "Working Professional (Ages 26–59)",
        "tone": "executive, pragmatic, result-oriented, focus on architecture and ROI",
        "visual_style": "infographic",
        "vocabulary_level": "business terminology, industry best practices, strategic tradeoffs",
        "pacing": "efficient, structured, actionable and concise",
        "analogy_focus": "market dynamics, enterprise workflows, case studies, cost vs scale tradeoffs"
    },
    "older_adult": {
        "label": "Older Adult & Lifelong Learner (Ages 60+)",
        "tone": "patient, respectful, reassuring, crystal clear, crystal simple navigation",
        "visual_style": "whiteboard",
        "vocabulary_level": "clear everyday language, large readable text, zero unnecessary jargon",
        "pacing": "deliberate, steady, repeatable with warm encouragement",
        "analogy_focus": "traditional life skills, letters, household appliances, banking passbooks"
    }
}

ANIMATION_TYPES = [
    "circulation",        # Biology, fluid dynamics, heart, pulmonary, vascular
    "force_vectors",      # Physics, Newton's laws, transformers, electromagnetism
    "equation_transform", # Mathematics, algebra, calculus, step-by-step proofs
    "molecular_reaction", # Chemistry, atoms, covalent bonds, reactions
    "sorting_algorithm",  # Computer Science, algorithms, arrays, database queries
    "cycle_loop",         # Geography, water cycle, carbon cycle, ecosystems
    "growth_curve",       # Finance, compound interest, exponential growth
    "step_tutorial"       # Everyday skills, digital banking, software tutorials
]

def build_storyboard_prompt(
    title: str,
    source_content: str,
    profile_key: str,
    language: str,
    lang_name: str,
    animation_style: str
) -> str:
    profile = LEARNER_PROFILES.get(profile_key, LEARNER_PROFILES["teen"])
    
    return f"""You are the Master Visual Learning Architect for 'Pod-Siksha 2.0', the universal AI animated learning platform.
Your mission is to produce a multi-scene ANIMATED EDUCATIONAL LESSON that visually demonstrates concepts through movement, diagrams, simulations, and synchronized narration.

LEARNER AUDIENCE PROFILE:
- Target Learner: {profile['label']}
- Tone of Voice: {profile['tone']}
- Vocabulary Level: {profile['vocabulary_level']}
- Pacing & Delivery: {profile['pacing']}
- Analogy Style: {profile['analogy_focus']}
- Preferred Animation Theme: {animation_style}

LESSON TOPIC / SOURCE CONTENT:
Title: {title}
Content:
\"\"\"
{source_content[:7000]}
\"\"\"

CRITICAL PEDAGOGICAL REQUIREMENTS:
1. Divide the lesson into 4 to 6 focused, sequential scenes (e.g. Scene 1: Hook & Core Problem, Scene 2: Intuitive Visual Metaphor, Scene 3: Deep Technical Simulation, Scene 4: Real-world Application / Proof, Scene 5: Common Misconception Warning, Scene 6: Mastery Summary).
2. For EACH scene, you MUST choose the most suitable `animation_type` from:
   - "circulation": for fluid movement, biology (heart/blood), loops, flow networks.
   - "force_vectors": for physics, motion, forces, electricity, transformers, machines.
   - "equation_transform": for mathematics, algebraic steps, formulas, graph coordinates.
   - "molecular_reaction": for chemistry, atoms, molecules, chemical bonding.
   - "sorting_algorithm": for computer science, data structures, comparisons, database queries.
   - "cycle_loop": for environmental cycles (water/carbon), meteorological loops, feedback systems.
   - "growth_curve": for finance (compound interest), economics, exponential scales, population growth.
   - "step_tutorial": for digital literacy, interface walkthroughs, practical instructions, safety steps.
3. SPOKEN NARRATION (`narration_text`):
   - MUST be written in {lang_name} naturally code-mixed with English technical keywords where suitable.
   - Character count: 120–220 characters per scene so narration sounds natural and punchy.
4. DISPLAY TEXT (`display_text`):
   - High-contrast English caption summary (under 180 chars) for subtitles and on-screen teleprompter.
5. DECLARATIVE VISUAL SPECIFICATION (`visual_spec`):
   - Provide concrete visual entities, labels, stages, and numerical values for the HTML5 canvas/SVG renderer to animate.
   - Include `labels`: array of key labels to point to.
   - Include `elements`: key entities with colors and coordinates.
   - Include `highlight`: the central focal point to pulse or highlight.
   - Include `action`: specific dynamic motion instruction (e.g. "expand_coils", "pulse_chambers", "swap_bars", "grow_curve", "flow_particles").
6. INTERACTIVE CHECKPOINT (`checkpoint_question`):
   - A 1-question check to verify comprehension of this specific scene (with question, options, correct_idx, and explanation).

OUTPUT FORMAT:
Respond ONLY with a strictly valid JSON object matching this schema:
{{
  "lesson_title": "Catchy Clear Title in English",
  "summary": "1-2 sentence overview of what the learner will master",
  "concepts": ["Concept 1", "Concept 2", "Concept 3"],
  "scenes": [
    {{
      "scene_index": 1,
      "title": "Scene 1 Headline",
      "concept_tag": "Specific Concept",
      "learning_objective": "What learner sees and understands in this scene",
      "animation_type": "circulation|force_vectors|equation_transform|molecular_reaction|sorting_algorithm|cycle_loop|growth_curve|step_tutorial",
      "narration_text": "Spoken text in {lang_name} (< 220 chars)",
      "display_text": "English subtitle and display text (< 180 chars)",
      "duration_sec": 12.0,
      "visual_spec": {{
        "theme": "{animation_style}",
        "action": "action_name",
        "highlight": "focal element",
        "labels": ["Label 1", "Label 2"],
        "values": {{"key1": "val1"}},
        "elements": [
          {{"id": "elem1", "name": "Primary Element", "color": "#E05A47", "x": 30, "y": 50, "detail": "extra info"}}
        ]
      }},
      "checkpoint_question": {{
        "question": "Quick question verifying this scene?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_index": 0,
        "explanation": "Why Option A is correct based on the animated proof."
      }}
    }}
  ]
}}
"""

def generate_subtitles_spec(narration: str, duration_sec: float) -> List[Dict[str, Any]]:
    """Splits a narration script into timed subtitle chunks spanning the scene duration."""
    sentences = re.split(r'(?<=[.!?।॥])\s+', narration.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        sentences = [narration.strip()]
    
    total_len = sum(len(s) for s in sentences) or 1
    total_ms = int(duration_sec * 1000)
    
    subtitles = []
    current_ms = 0
    for s in sentences:
        seg_duration = max(1500, int((len(s) / total_len) * total_ms))
        end_ms = min(total_ms, current_ms + seg_duration)
        subtitles.append({
            "start_ms": current_ms,
            "end_ms": end_ms,
            "text": s
        })
        current_ms = end_ms
    
    # Ensure last segment extends to total duration
    if subtitles and subtitles[-1]["end_ms"] < total_ms:
        subtitles[-1]["end_ms"] = total_ms
        
    return subtitles
