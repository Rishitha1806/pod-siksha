"""
Pydantic Data Models for Pedagogical Knowledge, Concept Dependency Graphs,
and Adaptive Teaching Recommendations.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Concept(BaseModel):
    id: Optional[str] = None
    concept_name: str
    concept_type: str = "core"  # core, foundational, advanced, terminology, mechanism
    definition: str
    summary: Optional[str] = ""
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    common_confusions: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    source_page: int = 1
    confidence: float = 1.0

class ConceptRelationship(BaseModel):
    id: Optional[str] = None
    from_concept: str
    to_concept: str
    relationship_type: str  # prerequisite_for, part_of, specializes, applies_to, leads_to
    evidence_text: Optional[str] = ""
    weight: float = 1.0

class ConceptGraph(BaseModel):
    document_id: str
    subject: str
    topic: str
    chapter_title: str
    concepts: List[Concept] = Field(default_factory=list)
    relationships: List[ConceptRelationship] = Field(default_factory=list)
    suggested_learning_path: List[str] = Field(default_factory=list)

class TeachingRecommendation(BaseModel):
    id: Optional[str] = None
    concept_name: str
    recommended_method: str  # step_by_step, animated_demonstration, interactive_diagram, code_walkthrough, execution_trace, mathematical_derivation, worked_example, timeline, comparison, case_study, practice_exercise, socratic_questioning
    rationale: str
    suggested_animation_type: str  # circulation, cycle_loop, force_vectors, sorting_algorithm, molecular_reaction, growth_curve, educational_2d
    priority: int = 1
    step_plan: List[str] = Field(default_factory=list)

class GroundedFact(BaseModel):
    statement: str
    source_page: int
    exact_quote_or_reference: str

class GroundedLessonContext(BaseModel):
    document_id: str
    subject: str
    topic: str
    stated_facts: List[GroundedFact] = Field(default_factory=list)
    derived_insights: List[str] = Field(default_factory=list)
    pedagogical_extensions: List[str] = Field(default_factory=list)
    concept_graph: Optional[ConceptGraph] = None
    teaching_recommendations: List[TeachingRecommendation] = Field(default_factory=list)
    verified_equations: List[str] = Field(default_factory=list)
    verified_code_blocks: List[str] = Field(default_factory=list)
    verified_figures: List[str] = Field(default_factory=list)
