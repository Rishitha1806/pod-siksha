"""
Automated Test Suite: Phase 2 - Universal Multimodal Document Intelligence.
Tests:
- Real OCR pipeline on 5.76 MB scanned document (11_scanned_manuscript.pdf)
- Programming Document Intelligence (Python, Java OOP, DSA)
- Mathematical Intelligence & LaTeX preservation (Calculus)
- Multimodal figures & diagrams (Biology, Research Paper)
- Pedagogical concept extraction & DAG dependency graph
- Adaptive teaching strategy recommendation engine
- Grounded lesson context with epistemic separation
- Interactive learning generation and playable scenes
"""

import os
import sys
import time
import json
import pytest
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from db_adapter import get_db
from extractors.ocr_extractor import OcrPdfExtractor
from extractors.code_extractor import ProgrammingCodeExtractor
from extractors.math_extractor import MathematicalIntelligenceExtractor
from extractors.multimodal_extractor import MultimodalDocumentExtractor
from extractors.pdf_extractor import TextPdfExtractor
from pedagogy.concept_extractor import PedagogicalConceptExtractor
from pedagogy.teaching_strategy_engine import AdaptiveTeachingStrategyEngine
from pedagogy.gemini_lesson_context import GroundedLessonContextBuilder
from document_service import DocumentService

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "phase2_documents"
BASE_URL = "http://127.0.0.1:8008"

# Test User
TEST_EMAIL = f"p2_tester_{int(time.time())}@demo.in"
TEST_PASS = "Password123!"

@pytest.fixture(scope="session")
def auth_token():
    reg = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASS,
        "full_name": "Phase 2 Automated Tester"
    })
    data = reg.json()
    token = data.get("access_token")
    assert token, f"Could not acquire token: {data}"
    return token

def test_01_ocr_scanned_pdf(auth_token):
    """Verifies real OCR recognition on image-only scanned document."""
    pdf_path = FIXTURES_DIR / "11_scanned_manuscript.pdf"
    assert pdf_path.exists(), "Scanned PDF fixture missing"
    assert os.path.getsize(pdf_path) > 5 * 1024 * 1024, "Scanned fixture should be > 5 MB"

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    ocr = OcrPdfExtractor()
    result = ocr.extract(file_bytes, "11_scanned_manuscript.pdf")

    assert result.total_pages >= 1
    assert result.metadata.get("ocr_performed") is True
    full_text = result.full_text.lower()
    print("OCR Transcribed text preview:", full_text[:200])

    # Check for recognized Kepler content
    assert any(w in full_text for w in ["kepler", "planetary", "orbit", "ellipse", "sun", "proportional"])
    print("Test 1 Passed: Real OCR on 5.76 MB scanned document successfully extracted text.")

def test_02_programming_code_extraction():
    """Verifies code blocks, language detection, and indentation preservation."""
    pdf_path = FIXTURES_DIR / "01_python_programming.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    extractor = TextPdfExtractor()
    res = extractor.extract(file_bytes, "01_python_programming.pdf")

    code_ext = ProgrammingCodeExtractor()
    blocks = code_ext.process_document(res.sections)

    assert len(blocks) >= 1
    py_block = blocks[0]
    assert py_block["language"] == "python"
    assert "def recursive_fibonacci" in py_block["code_text"]
    assert "    if n <= 0:" in py_block["code_text"], "Indentation must be preserved"
    print("Test 2 Passed: Python code extraction preserved indentation and detected language.")

def test_03_java_oop_extraction():
    """Verifies Java OOP structure, classes, and inheritance detection."""
    pdf_path = FIXTURES_DIR / "02_java_oop.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    extractor = TextPdfExtractor()
    res = extractor.extract(file_bytes, "02_java_oop.pdf")

    code_ext = ProgrammingCodeExtractor()
    blocks = code_ext.process_document(res.sections)

    assert len(blocks) >= 1
    all_code = "\n\n".join(b["code_text"] for b in blocks)
    assert any(b["language"] == "java" for b in blocks)
    assert "public abstract class GeometricShape" in all_code
    assert "public class Circle extends GeometricShape" in all_code
    print("Test 3 Passed: Java OOP extraction verified with classes and polymorphism.")

def test_04_mathematical_intelligence_latex():
    """Verifies calculus equations are parsed and normalized into LaTeX."""
    pdf_path = FIXTURES_DIR / "04_mathematics_calculus.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    extractor = TextPdfExtractor()
    res = extractor.extract(file_bytes, "04_mathematics_calculus.pdf")

    math_ext = MathematicalIntelligenceExtractor()
    math_items = math_ext.process_document(res.sections)

    assert len(math_items) >= 1
    latex_expressions = [m["latex_expr"] for m in math_items]
    print("Extracted LaTeX expressions:", latex_expressions)
    assert any("\\int" in expr or "\\nabla" in expr or "\\det" in expr for expr in latex_expressions)
    print("Test 4 Passed: Mathematical equations extracted and normalized into LaTeX.")

def test_05_pedagogical_concept_extraction():
    """Verifies pedagogical concept graph and universal subject taxonomy."""
    pdf_path = FIXTURES_DIR / "05_biology_cell_energetics.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    extractor = TextPdfExtractor()
    res = extractor.extract(file_bytes, "05_biology_cell_energetics.pdf")

    concept_ext = PedagogicalConceptExtractor()
    graph = concept_ext.extract_concepts_and_graph(
        document_id="test_doc_bio",
        filename="05_biology_cell_energetics.pdf",
        sections=res.sections
    )

    assert len(graph.concepts) >= 2
    concept_names = [c.concept_name for c in graph.concepts]
    print(f"Subject: {graph.subject} | Concepts: {concept_names}")
    for c in graph.concepts:
        assert c.definition, f"Concept {c.concept_name} must have a definition"
        assert c.source_page >= 1
    print("Test 5 Passed: Pedagogical concept graph constructed with grounded definitions.")

def test_06_adaptive_teaching_strategy_engine():
    """Verifies dynamic teaching method selection matching content type."""
    from pedagogy.models import Concept
    strategy_engine = AdaptiveTeachingStrategyEngine()

    # Code concept -> code walkthrough / execution trace
    code_concepts = [Concept(concept_name="Recursive Call Stack", definition="Stack frame allocation", source_page=1)]
    recs_code = strategy_engine.recommend_strategies("doc_code", "Computer Science", code_concepts, has_code=True)
    assert recs_code[0].recommended_method in ["code_walkthrough", "execution_trace"]

    # Math concept -> mathematical derivation
    math_concepts = [Concept(concept_name="Line Integrals", definition="Integration along curve", source_page=1)]
    recs_math = strategy_engine.recommend_strategies("doc_math", "Calculus", math_concepts, has_math=True)
    assert recs_math[0].recommended_method == "mathematical_derivation"

    # Biology concept -> animated demonstration
    bio_concepts = [Concept(concept_name="ATP Synthase Kinetics", definition="Rotor mechanism", source_page=1)]
    recs_bio = strategy_engine.recommend_strategies("doc_bio", "Biology", bio_concepts, has_figures=True)
    assert recs_bio[0].recommended_method in ["animated_demonstration", "process_animation", "step_by_step"]

    print("Test 6 Passed: Dynamic teaching strategy recommendations verified across subjects.")

def test_07_grounded_lesson_context():
    """Verifies strict epistemic separation between facts, deductions, and analogies."""
    pdf_path = FIXTURES_DIR / "07_physics_electromagnetism.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    extractor = TextPdfExtractor()
    res = extractor.extract(file_bytes, "07_physics_electromagnetism.pdf")

    concept_ext = PedagogicalConceptExtractor()
    graph = concept_ext.extract_concepts_and_graph("doc_phys", "07_physics_electromagnetism.pdf", res.sections)

    builder = GroundedLessonContextBuilder()
    ctx = builder.build_context("doc_phys", graph, res.sections)

    assert len(ctx.stated_facts) >= 1
    assert len(ctx.derived_insights) >= 1
    assert len(ctx.pedagogical_extensions) >= 1
    for fact in ctx.stated_facts:
        assert fact.source_page >= 1
        assert "Page " in fact.exact_quote_or_reference

    prompt_context = builder.format_prompt_context(ctx)
    assert "EXPLICITLY STATED TEXTBOOK FACTS" in prompt_context
    assert "LOGICALLY DERIVED INSIGHTS" in prompt_context
    assert "PEDAGOGICAL EXTENSIONS" in prompt_context
    print("Test 7 Passed: Grounded lesson context enforces strict epistemic honesty.")

def test_08_end_to_end_document_pipeline_api(auth_token):
    """Executes full document upload, processing job, and intelligence API queries."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    pdf_path = FIXTURES_DIR / "12_mixed_science_and_code.pdf"

    # 1. Upload
    with open(pdf_path, "rb") as f:
        up_res = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files={"file": ("12_mixed_science_and_code.pdf", f, "application/pdf")},
            headers=headers
        )
    assert up_res.status_code == 200, f"Upload failed: {up_res.text}"
    doc_info = up_res.json()
    doc_id = doc_info["document_id"]
    job_id = doc_info["job_id"]
    print(f"Uploaded doc {doc_id}, job {job_id}")

    # 2. Process Job synchronously to ensure pipeline execution
    job_result = DocumentService.process_document_job(job_id)
    assert job_result["status"] == "completed"
    print("Job processing completed successfully:", job_result.get("summary"))

    # 3. Query Concepts API
    c_res = requests.get(f"{BASE_URL}/api/documents/{doc_id}/concepts", headers=headers)
    assert c_res.status_code == 200
    concepts_data = c_res.json()
    assert len(concepts_data["concepts"]) >= 1
    chosen_concept = concepts_data["concepts"][0]["name"]
    print(f"Concepts query OK. Chosen concept for learning: '{chosen_concept}'")

    # 4. Query Code API
    cod_res = requests.get(f"{BASE_URL}/api/documents/{doc_id}/code", headers=headers)
    assert cod_res.status_code == 200
    code_data = cod_res.json()
    assert len(code_data["code_blocks"]) >= 1

    # 5. Query Math API
    m_res = requests.get(f"{BASE_URL}/api/documents/{doc_id}/math", headers=headers)
    assert m_res.status_code == 200
    math_data = m_res.json()
    assert len(math_data["math_expressions"]) >= 1

    # 6. Query Teaching Strategies API
    s_res = requests.get(f"{BASE_URL}/api/documents/{doc_id}/teaching-strategies", headers=headers)
    assert s_res.status_code == 200
    strat_data = s_res.json()
    assert len(strat_data["teaching_strategies"]) >= 1

    # 7. Learn Concept Action (Generates playable animated lesson)
    learn_res = requests.post(
        f"{BASE_URL}/api/documents/{doc_id}/learn-concept",
        json={"concept_name": chosen_concept, "learner_profile": "teen", "language": "te"},
        headers=headers
    )
    assert learn_res.status_code == 200, f"Learn concept failed: {learn_res.text}"
    learn_data = learn_res.json()
    proj = learn_data["project"]
    assert proj.get("id"), "Generated project must have an ID"
    assert len(proj.get("scenes", [])) >= 2, f"Generated project must contain scenes, got {len(proj.get('scenes', []))}"
    print(f"Test 8 Passed: End-to-end intelligence verified! Generated lesson '{proj.get('title')}' with {len(proj.get('scenes', []))} scenes.")

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
