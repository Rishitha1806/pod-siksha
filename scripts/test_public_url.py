from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time

shots_dir = os.path.join(r"C:\Users\jvris\.gemini\antigravity\brain\23d34354-39ca-40f8-aad7-0b7b2c82bbc3\screenshots")
os.makedirs(shots_dir, exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1440,900")
opts.add_argument("--incognito")

base_url = "https://fairly-private-supported-killing.trycloudflare.com"

try:
    driver = webdriver.Chrome(options=opts)
    print("Chrome headless incognito webdriver initialized.")

    # 1. Unauthenticated root navigation -> MUST display LOGIN page immediately
    driver.get(f"{base_url}/")
    time.sleep(2.5)
    root_hash = driver.execute_script("return window.location.hash;")
    active_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"Step 1: Unauthenticated root navigation resulted in screen: '{active_screen}', hash: '{root_hash}'")
    assert active_screen == "view-login", f"Expected view-login, got {active_screen}"
    driver.save_screenshot(os.path.join(shots_dir, "public_01_root_opens_login.png"))

    # 2. Attempt to open #landing while unauthenticated -> MUST redirect to login
    driver.get(f"{base_url}/#landing")
    time.sleep(1.5)
    landing_attempt_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"Step 2: #landing attempt resulted in screen: '{landing_attempt_screen}'")
    assert landing_attempt_screen == "view-login", f"Expected view-login, got {landing_attempt_screen}"

    # 3. Attempt to open #home while unauthenticated -> MUST redirect to login
    driver.get(f"{base_url}/#home")
    time.sleep(1.5)
    home_attempt_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"Step 3: #home attempt resulted in screen: '{home_attempt_screen}'")
    assert home_attempt_screen == "view-login", f"Expected view-login, got {home_attempt_screen}"

    # 4. Navigate to register page via 'Create one'
    driver.get(f"{base_url}/#register")
    time.sleep(1.5)
    reg_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"Step 4: #register resulted in screen: '{reg_screen}'")
    assert reg_screen == "view-register", f"Expected view-register, got {reg_screen}"
    driver.save_screenshot(os.path.join(shots_dir, "public_02_register_page.png"))

    # 5. Log in with credentials
    driver.get(f"{base_url}/#login")
    time.sleep(1.5)
    driver.execute_script("""
        document.getElementById('loginEmail').value = 'learner@demo.in';
        document.getElementById('loginPass').value = 'podsiksha2026';
        document.getElementById('btnLoginSubmit').click();
    """)
    time.sleep(3.0)

    post_login_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    post_login_hash = driver.execute_script("return window.location.hash;")
    print(f"Step 5: Post-login screen: '{post_login_screen}', hash: '{post_login_hash}'")
    assert post_login_screen == "view-home", f"Expected view-home, got {post_login_screen}"
    driver.save_screenshot(os.path.join(shots_dir, "public_03_authenticated_home.png"))

    # 6. Test authenticated page refresh -> MUST remain on home
    driver.refresh()
    time.sleep(2.5)
    refresh_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"Step 6: Authenticated refresh screen: '{refresh_screen}'")
    assert refresh_screen == "view-home", f"Expected view-home, got {refresh_screen}"

    # 7. Test logout redirect -> MUST redirect immediately to LOGIN
    driver.execute_script("AuthManager.logout();")
    time.sleep(2.0)
    post_logout_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    post_logout_hash = driver.execute_script("return window.location.hash;")
    print(f"Step 7: Post-logout screen: '{post_logout_screen}', hash: '{post_logout_hash}'")
    assert post_logout_screen == "view-login", f"Expected view-login, got {post_logout_screen}"
    driver.save_screenshot(os.path.join(shots_dir, "public_04_post_logout_login.png"))

    # 8. Verify demo credentials are NOT in DOM
    demo_btn_count = driver.execute_script("return document.querySelectorAll('.btn-demo-fill, [onclick*=\"fillDemoCredentials\"]').length;")
    print(f"Step 8: Demo helper buttons in DOM: {demo_btn_count}")
    assert demo_btn_count == 0, "Exposed demo credentials found in DOM!"

    print("\n=======================================================")
    print("ALL 7 CRITICAL PUBLIC URL TESTS PASSED COMPLETELY!")
    print(f"Public URL: {base_url}")
    print("=======================================================")

except Exception as e:
    print(f"\nTEST FAILED: {e}")
finally:
    driver.quit()
