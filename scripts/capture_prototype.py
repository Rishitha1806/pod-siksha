import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1440,1100')
driver = webdriver.Chrome(options=opts)

artifact_dir = r"C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\screenshots"
docs_dir = r"C:\Users\jvris\Downloads\pod-siksha\docs\screenshots"
os.makedirs(artifact_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

try:
    driver.get("http://127.0.0.1:8008/prototype")
    time.sleep(2)

    screens = [
        ("insights", "proto_01_learning_insights.png"),
        ("home", "proto_02_home_landing.png"),
        ("studio", "proto_03_learning_studio.png"),
        ("workspace", "proto_04_learning_workspace.png")
    ]

    for screen_id, filename in screens:
        driver.execute_script(f'showScreen("{screen_id}");')
        time.sleep(1)
        art_path = os.path.join(artifact_dir, filename)
        doc_path = os.path.join(docs_dir, filename)
        driver.save_screenshot(art_path)
        driver.save_screenshot(doc_path)
        print(f"Captured {screen_id} -> {filename} ({os.path.getsize(art_path)} bytes)")

    print("All screenshots captured successfully!")
finally:
    driver.quit()
