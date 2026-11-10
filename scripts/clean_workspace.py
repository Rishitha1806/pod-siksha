import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("\r\n", "\n")

# Remove "Test Sample Answer" button
html = re.sub(
    r'<button class="btn-chime-test" onclick="showToast\(\'Sample answer submitted:.*?\).*?</button>',
    '',
    html,
    flags=re.DOTALL
)

# Clean workspace mock citations
old_citations = """          <div class="source-quote-block">
            <span style="font-size:11px; font-weight:800; text-transform:uppercase; color:var(--accent-celadon);">Page 12 ? Equation</span>
            <p style="margin-top:4px;">
              "6CO2 + 6H2O + Solar Photons &rarr; C6H12O6 + 6O2. The light reactions take place exclusively across thylakoid membranes."
            </p>
          </div>

          <div class="source-quote-block" style="border-left-color:var(--accent-terracotta);">
            <span style="font-size:11px; font-weight:800; text-transform:uppercase; color:var(--accent-terracotta);">Page 13 ? Diagnostic Focus</span>
            <p style="margin-top:4px;">
              "Photolysis of water (2H2O &rarr; 4H+ + 4e- + O2) occurs within the thylakoid lumen to replenish electrons lost by excited chlorophyll."
            </p>
          </div>"""

new_citations = """          <div class="source-quote-block" style="background:var(--surface-tinted); border-left-color:var(--accent-celadon);">
            <span style="font-size:11px; font-weight:800; text-transform:uppercase; color:var(--accent-celadon);">Grounded Evidence</span>
            <p style="margin-top:4px; font-size:13px; color:var(--ink-secondary);">
              Textbook citations, formulas, and code snippets extracted from your uploaded documents will be grounded here alongside active lessons.
            </p>
          </div>"""

html = re.sub(
    r'<div class="source-quote-block">.*?</div>\s*<div class="source-quote-block".*?</div>',
    new_citations.strip(),
    html,
    flags=re.DOTALL
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished cleaning workspace.")
