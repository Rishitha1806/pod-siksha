import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--autoplay-policy=no-user-gesture-required')
driver = webdriver.Chrome(options=opts)

try:
    conn = sqlite3.connect(r'C:\Users\jvris\Downloads\pod-siksha\pod_siksha.db')
    latest_id = conn.execute('SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1').fetchone()[0]
    conn.close()
    print('Testing session:', latest_id)

    # 1. Load session
    driver.get(f'http://127.0.0.1:8008/?session_id={latest_id}')
    time.sleep(2)

    # Wait for audio to start
    for _ in range(10):
        t = driver.execute_script('return document.getElementById("audioPlayer").currentTime;')
        if t > 0:
            break
        time.sleep(0.5)

    print('Initial playback time:', t)
    assert t > 0

    # 2. Test Interruption (Hold mic button)
    hold_btn = driver.find_element(By.ID, 'holdButton')
    driver.execute_script('startHoldInterruption();')
    time.sleep(1)

    is_paused = driver.execute_script('return document.getElementById("audioPlayer").paused;')
    saved_ms = driver.execute_script('return savedPlaybackMs;')
    print(f'Podcast paused on interruption: {is_paused}, saved ms: {saved_ms}')
    assert is_paused is True
    assert saved_ms > 0

    # 3. Test exact resume
    driver.execute_script('resumeFromDoubt();')
    time.sleep(1)

    resumed_paused = driver.execute_script('return document.getElementById("audioPlayer").paused;')
    current_time = driver.execute_script('return document.getElementById("audioPlayer").currentTime;')
    print(f'Podcast resumed: {not resumed_paused}, current time: {current_time}')
    assert resumed_paused is False
    assert current_time >= saved_ms / 1000

    print('\n*** Interruption and Exact Resume: 100% PASSED ***')
finally:
    driver.quit()
