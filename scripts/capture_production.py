import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1440,1050')
driver = webdriver.Chrome(options=opts)

artifact_dir = r"C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\screenshots"
docs_dir = r"C:\Users\jvris\Downloads\pod-siksha\docs\screenshots"
os.makedirs(artifact_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

try:
    # 1. Open root production page
    driver.get("http://127.0.0.1:8008/")
    time.sleep(2)

    # 2. Login as demo user so that authenticated state and personal journeys load
    driver.execute_script("""
        localStorage.setItem('ps_token', 'session_demo_learner_001');
        localStorage.setItem('ps_user', JSON.stringify({
            id: 'user_demo_001',
            email: 'learner@demo.in',
            full_name: 'Rishitha J.V.',
            preferred_language: 'te'
        }));
        checkAuthStatus();
    """)
    time.sleep(1)

    screens = [
        ("landing", "prod_01_landing.png"),
        ("login", "prod_02_login.png"),
        ("register", "prod_03_register.png"),
        ("home", "prod_04_personal_home.png"),
        ("insights", "prod_05_learning_insights.png"),
        ("studio", "prod_06_learning_studio.png"),
        ("workspace", "prod_07_learning_workspace.png"),
        ("concept-dna", "prod_08_concept_dna.png"),
        ("teachback", "prod_09_teachback.png")
    ]

    for screen_id, filename in screens:
        driver.execute_script(f'switchScreen("{screen_id}");')
        time.sleep(1.2)
        art_path = os.path.join(artifact_dir, filename)
        doc_path = os.path.join(docs_dir, filename)
        driver.save_screenshot(art_path)
        driver.save_screenshot(doc_path)
        print(f"Captured production {screen_id} -> {filename} ({os.path.getsize(art_path)} bytes)")

    # Mobile Views (390 x 844)
    driver.set_window_size(390, 844)
    driver.execute_script('switchScreen("home");')
    time.sleep(1.0)
    driver.save_screenshot(os.path.join(artifact_dir, "prod_10_mobile_home.png"))
    driver.save_screenshot(os.path.join(docs_dir, "prod_10_mobile_home.png"))
    print("Captured production mobile home view (390x844)")

    driver.execute_script('switchScreen("studio");')
    time.sleep(1.0)
    driver.save_screenshot(os.path.join(artifact_dir, "prod_11_mobile_studio.png"))
    driver.save_screenshot(os.path.join(docs_dir, "prod_11_mobile_studio.png"))
    print("Captured production mobile studio view (390x844)")

    print("All 11 production Aura Atelier screenshots captured successfully!")
finally:
    driver.quit()
