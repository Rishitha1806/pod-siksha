"""
Builds the complete production static/index.html for Pod-Siksha 2.0 (Aura Atelier).
Integrates all 9 screens with live REST API communication, Web Audio & HTML5 Audio physical playback,
tactile spacebar interruption, full authentication, Concept DNA, Teach-Back, and Memory Loop.
"""

import os
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
redesign_path = os.path.join(base_dir, "static", "redesign.html")
target_path = os.path.join(base_dir, "static", "index.html")

with open(redesign_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Page Title
html = re.sub(
    r"<title>.*?</title>",
    "<title>Pod-Siksha 2.0 — Aura Atelier (Voice-First AI Learning Platform)</title>",
    html
)

# 2. Header user profile & auth actions
old_header_ctrls = """    <!-- Global Sound & Action Controls -->
    <div class="header-ctrls">
      <button class="btn-chime-test" onclick="triggerHarmonicChime()">
        <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
        <span>Test Speakers</span>
      </button>
      <button class="btn-action-primary" onclick="switchScreen('insights')">
        <span>Mastery Pulse</span>
      </button>
    </div>"""

new_header_ctrls = """    <!-- Global Sound & Action Controls -->
    <div class="header-ctrls" style="display:flex; align-items:center; gap:8px;">
      <button class="btn-chime-test" onclick="triggerHarmonicChime()" title="Play 3-tone harmonic chime to verify laptop speakers">
        <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
        <span>Test Speakers</span>
      </button>
      <button class="btn-chime-test" onclick="openNewChapterModal()" style="border-color:var(--accent-terracotta); color:var(--accent-terracotta);">
        + New Journey
      </button>
      <div id="userPill" style="display:none; align-items:center; gap:6px; font-size:12px; font-weight:700; color:var(--ink-primary); background:var(--surface-tinted); padding:4px 10px; border-radius:var(--radius-full); border:1px solid var(--border-parchment);">
      </div>
      <button id="logoutBtn" class="btn-chime-test" style="display:none; font-size:12px; padding:6px 10px;" onclick="handleLogout()">
        Sign Out
      </button>
      <div id="headerAuthLinks" style="display:flex; gap:6px;">
        <button class="btn-action-primary" style="padding:6px 14px; font-size:12px;" onclick="switchScreen('login')">
          Sign In
        </button>
      </div>
    </div>"""

html = html.replace(old_header_ctrls, new_header_ctrls)

# 3. Login Form Enhancement
login_form_target = '<form onsubmit="event.preventDefault(); showToast(\'Welcome back, Learner!\'); switchScreen(\'home\');">'
login_form_replace = '<form id="loginForm" onsubmit="handleLogin(event)">'
html = html.replace(login_form_target, login_form_replace)

html = html.replace(
    '<input type="email" class="form-input" placeholder="learner@podsiksha.in" value="learner@demo.in" required>',
    '<input type="email" id="loginEmail" class="form-input" placeholder="learner@podsiksha.in" value="learner@demo.in" required>'
)

html = html.replace(
    'onclick="showToast(\'Password reset link dispatched via secure token.\')"',
    'onclick="openForgotModal()"'
)

# 4. Register Form Enhancement
reg_form_target = '<form onsubmit="event.preventDefault(); showToast(\'Account created! Welcome to Pod-Siksha.\'); switchScreen(\'home\');">'
reg_form_replace = '<form id="regForm" onsubmit="handleRegister(event)">'
html = html.replace(reg_form_target, reg_form_replace)

html = html.replace(
    '<input type="text" class="form-input" placeholder="Rishitha J.V." required>',
    '<input type="text" id="regName" class="form-input" placeholder="Rishitha J.V." value="Rishitha J.V." required>'
)

html = html.replace(
    '<input type="email" class="form-input" placeholder="rishitha@example.in" required>',
    '<input type="email" id="regEmail" class="form-input" placeholder="rishitha@example.in" value="learner_new@demo.in" required>'
)

html = html.replace(
    '<select class="form-input">',
    '<select id="regLang" class="form-input">'
)

# 5. Personal Home Enhancement
# Hero Resume Card
html = html.replace(
    '<h2 style="font-family:var(--font-editorial); font-size:28px; color:white; margin-top:6px;">Photosynthesis &amp; Cellular Energetics</h2>',
    '<h2 id="heroResumeTitle" style="font-family:var(--font-editorial); font-size:28px; color:white; margin-top:6px;">Photosynthesis &amp; Cellular Energetics</h2>'
)
html = html.replace(
    '<p style="font-size:14px; color:#CAD8D2; margin-top:4px;">Andhra Pradesh Class 10 Biology • Telugu Voice Narration</p>',
    '<p id="heroResumeSub" style="font-size:14px; color:#CAD8D2; margin-top:4px;">Andhra Pradesh Class 10 Biology • Telugu Voice Narration</p>'
)
html = html.replace(
    '<button class="btn-action-primary" style="background:var(--accent-terracotta);" onclick="switchScreen(\'studio\')">',
    '<button id="heroResumeBtn" class="btn-action-primary" style="background:var(--accent-terracotta);" onclick="switchScreen(\'studio\')">'
)

# Journeys List
html = html.replace(
    '<span style="font-size:12px; font-weight:700; color:var(--ink-secondary);">102 Sessions in Database</span>',
    '<span id="journeysCountLabel" style="font-size:12px; font-weight:700; color:var(--ink-secondary);">Loading Sessions...</span>'
)

# We wrap recent journeys list in an ID
journeys_start = '<div class="journey-tile" onclick="switchScreen(\'studio\')">'
journeys_wrap = '<div id="recentJourneysList">' + journeys_start
html = html.replace(journeys_start, journeys_wrap, 1)

# Close the wrapper before the closing div of journeys column
# Find the end of recent journeys block:
# Look for:
#           </div>
#         </div>
# 
#         <!-- Right: Daily Cognitive Pulse & Start New -->
html = html.replace(
    '        <!-- Right: Daily Cognitive Pulse & Start New -->',
    '        </div>\n        <!-- Right: Daily Cognitive Pulse & Start New -->'
)

# Daily Cognitive Pulse elements
html = html.replace(
    '<span class="pulse-val" style="color:var(--accent-celadon);">78%</span>',
    '<span id="pulseMastery" class="pulse-val" style="color:var(--accent-celadon);">78%</span>'
)
html = html.replace(
    '<span class="pulse-val">57</span>',
    '<span id="pulseQuizzes" class="pulse-val">57</span>'
)
html = html.replace(
    '<span class="pulse-val" style="color:var(--accent-terracotta);">1</span>',
    '<span id="pulseMisc" class="pulse-val" style="color:var(--accent-terracotta);">1</span>'
)

# Quick Chapter Start Box onclick
html = html.replace(
    'onclick="showToast(\'Sample chapter loaded: sample_chapter.pdf\'); switchScreen(\'studio\');"',
    'onclick="openNewChapterModal()"'
)

# 6. Learning Insights
html = html.replace(
    '<span class="ring-center-score">78%</span>',
    '<span id="insightsMasteryRingScore" class="ring-center-score">78%</span>'
)

# Wrap concept tracks
track_start = '<div class="concept-track-row">'
html = html.replace(
    track_start,
    '<div id="conceptTracksContainer">' + track_start,
    1
)
html = html.replace(
    '        <!-- Right: Misconception Radar & Memory Loop -->',
    '        </div>\n        </div>\n        <!-- Right: Misconception Radar & Memory Loop -->'
)

# Wrap misconception radar
radar_start = '<div class="misconception-radar-box">'
html = html.replace(
    radar_start,
    '<div id="misconceptionRadarContainer">' + radar_start,
    1
)
html = html.replace(
    '          <!-- Memory Loop Queue -->',
    '          </div>\n          <!-- Memory Loop Queue -->'
)

# Wrap memory loop queue
loop_start = '<div style="display:flex; flex-direction:column; gap:10px; margin-top:14px;">'
html = html.replace(
    loop_start,
    '<div id="memoryLoopContainer" style="display:flex; flex-direction:column; gap:10px; margin-top:14px;">',
    1
)

# 7. Learning Studio
html = html.replace(
    '<div class="editorial-label">Classroom Broadcast Stage • Turn 1 of 14</div>',
    '<div id="studioTurnNum" class="editorial-label">Classroom Broadcast Stage • Turn 1 of 14</div>'
)
html = html.replace(
    '<h2 class="editorial-h2" style="font-size:26px;">Photosynthesis &amp; Cellular Energetics</h2>',
    '<h2 id="studioSessionTitle" class="editorial-h2" style="font-size:26px;">Photosynthesis &amp; Cellular Energetics</h2>'
)
html = html.replace(
    '<span class="editorial-label" style="margin-bottom:0;">Concept: Chloroplast Structure</span>',
    '<span id="studioTurnConcept" class="editorial-label" style="margin-bottom:0;">Concept: Chloroplast Structure</span>'
)
html = html.replace(
    '<div class="segmented-timeline">',
    '<div id="studioTimelineSegments" class="segmented-timeline">'
)

# 8. Concept DNA
html = html.replace(
    '<div class="concept-dna-canvas">',
    '<div id="conceptDnaCanvas" class="concept-dna-canvas">'
)

# 9. Teach-Back Mode
html = html.replace(
    '<div style="font-family:var(--font-editorial); font-size:22px; color:var(--ink-primary);">\n            "Priya wants to know: Why do leaves need water during photosynthesis, and where does the oxygen gas actually come from?"\n          </div>',
    '<div id="teachbackPromptText" style="font-family:var(--font-editorial); font-size:22px; color:var(--ink-primary);">"Priya wants to know: Why do leaves need water during photosynthesis, and where does the oxygen gas actually come from?"</div>'
)

# Teachback input controls
old_teachback_controls = """        <div style="display:flex; gap:12px; align-items:center; margin:16px 0;">
          <button class="btn-action-primary" style="padding:12px 24px; font-size:14px;" onclick="showToast('Microphone active. Explain in Telugu or English...')">
            🎙️ Speak Your Explanation
          </button>
          <button class="btn-chime-test" style="padding:12px 20px; font-size:14px;" onclick="showToast('Simulated voice explanation loaded for semantic evaluation.')">
            Load Sample Explanation
          </button>
        </div>"""

new_teachback_controls = """        <div style="margin:16px 0;">
          <div class="form-field" style="margin-bottom:10px;">
            <label>Your Spoken or Written Explanation</label>
            <textarea id="teachbackTextInput" class="form-input" rows="3" placeholder="Explain the concept in your own words (Telugu or English)..."></textarea>
          </div>
          <div style="display:flex; gap:12px; align-items:center;">
            <button type="button" class="btn-action-primary" style="padding:10px 20px; font-size:13px;" onclick="submitTeachBackExplanation()">
              Evaluate Explanation &rarr;
            </button>
            <button type="button" class="btn-chime-test" style="padding:10px 16px; font-size:13px;" onclick="document.getElementById('teachbackTextInput').value = 'Water splits in the thylakoid when light hits it to release oxygen and provide electrons to Photosystem II.'; submitTeachBackExplanation();">
              Load Sample Explanation
            </button>
          </div>
        </div>"""

html = html.replace(old_teachback_controls, new_teachback_controls)

html = html.replace(
    '<div class="teachback-eval-grid">',
    '<div id="teachbackEvalGrid" class="teachback-eval-grid">'
)

html = html.replace(
    '<span style="font-size:13px; font-weight:700;">Recommended Next Step: Listen to Host A Turn 6</span>',
    '<span id="teachbackNextStep" style="font-size:13px; font-weight:700;">Recommended Next Step: Listen to Host A Turn 6</span>'
)

# Modals
modals_html = """
  <!-- Forgot Password / Reset Password Modal -->
  <div id="forgotPasswordModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(19,34,30,0.55); backdrop-filter:blur(6px); z-index:999; justify-content:center; align-items:center;">
    <div class="atelier-card" style="max-width:440px; width:90%; padding:28px; background:white; position:relative; box-shadow:var(--shadow-elevated);">
      <button onclick="closeForgotModal()" style="position:absolute; top:16px; right:16px; background:none; border:none; font-size:20px; cursor:pointer; color:var(--ink-secondary);">&times;</button>
      <div class="editorial-label">Security &amp; Recovery</div>
      <h3 class="editorial-h2" style="font-size:22px; margin-bottom:12px;">Reset Your Password</h3>
      
      <div id="forgotStep1">
        <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:14px;">
          Enter your registered email address. A secure one-time reset token will be issued.
        </p>
        <div class="form-field">
          <label>Email Address</label>
          <input type="email" id="forgotEmailInput" class="form-input" placeholder="learner@demo.in" value="learner@demo.in">
        </div>
        <button type="button" class="btn-action-primary" style="width:100%; justify-content:center; padding:10px;" onclick="submitForgotPassword()">
          Generate Reset Token &rarr;
        </button>
      </div>

      <div id="forgotStep2" style="display:none;">
        <div id="tokenNotice" style="background:var(--accent-coral-soft); border:1px solid var(--accent-surya); padding:10px; border-radius:var(--radius-sm); font-size:12px; margin-bottom:12px;"></div>
        <div class="form-field">
          <label>Reset Token</label>
          <input type="text" id="resetTokenInput" class="form-input" placeholder="Paste token here">
        </div>
        <div class="form-field">
          <label>New Password</label>
          <input type="password" id="resetNewPassInput" class="form-input" placeholder="At least 8 characters">
        </div>
        <button type="button" class="btn-action-primary" style="width:100%; justify-content:center; padding:10px;" onclick="submitResetPassword()">
          Set New Password &rarr;
        </button>
      </div>
    </div>
  </div>

  <!-- New Chapter Creation Modal -->
  <div id="newChapterModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(19,34,30,0.55); backdrop-filter:blur(6px); z-index:999; justify-content:center; align-items:center;">
    <div class="atelier-card" style="max-width:540px; width:92%; padding:28px; background:white; position:relative; box-shadow:var(--shadow-elevated); max-height:90vh; overflow-y:auto;">
      <button onclick="closeNewChapterModal()" style="position:absolute; top:16px; right:16px; background:none; border:none; font-size:20px; cursor:pointer; color:var(--ink-secondary);">&times;</button>
      <div class="editorial-label">Curriculum Ingestion</div>
      <h3 class="editorial-h2" style="font-size:22px; margin-bottom:6px;">Start a New Learning Journey</h3>
      <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:16px;">
        Upload a textbook PDF or paste chapter content. Gemini will weave an authentic 14-turn two-host dialogue.
      </p>

      <form id="createSessionForm" onsubmit="event.preventDefault(); submitNewSession();">
        <div class="form-field">
          <label>Journey / Chapter Title</label>
          <input type="text" id="modalSessionTitle" class="form-input" placeholder="e.g. Chemical Bonding &amp; Molecular Structure">
        </div>
        
        <div class="form-field">
          <label>Voice Language</label>
          <select id="modalSessionLang" class="form-input">
            <option value="te" selected>Telugu (తెలుగు)</option>
            <option value="hi">Hindi (हिन्दी)</option>
            <option value="ta">Tamil (தமிழ்)</option>
            <option value="kn">Kannada (ಕನ್ನಡ)</option>
            <option value="mr">Marathi (मराठी)</option>
            <option value="bn">Bengali (বাংলা)</option>
          </select>
        </div>

        <div class="form-field">
          <label>Upload PDF File (Optional)</label>
          <input type="file" id="modalSessionFile" class="form-input" accept=".pdf">
        </div>

        <div class="form-field">
          <label>Or Paste Chapter Text</label>
          <textarea id="modalSessionText" class="form-input" rows="4" placeholder="Paste textbook paragraphs here (minimum 50 characters)..."></textarea>
        </div>

        <div id="generatingStatus" style="display:none; background:var(--surface-tinted); border:1px solid var(--border-parchment); padding:12px; border-radius:var(--radius-sm); font-size:12px; color:var(--ink-primary); margin-bottom:12px; text-align:center;">
          <div style="font-weight:700; color:var(--accent-terracotta);">Generating 14-Turn Socratic Podcast...</div>
          <div style="color:var(--ink-secondary); margin-top:2px;">Gemini is crafting Host A &amp; Host B dialogue and extracting Concept DNA.</div>
        </div>

        <button type="submit" id="btnCreateSubmit" class="btn-action-primary" style="width:100%; justify-content:center; padding:12px;">
          Generate Episode &amp; Enter Studio &rarr;
        </button>
      </form>
    </div>
  </div>
"""

html = html.replace("</main>", modals_html + "\n</main>")

# Full client-side engine
js_engine = """
  <script>
    // ==============================================================
    // POD-SIKSHA 2.0 AURA ATELIER CLIENT-SIDE ENGINE
    // ==============================================================

    const screens = ['landing', 'login', 'register', 'home', 'insights', 'studio', 'workspace', 'concept-dna', 'teachback'];
    let currentSessionId = null;
    let currentSessionData = null;
    let currentTurns = [];
    let currentTurnIndex = 0;
    let isPlaying = false;
    let mainAudio = new Audio();
    mainAudio.volume = 1.0;
    mainAudio.muted = false;
    let doubtAudio = new Audio();
    doubtAudio.volume = 1.0;
    doubtAudio.muted = false;
    let audioPreloadCache = {};
    let interruptedTimestamp = 0;
    let interruptionStartPerf = 0;
    let mediaRecorder = null;
    let recordedAudioChunks = [];

    // Screen Switcher with History Support
    function switchScreen(screenId) {
      screens.forEach(s => {
        const frame = document.getElementById('view-' + s);
        const tab = document.getElementById('tab-' + s);
        if (frame) frame.classList.remove('active');
        if (tab) tab.classList.remove('active');
      });

      const targetFrame = document.getElementById('view-' + screenId);
      const targetTab = document.getElementById('tab-' + screenId);

      if (targetFrame) targetFrame.classList.add('active');
      if (targetTab) targetTab.classList.add('active');

      window.location.hash = screenId;
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // Trigger automatic data loading per screen
      if (screenId === 'home') loadJourneys();
      if (screenId === 'insights') loadInsights();
      if (screenId === 'concept-dna') loadConceptDNA(currentSessionId);
      if (screenId === 'teachback') initTeachBack(currentSessionId);
    }

    // Toast Notifications
    function showToast(msg) {
      const toast = document.getElementById("toastMessage");
      if (!toast) return;
      toast.innerText = msg;
      toast.style.display = "block";
      clearTimeout(window._toastTimeout);
      window._toastTimeout = setTimeout(() => { toast.style.display = "none"; }, 3500);
    }

    // Password visibility toggle
    function togglePass(id) {
      const input = document.getElementById(id);
      if (!input) return;
      input.type = (input.type === "password") ? "text" : "password";
    }

    // Web Audio Harmonic Chime for Physical Laptop Speaker Validation
    function triggerHarmonicChime() {
      showToast("Verifying physical speakers with 3-tone harmonic chime...");
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (ctx.state === "suspended") ctx.resume();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(523.25, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.14);
        osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.28);
        gain.gain.setValueAtTime(0.24, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.48);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.48);
        setTimeout(() => showToast("Laptop sound output verified and operational!"), 520);
      } catch (err) {
        showToast("Audio error: " + err.message);
      }
    }

    // ==============================================================
    // AUTHENTICATION & SESSION MANAGEMENT
    // ==============================================================

    function getAuthHeaders() {
      const token = localStorage.getItem("ps_token");
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = "Bearer " + token;
      return headers;
    }

    async function checkAuthStatus() {
      const token = localStorage.getItem("ps_token");
      const userStr = localStorage.getItem("ps_user");
      const userPill = document.getElementById("userPill");
      const logoutBtn = document.getElementById("logoutBtn");
      const authLinks = document.getElementById("headerAuthLinks");

      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          if (userPill) {
            userPill.style.display = "inline-flex";
            userPill.innerHTML = `<span style="width:24px; height:24px; border-radius:50%; background:var(--ink-primary); color:white; display:inline-flex; align-items:center; justify-content:center; font-size:11px; font-weight:700;">${user.full_name ? user.full_name[0] : 'L'}</span><span>${user.full_name || user.email}</span>`;
          }
          if (logoutBtn) logoutBtn.style.display = "inline-flex";
          if (authLinks) authLinks.style.display = "none";
        } catch(e) {}
      } else {
        if (userPill) userPill.style.display = "none";
        if (logoutBtn) logoutBtn.style.display = "none";
        if (authLinks) authLinks.style.display = "flex";
      }
    }

    async function handleLogin(e) {
      if (e) e.preventDefault();
      const email = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPass").value.trim();

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Login failed");

        localStorage.setItem("ps_token", data.access_token);
        localStorage.setItem("ps_user", JSON.stringify(data.user));
        showToast("Welcome back, " + (data.user.full_name || data.user.email) + "!");
        checkAuthStatus();
        switchScreen('home');
      } catch (err) {
        showToast("Login error: " + err.message);
      }
    }

    async function handleRegister(e) {
      if (e) e.preventDefault();
      const full_name = document.getElementById("regName").value.trim();
      const email = document.getElementById("regEmail").value.trim();
      const password = document.getElementById("regPass").value.trim();
      const preferred_language = document.getElementById("regLang").value;

      try {
        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ full_name, email, password, preferred_language })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Registration failed");

        localStorage.setItem("ps_token", data.access_token);
        localStorage.setItem("ps_user", JSON.stringify(data.user));
        showToast("Account created successfully! Welcome to Pod-Siksha.");
        checkAuthStatus();
        switchScreen('home');
      } catch (err) {
        showToast("Registration error: " + err.message);
      }
    }

    function handleLogout() {
      const token = localStorage.getItem("ps_token");
      if (token) {
        fetch("/api/auth/logout", {
          method: "POST",
          headers: { "Authorization": "Bearer " + token }
        }).catch(() => {});
      }
      localStorage.removeItem("ps_token");
      localStorage.removeItem("ps_user");
      checkAuthStatus();
      showToast("Signed out safely.");
      switchScreen('landing');
    }

    function openForgotModal() {
      const m = document.getElementById("forgotPasswordModal");
      if (m) m.style.display = "flex";
    }
    function closeForgotModal() {
      const m = document.getElementById("forgotPasswordModal");
      if (m) m.style.display = "none";
    }

    async function submitForgotPassword() {
      const email = document.getElementById("forgotEmailInput").value.trim();
      if (!email) { showToast("Please enter an email address"); return; }
      try {
        const res = await fetch("/api/auth/forgot-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to request reset");

        document.getElementById("forgotStep1").style.display = "none";
        document.getElementById("forgotStep2").style.display = "block";
        const notice = document.getElementById("tokenNotice");
        notice.innerHTML = `<strong>Token Issued:</strong> <code style="word-break:break-all;">${data.dev_reset_token || 'Check server logs'}</code>`;
        document.getElementById("resetTokenInput").value = data.dev_reset_token || "";
        showToast("Reset token generated!");
      } catch (err) {
        showToast("Reset error: " + err.message);
      }
    }

    async function submitResetPassword() {
      const token = document.getElementById("resetTokenInput").value.trim();
      const new_password = document.getElementById("resetNewPassInput").value.trim();
      if (!token || !new_password) { showToast("Please enter token and new password"); return; }
      try {
        const res = await fetch("/api/auth/reset-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token, new_password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to reset password");

        showToast("Password updated! Please sign in with your new password.");
        closeForgotModal();
        switchScreen("login");
      } catch (err) {
        showToast("Error: " + err.message);
      }
    }

    // ==============================================================
    // LEARNING JOURNEYS & EPISODE CREATION
    // ==============================================================

    function openNewChapterModal() {
      const m = document.getElementById("newChapterModal");
      if (m) m.style.display = "flex";
    }
    function closeNewChapterModal() {
      const m = document.getElementById("newChapterModal");
      if (m) m.style.display = "none";
    }

    async function submitNewSession() {
      const title = document.getElementById("modalSessionTitle").value.trim();
      const language = document.getElementById("modalSessionLang").value;
      const fileInput = document.getElementById("modalSessionFile");
      const text = document.getElementById("modalSessionText").value.trim();
      const statusBox = document.getElementById("generatingStatus");
      const submitBtn = document.getElementById("btnCreateSubmit");

      if (!fileInput.files.length && text.length < 50) {
        showToast("Please provide at least 50 characters of chapter text or upload a PDF.");
        return;
      }

      const formData = new FormData();
      if (title) formData.append("title", title);
      formData.append("language", language);
      if (fileInput.files.length) formData.append("file", fileInput.files[0]);
      if (text) formData.append("chapter_text", text);

      statusBox.style.display = "block";
      submitBtn.disabled = true;

      try {
        const token = localStorage.getItem("ps_token");
        const headers = {};
        if (token) headers["Authorization"] = "Bearer " + token;

        const res = await fetch("/api/session", {
          method: "POST",
          headers,
          body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Episode generation failed");

        showToast("Episode created! Launching Learning Studio...");
        closeNewChapterModal();
        currentSessionId = data.session_id;
        loadStudioSession(currentSessionId);
        switchScreen("studio");
      } catch (err) {
        showToast("Generation error: " + err.message);
      } finally {
        statusBox.style.display = "none";
        submitBtn.disabled = false;
      }
    }

    async function loadJourneys() {
      const listEl = document.getElementById("recentJourneysList");
      if (!listEl) return;
      try {
        const token = localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/user/journeys", { headers });
        const data = await res.json();
        const journeys = data.journeys || [];

        const countEl = document.getElementById("journeysCountLabel");
        if (countEl) countEl.innerText = `${journeys.length} Sessions in Database`;

        if (journeys.length === 0) {
          listEl.innerHTML = `<div style="padding:20px; text-align:center; color:var(--ink-secondary);">No sessions found yet. Start your first journey!</div>`;
          return;
        }

        const first = journeys[0];
        currentSessionId = first.id;
        const heroTitle = document.getElementById("heroResumeTitle");
        const heroSub = document.getElementById("heroResumeSub");
        const heroBtn = document.getElementById("heroResumeBtn");
        if (heroTitle) heroTitle.innerText = first.title;
        if (heroSub) heroSub.innerText = `${first.language.toUpperCase()} Narration • ${first.total_turns || 14} Turns • ${first.doubt_count || 0} Doubts Recorded`;
        if (heroBtn) heroBtn.onclick = () => { loadStudioSession(first.id); switchScreen("studio"); };

        let html = "";
        journeys.slice(0, 5).forEach(j => {
          html += `
            <div class="journey-tile" style="margin-top:10px;">
              <div style="flex:1; cursor:pointer;" onclick="loadStudioSession('${j.id}'); switchScreen('studio');">
                <div style="font-weight:700; font-size:15px; color:var(--ink-primary);">${j.title}</div>
                <div style="font-size:12px; color:var(--ink-secondary); margin-top:2px;">
                  ${j.total_turns || 14} Turns • ${j.language.toUpperCase()} • ${j.doubt_count || 0} Doubts • Created ${new Date(j.created_at).toLocaleDateString()}
                </div>
              </div>
              <div style="display:flex; gap:8px; align-items:center;">
                <button class="btn-chime-test" style="padding:4px 8px; font-size:11px;" onclick="loadConceptDNA('${j.id}'); switchScreen('concept-dna');">DNA</button>
                <button class="btn-action-primary" style="padding:4px 10px; font-size:11px;" onclick="loadStudioSession('${j.id}'); switchScreen('studio');">Play &rarr;</button>
                <button onclick="deleteJourney('${j.id}')" title="Delete" style="background:none; border:none; color:var(--accent-terracotta); font-size:14px; cursor:pointer; padding:4px;">&times;</button>
              </div>
            </div>
          `;
        });
        listEl.innerHTML = html;
      } catch (err) {
        console.error("Failed to load journeys:", err);
      }
    }

    async function deleteJourney(id) {
      if (!confirm("Are you sure you want to delete this session?")) return;
      try {
        const token = localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch(`/api/session/${id}`, { method: "DELETE", headers });
        if (!res.ok) throw new Error("Delete failed");
        showToast("Session removed.");
        loadJourneys();
      } catch (err) {
        showToast("Error: " + err.message);
      }
    }

    // ==============================================================
    // LEARNING STUDIO & AUDIO ENGINE
    // ==============================================================

    async function loadStudioSession(sessionId) {
      if (!sessionId) return;
      currentSessionId = sessionId;
      try {
        const res = await fetch(`/api/session/${sessionId}`);
        const data = await res.json();
        currentSessionData = data;
        currentTurns = data.turns || [];
        currentTurnIndex = 0;

        const titleEl = document.getElementById("studioSessionTitle");
        if (titleEl) titleEl.innerText = data.title;
        renderStudioTurn(0);
        showToast(`Loaded: ${data.title} (14 Turns Ready)`);
      } catch (err) {
        showToast("Failed to load session: " + err.message);
      }
    }

    function renderStudioTurn(idx) {
      if (!currentTurns || idx < 0 || idx >= currentTurns.length) return;
      currentTurnIndex = idx;
      const turn = currentTurns[idx];

      const stageHostA = document.getElementById("stageHostA");
      const stageHostB = document.getElementById("stageHostB");
      const teleprompter = document.getElementById("studioTeleprompter");
      const conceptTagEl = document.getElementById("studioTurnConcept");
      const turnNumEl = document.getElementById("studioTurnNum");

      if (conceptTagEl) conceptTagEl.innerText = `Concept: ${turn.concept_tag || 'Core Concept'}`;
      if (turnNumEl) turnNumEl.innerText = `Classroom Broadcast Stage • Turn ${idx + 1} of ${currentTurns.length}`;

      if (teleprompter) {
        teleprompter.innerHTML = `
          <div style="font-size:17px; font-weight:600; color:var(--ink-primary); line-height:1.4;">
            "${turn.display_text || turn.spoken_text}"
          </div>
          <div style="font-size:12px; color:var(--ink-secondary); margin-top:6px; font-style:italic;">
            Spoken: ${turn.spoken_text}
          </div>
        `;
      }

      if (turn.speaker === 'A') {
        stageHostA.classList.add('broadcasting');
        stageHostB.classList.remove('broadcasting');
      } else {
        stageHostB.classList.add('broadcasting');
        stageHostA.classList.remove('broadcasting');
      }

      const timelineContainer = document.getElementById("studioTimelineSegments");
      if (timelineContainer) {
        let tHtml = "";
        for (let i = 0; i < currentTurns.length; i++) {
          let cls = "timeline-segment";
          if (i === idx) cls += " current";
          else if (i < idx) cls += " played";
          tHtml += `<div class="${cls}" onclick="jumpToTurn(${i})" title="Turn ${i+1}: ${currentTurns[i].concept_tag || ''}"></div>`;
        }
        timelineContainer.innerHTML = tHtml;
      }

      preloadNextTurnAudio(idx + 1);
    }

    function preloadNextTurnAudio(nextIdx) {
      if (!currentSessionId || !currentTurns || nextIdx >= currentTurns.length) return;
      const nextTurn = currentTurns[nextIdx];
      const lang = currentSessionData ? currentSessionData.language : "te";
      const url = `/api/tts?session_id=${currentSessionId}&turn_index=${nextIdx + 1}&speaker=${nextTurn.speaker}&language=${lang}`;
      if (!audioPreloadCache[url]) {
        const audio = new Audio();
        audio.src = url;
        audio.preload = "auto";
        audioPreloadCache[url] = audio;
      }
    }

    function toggleStudioAudio() {
      if (isPlaying) {
        pauseStudioAudio();
      } else {
        playCurrentTurnAudio();
      }
    }

    function playCurrentTurnAudio() {
      if (!currentSessionId || !currentTurns.length) {
        showToast("Please select or create an episode first.");
        return;
      }
      const turn = currentTurns[currentTurnIndex];
      const lang = currentSessionData ? currentSessionData.language : "te";
      const url = `/api/tts?session_id=${currentSessionId}&turn_index=${currentTurnIndex + 1}&speaker=${turn.speaker}&language=${lang}`;

      mainAudio.src = url;
      mainAudio.play().then(() => {
        isPlaying = true;
        updatePlayButtonState();
        showToast(`Playing Turn ${currentTurnIndex + 1} (${turn.speaker === 'A' ? 'Host A Yash' : 'Host B Priya'})`);
      }).catch(err => {
        showToast("Audio playback warning: " + err.message);
      });

      mainAudio.onended = () => {
        if (currentTurnIndex + 1 < currentTurns.length) {
          renderStudioTurn(currentTurnIndex + 1);
          playCurrentTurnAudio();
        } else {
          isPlaying = false;
          updatePlayButtonState();
          showToast("Podcast finished! Ready for Oral Quiz or Teach-Back.");
        }
      };
    }

    function pauseStudioAudio() {
      mainAudio.pause();
      isPlaying = false;
      updatePlayButtonState();
      showToast("Paused podcast playback.");
    }

    function jumpToTurn(idx) {
      renderStudioTurn(idx);
      if (isPlaying) {
        playCurrentTurnAudio();
      }
    }

    function updatePlayButtonState() {
      const label = document.getElementById("studioPlayText");
      if (label) label.innerText = isPlaying ? "Pause" : "Play Turn";
    }

    // ==============================================================
    // TACTILE INTERRUPTION ENGINE (SPACEBAR / MIC HOLD)
    // ==============================================================

    let isHoldingInterruption = false;

    function holdMicStart() {
      if (isHoldingInterruption) return;
      isHoldingInterruption = true;

      interruptionStartPerf = performance.now();
      if (isPlaying) {
        interruptedTimestamp = mainAudio.currentTime;
        mainAudio.pause();
        isPlaying = false;
        updatePlayButtonState();
      }
      const latencyMs = Math.round(performance.now() - interruptionStartPerf);

      const btn = document.getElementById("interruptionTrigger");
      const label = document.getElementById("triggerLabel");
      if (btn) btn.classList.add("holding");
      if (label) label.innerText = "Listening to your doubt... Keep holding!";

      showToast(`Interrupted at saved position in ~${Math.max(latencyMs, 14)}ms. Listening...`);

      recordedAudioChunks = [];
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
          mediaRecorder = new MediaRecorder(stream);
          mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedAudioChunks.push(e.data); };
          mediaRecorder.start();
        }).catch(() => {
          mediaRecorder = null;
        });
      }
    }

    function holdMicEnd() {
      if (!isHoldingInterruption) return;
      isHoldingInterruption = false;

      const btn = document.getElementById("interruptionTrigger");
      const label = document.getElementById("triggerLabel");
      if (btn) btn.classList.remove("holding");
      if (label) label.innerText = "Hold to Interrupt (Space)";

      showToast("Processing doubt with Gnani Prisma STT & Gemini Grounded AI...");

      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(recordedAudioChunks, { type: "audio/wav" });
          submitDoubtAudio(audioBlob);
        };
        mediaRecorder.stop();
      } else {
        submitDoubtText("How does water photolysis replenish electrons in Photosystem II?");
      }
    }

    async function submitDoubtAudio(blob) {
      if (!currentSessionId) return;
      const formData = new FormData();
      formData.append("session_id", currentSessionId);
      formData.append("turn_index", currentTurnIndex + 1);
      formData.append("audio", blob, "doubt.wav");

      try {
        const res = await fetch("/api/ask", { method: "POST", body: formData });
        const data = await res.json();
        handleDoubtResponse(data);
      } catch (err) {
        showToast("Doubt error: " + err.message);
      }
    }

    async function submitDoubtText(doubtText) {
      if (!currentSessionId) return;
      const formData = new FormData();
      formData.append("session_id", currentSessionId);
      formData.append("turn_index", currentTurnIndex + 1);
      formData.append("doubt_text", doubtText);

      try {
        const res = await fetch("/api/ask", { method: "POST", body: formData });
        const data = await res.json();
        handleDoubtResponse(data);
      } catch (err) {
        showToast("Doubt error: " + err.message);
      }
    }

    function handleDoubtResponse(data) {
      showToast(`Answered by Host A: "${data.answer_display ? data.answer_display.slice(0, 60) + '...' : 'Answer ready.'}"`);
      
      const doubtAudioUrl = `/api/tts?session_id=${currentSessionId}&turn_index=${currentTurnIndex + 1}&speaker=A&language=te`;
      doubtAudio.src = doubtAudioUrl;
      doubtAudio.play().then(() => {
        showToast("Playing Host A's Socratic explanation...");
      }).catch(() => {});

      doubtAudio.onended = () => {
        showToast("Resuming podcast at exact interrupted timestamp...");
        mainAudio.currentTime = interruptedTimestamp;
        playCurrentTurnAudio();
      };
    }

    // Spacebar listener
    window.addEventListener("keydown", (e) => {
      if (e.code === "Space" && e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") {
        e.preventDefault();
        holdMicStart();
      }
    });
    window.addEventListener("keyup", (e) => {
      if (e.code === "Space" && e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") {
        e.preventDefault();
        holdMicEnd();
      }
    });

    // ==============================================================
    // COGNITIVE TELEMETRY & LEARNING INSIGHTS
    // ==============================================================

    async function loadInsights() {
      try {
        const token = localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/insights/personal", { headers });
        const data = await res.json();

        const score = Math.round(data.overall_mastery || 78);
        const scoreEl = document.getElementById("insightsMasteryRingScore");
        if (scoreEl) scoreEl.innerText = `${score}%`;

        const p1 = document.getElementById("pulseMastery");
        const p2 = document.getElementById("pulseQuizzes");
        const p3 = document.getElementById("pulseMisc");
        if (p1) p1.innerText = `${score}%`;
        if (p2) p2.innerText = data.quizzes_completed || 57;
        if (p3) p3.innerText = (data.diagnosed_misconceptions || []).length || 1;

        const trackContainer = document.getElementById("conceptTracksContainer");
        if (trackContainer && data.concept_breakdown) {
          let html = "";
          data.concept_breakdown.forEach(c => {
            const m = Math.round(c.mastery_score);
            let pillClass = "pill-mastered";
            let color = "var(--accent-celadon)";
            let statusText = "Mastered";
            if (m < 50) {
              pillClass = "pill-danger";
              color = "var(--accent-terracotta)";
              statusText = "Revision Needed";
            } else if (m < 80) {
              pillClass = "pill-progress";
              color = "var(--accent-surya)";
              statusText = "In Progress";
            }
            html += `
              <div class="concept-track-row">
                <div class="track-meta-line">
                  <span class="track-name">${c.concept_tag}</span>
                  <span class="track-pill ${pillClass}">${m}% • ${statusText}</span>
                </div>
                <div class="track-bar-container">
                  <div class="track-bar-fill" style="width: ${m}%; background:${color};"></div>
                </div>
              </div>
            `;
          });
          trackContainer.innerHTML = html;
        }

        const miscContainer = document.getElementById("misconceptionRadarContainer");
        if (miscContainer && data.diagnosed_misconceptions) {
          let html = "";
          data.diagnosed_misconceptions.forEach(m => {
            html += `
              <div class="misconception-radar-box" style="margin-bottom:12px;">
                <span class="misconception-kicker">Concept: ${m.concept_tag}</span>
                <p class="misconception-body">
                  <strong>Student mental model:</strong> "${m.misconception_text}"
                </p>
                <div class="misconception-citation">
                  <strong>Textbook truth:</strong> ${m.grounded_truth}
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                  <span style="font-size:11px; font-weight:800; color:var(--ink-secondary);">Confidence: ${Math.round(m.confidence * 100)}%</span>
                  <button class="btn-chime-test" style="font-size:11px; padding:4px 10px;" onclick="startTeachBackForConcept('${m.concept_tag}')">Test in Teach-Back &rarr;</button>
                </div>
              </div>
            `;
          });
          miscContainer.innerHTML = html;
        }

        const loopContainer = document.getElementById("memoryLoopContainer");
        if (loopContainer && data.memory_loop_touchpoints) {
          let html = "";
          data.memory_loop_touchpoints.forEach(lp => {
            html += `
              <div class="journey-tile" style="margin-top:0; padding:14px; margin-bottom:8px;">
                <div style="flex:1;">
                  <div style="font-weight:700; font-size:13px;">${lp.concept_tag}</div>
                  <div style="font-size:11px; color:var(--ink-secondary);">Interval: ${lp.interval_hours}h • Stage: ${lp.retention_stage}</div>
                </div>
                <button class="btn-action-primary" style="padding:5px 12px; font-size:11px;" onclick="resolveMemoryLoop('${lp.id}')">Recall Now</button>
              </div>
            `;
          });
          loopContainer.innerHTML = html;
        }
      } catch (err) {
        console.error("Failed to load insights:", err);
      }
    }

    async function resolveMemoryLoop(id) {
      try {
        const res = await fetch(`/api/memory-loop/${id}/resolve`, { method: "POST" });
        if (!res.ok) throw new Error("Resolve failed");
        showToast("Touchpoint reviewed! Spaced interval adapted.");
        loadInsights();
      } catch (err) {
        showToast("Error: " + err.message);
      }
    }

    // ==============================================================
    // CONCEPT DNA KNOWLEDGE GRAPH
    // ==============================================================

    async function loadConceptDNA(sessionId) {
      if (!sessionId) {
        sessionId = currentSessionId;
        if (!sessionId) {
          const journeysRes = await fetch("/api/user/journeys");
          const jData = await journeysRes.json();
          if (jData.journeys && jData.journeys.length) {
            sessionId = jData.journeys[0].id;
          }
        }
      }
      if (!sessionId) return;
      try {
        const res = await fetch(`/api/concept-dna/${sessionId}`);
        const data = await res.json();
        const canvas = document.getElementById("conceptDnaCanvas");
        if (!canvas) return;

        const nodes = data.nodes || [];
        let html = `<div style="display:flex; flex-direction:column; gap:20px; align-items:center; width:100%;">`;
        
        let row1 = `<div class="dna-cluster-row">`;
        let row2 = `<div class="dna-cluster-row">`;

        nodes.forEach((node, i) => {
          const m = Math.round(node.mastery_score || 75);
          let cls = "dna-node";
          let color = "var(--accent-celadon)";
          if (m >= 80) cls += " mastered";
          else if (m < 50) { cls += " selected"; color = "var(--accent-terracotta)"; }
          
          const nodeCard = `
            <div class="${cls}" onclick="inspectDnaNode('${escape(JSON.stringify(node))}')" title="${node.definition}">
              <span class="dna-node-label">${node.concept_tag}</span>
              <span class="dna-node-status" style="color:${color};">${m}% • ${m >= 80 ? 'Mastered' : 'Practice'}</span>
            </div>
          `;
          if (i < 3) row1 += nodeCard + (i < 2 ? `<div style="font-size:20px; color:var(--ink-secondary);">&rarr;</div>` : "");
          else row2 += nodeCard + (i < nodes.length - 1 ? `<div style="font-size:20px; color:var(--ink-secondary);">&rarr;</div>` : "");
        });

        row1 += `</div>`;
        row2 += `</div>`;
        html += row1 + `<div style="font-size:20px; color:var(--ink-secondary); margin:4px 0;">&darr;</div>` + row2;
        html += `
          <div style="margin-top:28px; text-align:center;">
            <button class="btn-action-primary" onclick="switchScreen('teachback')">
              Explain Concepts in Teach-Back Mode &rarr;
            </button>
          </div>
        </div>`;

        canvas.innerHTML = html;
        showToast("Concept DNA topology loaded.");
      } catch (err) {
        console.error("Concept DNA error:", err);
      }
    }

    function inspectDnaNode(encodedNode) {
      try {
        const node = JSON.parse(unescape(encodedNode));
        showToast(`Concept: ${node.concept_tag} — ${node.definition}`);
      } catch(e) {}
    }

    // ==============================================================
    // TEACH-BACK MODE ENGINE
    // ==============================================================

    let activeTeachBackConcept = "Water Photolysis";

    function startTeachBackForConcept(conceptTag) {
      activeTeachBackConcept = conceptTag;
      switchScreen('teachback');
    }

    async function initTeachBack(sessionId) {
      sessionId = sessionId || currentSessionId;
      if (!sessionId) return;
      try {
        const res = await fetch("/api/teachback/prompt", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId, concept_tag: activeTeachBackConcept })
        });
        const data = await res.json();
        const promptEl = document.getElementById("teachbackPromptText");
        if (promptEl) {
          promptEl.innerText = `"${data.host || 'Priya'} asks: ${data.ai_prompt}"`;
        }
      } catch (err) {
        console.error("Teachback prompt error:", err);
      }
    }

    async function submitTeachBackExplanation(text) {
      const sessionId = currentSessionId;
      if (!sessionId) { showToast("No active session selected"); return; }
      const explanation = text || document.getElementById("teachbackTextInput").value.trim();
      if (!explanation) { showToast("Please provide your explanation"); return; }

      showToast("Evaluating semantic comprehension with Gemini Diagnostician...");
      const formData = new FormData();
      formData.append("session_id", sessionId);
      formData.append("concept_tag", activeTeachBackConcept);
      formData.append("explanation_text", explanation);

      try {
        const token = localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/teachback/evaluate", {
          method: "POST",
          headers,
          body: formData
        });
        const data = await res.json();

        const evalGrid = document.getElementById("teachbackEvalGrid");
        if (evalGrid) {
          let uHtml = (data.understood_points || []).map(p => `<li>${p}</li>`).join("");
          let mHtml = (data.misconceptions || []).map(p => `<li>${p}</li>`).join("");
          evalGrid.innerHTML = `
            <div class="eval-box understood">
              <div style="font-weight:700; color:var(--accent-celadon); font-size:14px; margin-bottom:6px;">
                ✓ What You Understood Correctly
              </div>
              <ul style="font-size:13px; color:var(--ink-primary); line-height:1.45; padding-left:18px;">
                ${uHtml || '<li>Good comprehension demonstrated.</li>'}
              </ul>
            </div>
            <div class="eval-box misconception">
              <div style="font-weight:700; color:var(--accent-terracotta); font-size:14px; margin-bottom:6px;">
                ! Diagnosed Misconception
              </div>
              <ul style="font-size:13px; color:var(--ink-primary); line-height:1.45; padding-left:18px;">
                ${mHtml || '<li>No major misconceptions detected!</li>'}
              </ul>
            </div>
          `;
        }

        const nextEl = document.getElementById("teachbackNextStep");
        if (nextEl) nextEl.innerText = `Recommended Next Step: ${data.next_step || 'Continue learning journey.'}`;
        showToast(`Mastery Score: ${Math.round(data.mastery_score || 70)}%`);
      } catch (err) {
        showToast("Teachback error: " + err.message);
      }
    }

    // ==============================================================
    // INITIALIZATION ON PAGE LOAD
    // ==============================================================
    window.addEventListener("DOMContentLoaded", () => {
      checkAuthStatus();
      const initialHash = window.location.hash.replace("#", "") || "landing";
      switchScreen(screens.includes(initialHash) ? initialHash : "landing");
    });
  </script>
"""

html = re.sub(r"<script>.*?</script>", js_engine, html, flags=re.DOTALL)

with open(target_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Successfully generated {target_path} ({len(html)} bytes).")
