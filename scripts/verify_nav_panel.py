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

base_url = "http://127.0.0.1:8008"

driver = webdriver.Chrome(options=opts)

try:
    print("Testing navigation panel visibility on login page vs authenticated page...")

    # 1. Open root unauthenticated -> Login page
    driver.get(f"{base_url}/")
    time.sleep(2.0)

    active_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"1. Active screen on root load: {active_screen}")
    assert active_screen == "view-login", f"Expected view-login, got {active_screen}"

    # Check navigation panel visibility on login page
    nav_display = driver.execute_script("""
        const nav = document.getElementById('mainScreenSwitcher') || document.querySelector('.screen-switcher-bar');
        if (!nav) return 'not_found';
        const style = window.getComputedStyle(nav);
        return {
            display: style.display,
            visibility: style.visibility,
            offsetParent: nav.offsetParent !== null,
            offsetWidth: nav.offsetWidth,
            offsetHeight: nav.offsetHeight
        };
    """)
    print(f"2. Navigation panel computed state on login page: {nav_display}")
    assert nav_display["display"] == "none", f"Expected display: none, got {nav_display['display']}"
    assert nav_display["offsetParent"] is False, "Navigation panel should not be rendered on login page"
    driver.save_screenshot(os.path.join(shots_dir, "nav_panel_01_hidden_on_login.png"))
    print("   -> Screenshot saved: nav_panel_01_hidden_on_login.png (Navigation panel verified REMOVED from login page!)")

    # 3. Check registration page
    driver.get(f"{base_url}/#register")
    time.sleep(1.0)
    reg_nav = driver.execute_script("""
        const nav = document.getElementById('mainScreenSwitcher') || document.querySelector('.screen-switcher-bar');
        return window.getComputedStyle(nav).display;
    """)
    print(f"3. Navigation panel on #register: {reg_nav}")
    assert reg_nav == "none", f"Expected display: none on register, got {reg_nav}"

    # 4. Log in
    driver.get(f"{base_url}/#login")
    time.sleep(1.0)
    driver.execute_script("""
        document.getElementById('loginEmail').value = 'learner@demo.in';
        document.getElementById('loginPass').value = 'podsiksha2026';
        document.getElementById('btnLoginSubmit').click();
    """)
    time.sleep(3.0)

    post_login_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    print(f"4. Post-login active screen: {post_login_screen}")
    assert post_login_screen == "view-home", f"Expected view-home, got {post_login_screen}"

    # Check navigation panel visibility after login
    post_login_nav = driver.execute_script("""
        const nav = document.getElementById('mainScreenSwitcher') || document.querySelector('.screen-switcher-bar');
        if (!nav) return 'not_found';
        const style = window.getComputedStyle(nav);
        return {
            display: style.display,
            visibility: style.visibility,
            offsetParent: nav.offsetParent !== null,
            offsetWidth: nav.offsetWidth,
            offsetHeight: nav.offsetHeight
        };
    """)
    print(f"5. Navigation panel computed state AFTER login: {post_login_nav}")
    assert post_login_nav["display"] == "flex", f"Expected display: flex, got {post_login_nav['display']}"
    assert post_login_nav["offsetParent"] is True, "Navigation panel should be rendered and visible after login"
    driver.save_screenshot(os.path.join(shots_dir, "nav_panel_02_visible_after_login.png"))
    print("   -> Screenshot saved: nav_panel_02_visible_after_login.png (Navigation panel verified VISIBLE after login!)")

    # 5. Log out
    driver.execute_script("AuthManager.logout();")
    time.sleep(1.5)
    post_logout_screen = driver.execute_script("const active = document.querySelector('.screen-frame.active'); return active ? active.id : null;")
    post_logout_nav = driver.execute_script("""
        const nav = document.getElementById('mainScreenSwitcher') || document.querySelector('.screen-switcher-bar');
        return window.getComputedStyle(nav).display;
    """)
    print(f"6. Post-logout screen: {post_logout_screen}, nav display: {post_logout_nav}")
    assert post_logout_screen == "view-login"
    assert post_logout_nav == "none", "Navigation panel must hide immediately upon logout"
    driver.save_screenshot(os.path.join(shots_dir, "nav_panel_03_hidden_again_on_logout.png"))

    print("\nSUCCESS: All navigation panel visibility checks PASSED completely!")

finally:
    driver.quit()
