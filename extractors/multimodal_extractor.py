"""
Real Multimodal Document Extractor for Universal AI Educator.
Rasterizes PDF pages containing figures, diagrams, chemical reactions, flowcharts,
and mathematical graphs using PyMuPDF (fitz), then passes them to Google Gemini Multimodal Vision
to perform in-depth pedagogical visual decomposition, extract visual labels, and connect diagrams
to the surrounding curriculum context.
"""

import os
import io
import re
import json
import uuid
import hashlib
import logging
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF

from extractors.base import BaseExtractor, ExtractionResult, ExtractedSection
from db_adapter import get_db

log = logging.getLogger("pod_siksha.multimodal")

class MultimodalDocumentExtractor(BaseExtractor):
    """Decomposes diagrams, graphs, charts, and technical illustrations into structured educational knowledge."""

    def __init__(self, gemini_client=None):
        self.client = gemini_client
        if not self.client:
            try:
                from google import genai
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    self.client = genai.Client(api_key=api_key)
            except Exception as e:
                log.warning("Could not auto-initialize Gemini client for Multimodal: %s", e)

    def get_extractor_name(self) -> str:
        return "gemini_multimodal_vision"

    def page_has_visual_figures(self, page) -> bool:
        """Determines if a page contains images, complex vector drawings, or diagrams."""
        images = page.get_images()
        drawings = page.get_drawings()
        # Pages with embedded raster images or significant vector drawing paths
        return len(images) > 0 or len(drawings) >= 5

    def analyze_page_visuals(self, img_bytes: bytes, page_number: int, context_text: str = "") -> List[Dict[str, Any]]:
        """Invokes Gemini Multimodal Vision to analyze visual elements on the page."""
        if not self.client:
            log.warning("Gemini client unavailable for visual analysis.")
            return []

        from google.genai import types

        prompt = f"""You are an expert pedagogical diagram analyst for an AI Universal Educator.
Examine this high-resolution document image of Page {page_number}.
Context surrounding this page: "{context_text[:1000]}"

Identify all educational visual elements:
- Scientific diagrams (biology anatomy, cellular structures, physics setups)
- Mathematical graphs (functions, coordinate axes, vectors, distributions)
- Flowcharts & system architectures (algorithms, data pipelines, decision trees)
- Chemical reaction pathways & molecular structures
- Code screenshots or UI wireframes
- Research paper charts, bar plots, line plots, heatmaps, and tables

For each distinct visual figure detected on this page, extract:
1. figure_type: "diagram" | "graph" | "flowchart" | "chart" | "chemical_structure" | "code_screenshot" | "technical_drawing"
2. caption: Title or caption from the document (e.g. "Figure 3.2: Calvin-Benson Cycle")
3. summary: Concise 1-2 sentence overview of what the figure illustrates.
4. detailed_explanation: Clear step-by-step educational breakdown of its parts and dynamics.
5. visual_labels: Key text callouts/labels visible in the image.
6. educational_significance: What core lesson or concept the student must learn from this visual.

Respond strictly with valid JSON matching this schema:
{{
  "figures": [
    {{
      "figure_type": "diagram",
      "caption": "Figure title or caption",
      "summary": "Concise summary",
      "detailed_explanation": "Comprehensive breakdown",
      "visual_labels": ["Label A", "Label B", "Label C"],
      "educational_significance": "Core learning objective"
    }}
  ]
}}
If no educational visual figures exist (e.g. plain text only), return {{"figures": []}}.
"""
        models_to_try = [os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"), "gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
        for model in models_to_try:
            try:
                part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
                res = self.client.models.generate_content(
                    model=model,
                    contents=[part, prompt],
                    config={"response_mime_type": "application/json"}
                )
                raw_json = res.text.strip()
                raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json, flags=re.MULTILINE)
                raw_json = re.sub(r"\s*```$", "", raw_json, flags=re.MULTILINE)
                parsed = json.loads(raw_json)
                return parsed.get("figures", [])
            except Exception as e:
                log.warning("Multimodal analysis attempt on model %s page %d failed: %s", model, page_number, e)
                continue

        return []

    def extract(self, file_bytes: bytes, filename: str, document_id: Optional[str] = None) -> ExtractionResult:
        """Extracts and analyzes all visual diagrams across the document."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        sections: List[ExtractedSection] = []
        figures_extracted = []

        # Cost-control: examine up to 10 pages with highest visual density
        candidate_pages = []
        for p_idx in range(total_pages):
            page = doc[p_idx]
            if self.page_has_visual_figures(page):
                candidate_pages.append(p_idx)

        # Cap at first 8 visual pages to balance deep intelligence with performance & cost
        selected_pages = candidate_pages[:8]
        log.info("Document %s: found %d visual candidate pages, analyzing %d pages", filename, len(candidate_pages), len(selected_pages))

        for p_idx in selected_pages:
            page_num = p_idx + 1
            page = doc[p_idx]
            raw_text = page.get_text()[:600]

            # Rasterize page to PNG
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")

            figs = self.analyze_page_visuals(img_bytes, page_num, raw_text)
            for f_idx, fig in enumerate(figs):
                fig_type = fig.get("figure_type", "diagram")
                caption = fig.get("caption", f"Figure {page_num}.{f_idx + 1}")
                summary = fig.get("summary", "")
                detailed = fig.get("detailed_explanation", "")
                labels = fig.get("visual_labels", [])
                significance = fig.get("educational_significance", "")

                fig_id = str(uuid.uuid4())
                figures_extracted.append({
                    "id": fig_id,
                    "page_number": page_num,
                    "figure_index": f_idx + 1,
                    "figure_type": fig_type,
                    "caption": caption,
                    "summary": summary,
                    "detailed_explanation": detailed,
                    "visual_labels": labels,
                    "educational_significance": significance
                })

                # Persist in document_figures table
                if document_id:
                    try:
                        with get_db() as conn:
                            conn.execute("""
                                INSERT INTO document_figures (
                                    id, document_id, page_number, figure_index,
                                    figure_type, caption, summary, detailed_explanation,
                                    visual_labels_json, educational_significance
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                fig_id, document_id, page_num, f_idx + 1,
                                fig_type, caption, summary, detailed,
                                json.dumps(labels), significance
                            ))
                            conn.commit()
                    except Exception as db_err:
                        log.warning("Could not persist document_figure for doc %s: %s", document_id, db_err)

                sections.append(ExtractedSection(
                    page_number=page_num,
                    section_index=len(sections) + 1,
                    section_title=caption,
                    content_type="figure",
                    content=f"[{fig_type.upper()}: {caption}]\nSummary: {summary}\nDetails: {detailed}\nSignificance: {significance}",
                    metadata={
                        "figure_id": fig_id,
                        "figure_type": fig_type,
                        "visual_labels": labels,
                        "caption": caption
                    }
                ))

        doc.close()
        return ExtractionResult(
            document_id=document_id or "",
            filename=filename,
            total_pages=total_pages,
            sections=sections,
            full_text="\n\n".join(s.content for s in sections),
            metadata={
                "figures_count": len(figures_extracted),
                "analyzed_pages": [p + 1 for p in selected_pages],
                "extractor": self.get_extractor_name()
            }
        )
