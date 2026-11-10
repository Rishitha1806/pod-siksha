import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

out_dir_artifact = r"C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\screenshots"
out_dir_repo = r"C:\Users\jvris\Downloads\pod-siksha\docs\screenshots"
os.makedirs(out_dir_artifact, exist_ok=True)
os.makedirs(out_dir_repo, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1440,900")

driver = webdriver.Chrome(options=chrome_options)
try:
    url = "http://127.0.0.1:8008"
    driver.get(url)
    time.sleep(2)

    # 1. Login page
    driver.save_screenshot(os.path.join(out_dir_artifact, "final_01_login.png"))
    driver.save_screenshot(os.path.join(out_dir_repo, "final_01_login.png"))
    print("Saved final_01_login.png")

    # 2. Login as existing user
    driver.find_element(By.ID, "loginEmail").send_keys("e2e_user_a_1794309417@podsiksha.edu")
    driver.find_element(By.ID, "loginPass").send_keys("TestPassword@123")
    driver.find_element(By.ID, "btnLoginSubmit").click()
    time.sleep(3)

    driver.save_screenshot(os.path.join(out_dir_artifact, "final_02_atelier_home.png"))
    driver.save_screenshot(os.path.join(out_dir_repo, "final_02_atelier_home.png"))
    print("Saved final_02_atelier_home.png")

    # 3. Open Dual-Entry Modal (Document Tab)
    driver.execute_script("openNewChapterModal()")
    time.sleep(1)
    driver.save_screenshot(os.path.join(out_dir_artifact, "final_03_dual_entry_modal.png"))
    driver.save_screenshot(os.path.join(out_dir_repo, "final_03_dual_entry_modal.png"))
    print("Saved final_03_dual_entry_modal.png")

    # Switch to Topic Tab (Paragraph text optional)
    driver.execute_script("switchModalEntryTab('topic')")
    time.sleep(1)
    driver.save_screenshot(os.path.join(out_dir_artifact, "final_04_modal_topic_tab.png"))
    driver.save_screenshot(os.path.join(out_dir_repo, "final_04_modal_topic_tab.png"))
    print("Saved final_04_modal_topic_tab.png")

    # 4. Open Animated Studio
    driver.execute_script("closeNewChapterModal()")
    driver.execute_script("switchScreen('animated-studio')")
    time.sleep(2)
    driver.save_screenshot(os.path.join(out_dir_artifact, "final_05_animated_studio.png"))
    driver.save_screenshot(os.path.join(out_dir_repo, "final_05_animated_studio.png"))
    print("Saved final_05_animated_studio.png")

finally:
    driver.quit()
print("All screenshots captured successfully!")
