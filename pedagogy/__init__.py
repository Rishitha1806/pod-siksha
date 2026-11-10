"""
Pedagogical Knowledge & Adaptive Teaching Engine Package for Pod-Siksha.
Includes concept extraction, dependency graphs, multimodal grounding, and teaching strategy generation.
"""

from pedagogy.models import (
    Concept,
    ConceptRelationship,
    ConceptGraph,
    TeachingRecommendation,
    GroundedLessonContext
)
from pedagogy.concept_extractor import PedagogicalConceptExtractor
from pedagogy.teaching_strategy_engine import AdaptiveTeachingStrategyEngine
from pedagogy.gemini_lesson_context import GroundedLessonContextBuilder

__all__ = [
    "Concept",
    "ConceptRelationship",
    "ConceptGraph",
    "TeachingRecommendation",
    "GroundedLessonContext",
    "PedagogicalConceptExtractor",
    "AdaptiveTeachingStrategyEngine",
    "GroundedLessonContextBuilder"
]
