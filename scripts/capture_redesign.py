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
    driver.get("http://127.0.0.1:8008/redesign")
    time.sleep(2)

    screens = [
        ("landing", "redesign_01_landing.png"),
        ("login", "redesign_02_login.png"),
        ("register", "redesign_03_register.png"),
        ("home", "redesign_04_personal_home.png"),
        ("insights", "redesign_05_learning_insights.png"),
        ("studio", "redesign_06_learning_studio.png"),
        ("workspace", "redesign_07_learning_workspace.png"),
        ("concept-dna", "redesign_08_concept_dna.png"),
        ("teachback", "redesign_09_teachback.png")
    ]

    for screen_id, filename in screens:
        driver.execute_script(f'switchScreen("{screen_id}");')
        time.sleep(0.8)
        art_path = os.path.join(artifact_dir, filename)
        doc_path = os.path.join(docs_dir, filename)
        driver.save_screenshot(art_path)
        driver.save_screenshot(doc_path)
        print(f"Captured {screen_id} -> {filename} ({os.path.getsize(art_path)} bytes)")

    # Also capture mobile view of Landing and Studio (390 x 844)
    driver.set_window_size(390, 844)
    driver.execute_script('switchScreen("landing");')
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(artifact_dir, "redesign_10_mobile_landing.png"))
    driver.save_screenshot(os.path.join(docs_dir, "redesign_10_mobile_landing.png"))
    print("Captured mobile landing view (390x844)")

    driver.execute_script('switchScreen("studio");')
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(artifact_dir, "redesign_11_mobile_studio.png"))
    driver.save_screenshot(os.path.join(docs_dir, "redesign_11_mobile_studio.png"))
    print("Captured mobile studio view (390x844)")

    print("All 11 redesign screenshots captured successfully!")
finally:
    driver.quit()
