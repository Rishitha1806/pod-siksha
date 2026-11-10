"""
Makes chapter text / paragraph input optional in both frontend modal and backend endpoint.
If only a chapter title is provided, Gemini generates the full curriculum from the title.
"""

import re

# 1. Update static/index.html
INDEX_PATH = r"C:\Users\jvris\Downloads\pod-siksha\static\index.html"
with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Update label & placeholder
OLD_LABEL = """        <div class="form-field">
          <label>Or Paste Chapter Text</label>
          <textarea id="modalSessionText" class="form-input" rows="4" placeholder="Paste textbook paragraphs here (minimum 50 characters)..."></textarea>
        </div>"""

NEW_LABEL = """        <div class="form-field">
          <label>Paste Chapter Text (Optional)</label>
          <textarea id="modalSessionText" class="form-input" rows="4" placeholder="Optional: Paste textbook paragraphs or notes. If left blank, Gemini will generate the curriculum from the title."></textarea>
        </div>"""

if OLD_LABEL in html:
    html = html.replace(OLD_LABEL, NEW_LABEL)
    print("Updated modal label and placeholder in index.html.")

# Update validation in submitNewSession
OLD_VALIDATION = """      if (!fileInput.files.length && text.length < 50) {
        showToast("Please provide at least 50 characters of chapter text or upload a PDF.");
        return;
      }"""

NEW_VALIDATION = """      if (!title && !fileInput.files.length && !text) {
        showToast("Please provide a journey title, upload a PDF, or paste text.");
        return;
      }"""

if OLD_VALIDATION in html:
    html = html.replace(OLD_VALIDATION, NEW_VALIDATION)
    print("Updated submitNewSession validation in index.html.")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)


# 2. Update server.py
SERVER_PATH = r"C:\Users\jvris\Downloads\pod-siksha\server.py"
with open(SERVER_PATH, "r", encoding="utf-8") as f:
    server_code = f.read()

OLD_SERVER_LOGIC = """    text_content = ""
    if file and file.filename:
        pdf_bytes = await file.read()
        text_content = extract_text_from_pdf(pdf_bytes)
        if not title:
            title = file.filename.replace(".pdf", "")
    elif chapter_text:
        text_content = chapter_text.strip()
    
    if not text_content or len(text_content) < 50:
        raise HTTPException(status_code=400, detail="Chapter content is too short or missing. Please provide at least 50 characters.")"""

NEW_SERVER_LOGIC = """    text_content = ""
    if file and file.filename:
        pdf_bytes = await file.read()
        text_content = extract_text_from_pdf(pdf_bytes)
        if not title:
            title = file.filename.replace(".pdf", "")
    elif chapter_text and chapter_text.strip():
        text_content = chapter_text.strip()
    elif title and title.strip():
        text_content = f"Comprehensive curriculum on {title.strip()}. Core definitions, fundamental principles, real-world examples, and key mechanisms."
    
    if not text_content:
        raise HTTPException(status_code=400, detail="Please provide a chapter title, paste text, or upload a PDF.")

    if len(text_content) < 50:
        text_content = f"Comprehensive curriculum on {text_content}. Core definitions, fundamental principles, real-world examples, and key mechanisms." """

if OLD_SERVER_LOGIC in server_code:
    server_code = server_code.replace(OLD_SERVER_LOGIC, NEW_SERVER_LOGIC)
    print("Updated /api/session in server.py.")

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(server_code)

print("Both static/index.html and server.py updated successfully!")
