#!/usr/bin/env python3
"""
Database Migration: Phase 2 - Multimodal Intelligence, OCR & Pedagogical Knowledge.
Adds additive tables for:
- document_concepts: Educational concepts, definitions, prerequisites, objectives
- concept_relationships: Directed concept graph edges and dependency mappings
- document_figures: Multimodal analyses of diagrams, charts, graphs, flowcharts
- document_code_blocks: Programming snippets with indentation, language, sample I/O
- document_math_expressions: LaTeX equations, fractions, integrals, matrices
- document_ocr_results: OCR extractions for scanned pages with confidence & status
- teaching_strategies: Dynamic pedagogical recommendations and execution plans

Idempotent: Uses CREATE TABLE IF NOT EXISTS and CREATE INDEX IF NOT EXISTS.
Safe: Never deletes or modifies existing tables or records.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

from db_adapter import get_db

def run_migration():
    print("Connecting to database via db_adapter...")
    with get_db() as conn:
        print("Creating table: document_concepts...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_concepts (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                concept_name VARCHAR(255) NOT NULL,
                concept_type VARCHAR(64) DEFAULT 'core',
                definition TEXT,
                summary TEXT,
                prerequisites_json TEXT DEFAULT '[]',
                learning_objectives_json TEXT DEFAULT '[]',
                common_confusions_json TEXT DEFAULT '[]',
                examples_json TEXT DEFAULT '[]',
                source_page INT DEFAULT 1,
                confidence FLOAT DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating table: concept_relationships...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS concept_relationships (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                from_concept VARCHAR(255) NOT NULL,
                to_concept VARCHAR(255) NOT NULL,
                relationship_type VARCHAR(64) NOT NULL,
                evidence_text TEXT,
                weight FLOAT DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating table: document_figures...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_figures (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                page_number INT NOT NULL,
                figure_index INT DEFAULT 1,
                figure_type VARCHAR(64) DEFAULT 'diagram',
                caption TEXT,
                summary TEXT,
                detailed_explanation TEXT,
                visual_labels_json TEXT DEFAULT '[]',
                educational_significance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating table: document_code_blocks...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_code_blocks (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                page_number INT NOT NULL,
                language VARCHAR(64) DEFAULT 'python',
                purpose TEXT,
                code_text TEXT NOT NULL,
                algorithm_name VARCHAR(255),
                sample_inputs_json TEXT DEFAULT '[]',
                sample_outputs_json TEXT DEFAULT '[]',
                related_concepts_json TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating table: document_math_expressions...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_math_expressions (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                page_number INT NOT NULL,
                latex_expr TEXT NOT NULL,
                expression_type VARCHAR(64) DEFAULT 'equation',
                context_text TEXT,
                variables_json TEXT DEFAULT '{}',
                derivation_step INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating table: document_ocr_results...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_ocr_results (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                page_number INT NOT NULL,
                ocr_text TEXT NOT NULL,
                confidence FLOAT DEFAULT 0.95,
                provider VARCHAR(64) DEFAULT 'gemini_multimodal',
                has_handwriting BOOLEAN DEFAULT FALSE,
                processing_status VARCHAR(32) DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating table: teaching_strategies...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS teaching_strategies (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL,
                concept_name VARCHAR(255) NOT NULL,
                recommended_method VARCHAR(64) NOT NULL,
                rationale TEXT,
                suggested_animation_type VARCHAR(64),
                priority INT DEFAULT 1,
                step_plan_json TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Creating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_concepts_doc ON document_concepts(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_concept_rels_doc ON concept_relationships(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_figures_doc ON document_figures(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_code_doc ON document_code_blocks(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_math_doc ON document_math_expressions(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_ocr_doc ON document_ocr_results(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_teaching_strat_doc ON teaching_strategies(document_id)")

        conn.commit()
    print("Phase 2 database migration completed successfully!")

if __name__ == "__main__":
    run_migration()
