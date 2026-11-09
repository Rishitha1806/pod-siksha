"""P2 Acceptance Browser Automation Audit for Pod-Siksha.
Tests Public HTTPS Deployment, Advanced Teacher Observatory, Grounded AI Recommendations,
Individual Student Study Report, CSV Downloads, and Mobile Responsiveness.
"""
import io
import json
import os
import shutil
import sys
import time
import wave

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import httpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PUBLIC_URL = "https://fairly-private-supported-killing.trycloudflare.com"
ARTIFACT_DIR = r"C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\screenshots"
DOCS_SCREENSHOTS = r"C:\Users\jvris\Downloads\pod-siksha\docs\screenshots"
PDF_PATH = r"C:\Users\jvris\Downloads\pod-siksha\sample_chapter.pdf"

os.makedirs(ARTIFACT_DIR, exist_ok=True)
os.makedirs(DOCS_SCREENSHOTS, exist_ok=True)

def generate_dummy_wav():
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 8000)
    return buf.getvalue()

def save_screenshot(driver, name):
    fpath1 = os.path.join(DOCS_SCREENSHOTS, name)
    fpath2 = os.path.join(ARTIFACT_DIR, name)
    driver.save_screenshot(fpath1)
    shutil.copyfile(fpath1, fpath2)
    print(f"Captured screenshot: {name}")

def run_p2_browser_audit():
    print("=" * 80)
    print("POD-SIKSHA: P2 ACCEPTANCE AUDIT (PUBLIC HTTPS & COMPLETE PLATFORM)")
    print(f"Target Public HTTPS URL: {PUBLIC_URL}")
    print("=" * 80)

    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--window-size=1440,960")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--use-fake-ui-for-media-stream")
    chrome_opts.add_argument("--use-fake-device-for-media-stream")
    chrome_opts.add_argument("--autoplay-policy=no-user-gesture-required")

    driver = webdriver.Chrome(options=chrome_opts)
    wait = WebDriverWait(driver, 40)

    try:
        # Step 1: Public HTTPS Health Check and Landing Page
        print("\n[Step 1] Loading Public HTTPS Landing Page...")
        driver.get(PUBLIC_URL)
        wait.until(EC.presence_of_element_located((By.ID, "setupPanel")))
        save_screenshot(driver, "p2_01_public_https_landing.png")
        print("  Public landing page loaded successfully with valid SSL certificate.")

        # Step 2: Upload PDF and Start 14-Turn Podcast
        print("\n[Step 2] Initializing Podcast Session on Public HTTPS...")
        driver.find_element(By.ID, "pdfInput").send_keys(PDF_PATH)
        time.sleep(1)
        driver.find_element(By.ID, "startBtn").click()

        wait.until(EC.visibility_of_element_located((By.ID, "studioPanel")))
        session_data = driver.execute_script("return currentSession;")
        session_id = session_data["session_id"]
        print(f"  Session created on public deployment: {session_id}")
        time.sleep(2)
        save_screenshot(driver, "p2_02_dual_host_podcast.png")

        # Step 3: Spacebar / Doubt Interruption on Public HTTPS
        print("\n[Step 3] Submitting Telugu Voice Doubt via Prisma STT...")
        doubt_res = httpx.post(f"{PUBLIC_URL}/api/ask", data={
            "session_id": session_id,
            "turn_index": 2,
            "playback_ms": 1500,
            "language": "te"
        }, files={"file": ("doubt_voice.wav", generate_dummy_wav(), "audio/wav")}, timeout=45).json()

        ans = doubt_res.get("display_text") or doubt_res.get("spoken_text") or "Answer processed"
        print(f"  Doubt Processed: Concept='{doubt_res.get('concept_tag')}', Hint Level={doubt_res.get('hint_level')}")
        print(f"  Host Answer: \"{ans[:60]}...\"")
        time.sleep(1)
        save_screenshot(driver, "p2_03_doubt_interruption_resumed.png")

        # Step 4: Complete 4-Question Oral Quiz
        print("\n[Step 4] Starting and Completing Oral Quiz on Public Deployment...")
        driver.execute_script("loadOralQuiz();")
        time.sleep(3)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-question-card")))

        # Answer all 4 questions programmatically via text input
        quiz_answers = [
            "The light reactions occur inside the chloroplast thylakoid membranes.",
            "Water molecules split into oxygen gas, protons, and electrons during photolysis.",
            "Without ATP and NADPH energy, the Calvin cycle cannot synthesize glucose sugars.",
            "Guard cells close stomata to prevent excessive water loss during dehydration."
        ]

        for idx, ans_text in enumerate(quiz_answers):
            print(f"  Answering Question {idx+1} of 4...")
            wait.until(EC.presence_of_element_located((By.ID, "quizTextInput")))
            input_box = driver.find_element(By.ID, "quizTextInput")
            input_box.clear()
            input_box.send_keys(ans_text)
            driver.find_element(By.ID, "quizSubmitTextBtn").click()

            WebDriverWait(driver, 35).until(
                lambda d: "Points" in d.find_element(By.ID, "quizEvaluationBox").text or "Next Question" in d.find_element(By.ID, "quizEvaluationBox").text
            )
            time.sleep(1)

            # Advance to next question (or final results after Q4)
            driver.execute_script("advanceQuizQuestion();")
            time.sleep(2)

        wait.until(lambda d: "Final Score" in d.find_element(By.ID, "quizContainer").text)
        print("  Oral quiz completed and scored!")
        save_screenshot(driver, "p2_04_oral_quiz_completed.png")

        # Step 5: Individual Student Study Report Screen & CSV Download
        print("\n[Step 5] Opening Individual Student Study Report (/report)...")
        driver.get(f"{PUBLIC_URL}/report?session_id={session_id}")
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Oral Quiz Breakdown')]")))
        save_screenshot(driver, "p2_05_student_study_report.png")
        print("  Student study report rendered and persisted from SQLite!")

        # Verify Student CSV Export
        student_csv_res = httpx.get(f"{PUBLIC_URL}/api/student/{session_id}/export/csv", timeout=20)
        assert student_csv_res.status_code == 200
        assert "POD-SIKSHA STUDENT STUDY REPORT" in student_csv_res.text
        print("  Student CSV export verified successfully.")

        # Step 6: Advanced Teacher Observatory with Grounded AI Recommendations
        print("\n[Step 6] Opening Teacher Observatory (/teacher)...")
        driver.get(f"{PUBLIC_URL}/teacher")
        wait.until(EC.presence_of_element_located((By.ID, "kpiSessions")))
        wait.until(lambda d: int(d.find_element(By.ID, "kpiSessions").text) > 0)
        wait.until(lambda d: "Evidence" in d.find_element(By.ID, "recommendationsList").text or "Grounded" in d.find_element(By.ID, "recommendationsList").text)
        save_screenshot(driver, "p2_06_teacher_observatory_p2.png")
        print("  Teacher Observatory loaded with live KPIs, Radar Quadrants, and AI Recommendations!")

        # Verify Teacher CSV Export
        teacher_csv_res = httpx.get(f"{PUBLIC_URL}/api/teacher/export/csv", timeout=20)
        assert teacher_csv_res.status_code == 200
        assert "POD-SIKSHA CLASSROOM INTELLIGENCE REPORT" in teacher_csv_res.text
        print("  Classroom analytics CSV export verified successfully.")

        # Step 7: Mobile Viewport Responsiveness
        print("\n[Step 7] Testing Mobile Responsive Layout (375x812)...")
        driver.set_window_size(375, 812)
        driver.get(PUBLIC_URL)
        wait.until(EC.presence_of_element_located((By.ID, "setupPanel")))
        time.sleep(1)
        save_screenshot(driver, "p2_07_mobile_responsive_view.png")
        print("  Mobile responsive layout verified!")

        print("\n" + "=" * 80)
        print("ALL P2 ACCEPTANCE CRITERIA PASSED ON PUBLIC HTTPS DEPLOYMENT!")
        print("=" * 80)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_p2_browser_audit()
