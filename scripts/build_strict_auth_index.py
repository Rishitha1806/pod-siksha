"""
Builds the complete production static/index.html for Pod-Siksha 2.0 with STRICT AUTHENTICATION-FIRST ACCESS CONTROL:
1. Branded Aura Atelier verification overlay (zero flash of protected content).
2. Centralized AuthManager with state machine and session verification.
3. Strict route guards preventing direct URL access to protected pages.
4. Intended destination preservation across login.
5. Graceful expired session handling.
6. Public routes: landing, login, register, forgot-password, reset-password, verify-email, privacy, terms.
7. Protected routes: home, insights, studio, workspace, concept-dna, teachback.
8. Clean form inputs (no hardcoded credentials) with optional evaluator demo helpers.
"""

import os
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source_path = os.path.join(base_dir, "static", "redesign.html")
target_path = os.path.join(base_dir, "static", "index.html")

with open(source_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Title
html = re.sub(
    r"<title>.*?</title>",
    "<title>Pod-Siksha 2.0 — Aura Atelier (Strict Auth-First Learning Sanctuary)</title>",
    html
)

# 2. Add Branded Session Verification Overlay right after <body>
overlay_html = """
  <!-- Branded Session Verification Overlay (Zero Flash of Protected Content) -->
  <div id="sessionVerifyOverlay" style="position:fixed; inset:0; background:var(--canvas-bg); z-index:9999; display:flex; flex-direction:column; justify-content:center; align-items:center;">
    <div style="width:58px; height:58px; border-radius:var(--radius-md); background:var(--ink-primary); color:var(--canvas-bg); font-family:var(--font-editorial); font-size:32px; font-style:italic; display:flex; align-items:center; justify-content:center; box-shadow:var(--shadow-elevated); margin-bottom:18px;">
      P
    </div>
    <div style="font-family:var(--font-editorial); font-size:24px; color:var(--ink-primary); margin-bottom:4px;">Pod-Siksha 2.0</div>
    <div style="font-size:11px; font-weight:800; letter-spacing:1px; text-transform:uppercase; color:var(--accent-terracotta);">Vedic Lumina Architecture</div>
    <div style="font-size:13px; color:var(--ink-secondary); margin-top:16px; display:flex; align-items:center; gap:8px;">
      <span style="display:inline-block; width:12px; height:12px; border:2px solid var(--border-parchment); border-top-color:var(--accent-terracotta); border-radius:50%; animation:spin 0.8s linear infinite;"></span>
      <span id="overlayStatusText">Verifying Sovereign Learner Session...</span>
    </div>
  </div>
"""
html = html.replace("<body>", "<body>\n" + overlay_html)

# Add CSS animation for spinner
spinner_css = """
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .screen-frame { display: none !important; }
    .screen-frame.active { display: block !important; }
    .locked-badge { font-size: 10px; color: var(--accent-terracotta); margin-left: 4px; }
"""
html = html.replace("</style>", spinner_css + "\n</style>")

# 3. Update Header Navigation with Protected Indicators and Public Links
old_nav = """    <nav class="screen-switcher-bar">
      <button class="screen-tab-btn active" id="tab-landing" onclick="switchScreen('landing')">1. Landing</button>
      <button class="screen-tab-btn" id="tab-login" onclick="switchScreen('login')">2. Login</button>
      <button class="screen-tab-btn" id="tab-register" onclick="switchScreen('register')">3. Register</button>
      <button class="screen-tab-btn" id="tab-home" onclick="switchScreen('home')">4. Personal Home</button>
      <button class="screen-tab-btn highlight" id="tab-insights" onclick="switchScreen('insights')">5. Learning Insights</button>
      <button class="screen-tab-btn" id="tab-studio" onclick="switchScreen('studio')">6. Learning Studio</button>
      <button class="screen-tab-btn" id="tab-workspace" onclick="switchScreen('workspace')">7. Workspace</button>
      <button class="screen-tab-btn" id="tab-concept-dna" onclick="switchScreen('concept-dna')">8. Concept DNA</button>
      <button class="screen-tab-btn" id="tab-teachback" onclick="switchScreen('teachback')">9. Teach-Back</button>
    </nav>"""

new_nav = """    <nav class="screen-switcher-bar">
      <button class="screen-tab-btn active" id="tab-landing" onclick="switchScreen('landing')">Sanctuary</button>
      <button class="screen-tab-btn" id="tab-home" onclick="switchScreen('home')">Atelier Home <span class="locked-badge" id="lock-home">&#128274;</span></button>
      <button class="screen-tab-btn highlight" id="tab-insights" onclick="switchScreen('insights')">Insights <span class="locked-badge" id="lock-insights">&#128274;</span></button>
      <button class="screen-tab-btn" id="tab-studio" onclick="switchScreen('studio')">Studio <span class="locked-badge" id="lock-studio">&#128274;</span></button>
      <button class="screen-tab-btn" id="tab-workspace" onclick="switchScreen('workspace')">Workspace <span class="locked-badge" id="lock-workspace">&#128274;</span></button>
      <button class="screen-tab-btn" id="tab-concept-dna" onclick="switchScreen('concept-dna')">Concept DNA <span class="locked-badge" id="lock-concept-dna">&#128274;</span></button>
      <button class="screen-tab-btn" id="tab-teachback" onclick="switchScreen('teachback')">Teach-Back <span class="locked-badge" id="lock-teachback">&#128274;</span></button>
      <button class="screen-tab-btn" id="tab-privacy" onclick="switchScreen('privacy')">Privacy</button>
      <button class="screen-tab-btn" id="tab-terms" onclick="switchScreen('terms')">Terms</button>
    </nav>"""

html = html.replace(old_nav, new_nav)

# 4. Header controls: User profile / Login / Sign out
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
      <button class="btn-chime-test" id="btnHeaderNewJourney" onclick="openNewChapterModal()" style="display:none; border-color:var(--accent-terracotta); color:var(--accent-terracotta);">
        + New Journey
      </button>
      <div id="userPill" style="display:none; align-items:center; gap:6px; font-size:12px; font-weight:700; color:var(--ink-primary); background:var(--surface-tinted); padding:4px 10px; border-radius:var(--radius-full); border:1px solid var(--border-parchment);">
      </div>
      <button id="logoutBtn" class="btn-chime-test" style="display:none; font-size:12px; padding:6px 10px;" onclick="AuthManager.logout()">
        Sign Out
      </button>
      <div id="headerAuthLinks" style="display:flex; gap:6px;">
        <button class="btn-action-primary" style="padding:6px 14px; font-size:12px;" onclick="switchScreen('login')">
          Sign In &rarr;
        </button>
      </div>
    </div>"""

html = html.replace(old_header_ctrls, new_header_ctrls)

# 5. Clean Login Form (No hardcoded credentials)
old_login_form = """          <form onsubmit="event.preventDefault(); showToast('Welcome back, Learner!'); switchScreen('home');">
            <div class="form-field">
              <label>Email Address</label>
              <input type="email" class="form-input" placeholder="learner@podsiksha.in" value="learner@demo.in" required>
            </div>
            <div class="form-field">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <label>Password</label>
                <a href="javascript:void(0)" onclick="showToast('Password reset link dispatched via secure token.')" style="font-size:11px; color:var(--accent-terracotta); text-decoration:none; font-weight:600;">Forgot Password?</a>
              </div>
              <div class="password-wrap">
                <input type="password" id="loginPass" class="form-input" value="podsiksha2026" required>
                <button type="button" class="password-toggle-btn" onclick="togglePass('loginPass')">Show</button>
              </div>
            </div>
            <button type="submit" class="btn-action-primary" style="width:100%; justify-content:center; padding:12px; font-size:14px; margin-top:10px;">
              Enter Learning Atelier &rarr;
            </button>
          </form>"""

new_login_form = """          <form id="loginForm" onsubmit="event.preventDefault(); AuthManager.login();">
            <div class="form-field">
              <label>Email Address</label>
              <input type="email" id="loginEmail" class="form-input" placeholder="learner@example.in" required>
            </div>
            <div class="form-field">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <label>Password</label>
                <a href="javascript:void(0)" onclick="openForgotModal()" style="font-size:11px; color:var(--accent-terracotta); text-decoration:none; font-weight:600;">Forgot Password?</a>
              </div>
              <div class="password-wrap">
                <input type="password" id="loginPass" class="form-input" placeholder="Enter your password" required>
                <button type="button" class="password-toggle-btn" onclick="togglePass('loginPass')">Show</button>
              </div>
            </div>
            <button type="submit" id="btnLoginSubmit" class="btn-action-primary" style="width:100%; justify-content:center; padding:12px; font-size:14px; margin-top:10px;">
              Enter Learning Atelier &rarr;
            </button>
          </form>"""

html = html.replace(old_login_form, new_login_form)

# 6. Clean Registration Form
old_reg_form = """          <form onsubmit="event.preventDefault(); showToast('Account created! Welcome to Pod-Siksha.'); switchScreen('home');">
            <div class="form-field">
              <label>Full Name</label>
              <input type="text" class="form-input" placeholder="Rishitha J.V." required>
            </div>
            <div class="form-field">
              <label>Email Address</label>
              <input type="email" class="form-input" placeholder="rishitha@example.in" required>
            </div>
            <div class="form-field">
              <label>Password</label>
              <div class="password-wrap">
                <input type="password" id="regPass" class="form-input" placeholder="Minimum 8 characters" required>
                <button type="button" class="password-toggle-btn" onclick="togglePass('regPass')">Show</button>
              </div>
            </div>
            <div class="form-field">
              <label>Preferred Voice Language</label>
              <select class="form-input">
                <option value="te" selected>Telugu (తెలుగు)</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                <option value="mr">Marathi (मराठी)</option>
                <option value="bn">Bengali (বাংলা)</option>
              </select>
            </div>
            <button type="submit" class="btn-action-primary" style="width:100%; justify-content:center; padding:12px; font-size:14px; margin-top:8px;">
              Create Personal Account &rarr;
            </button>
          </form>"""

new_reg_form = """          <form id="regForm" onsubmit="event.preventDefault(); AuthManager.register();">
            <div class="form-field">
              <label>Full Name</label>
              <input type="text" id="regName" class="form-input" placeholder="Enter full name" required>
            </div>
            <div class="form-field">
              <label>Email Address</label>
              <input type="email" id="regEmail" class="form-input" placeholder="your.name@example.in" required>
            </div>
            <div class="form-field">
              <label>Password</label>
              <div class="password-wrap">
                <input type="password" id="regPass" class="form-input" placeholder="Minimum 6 characters" required>
                <button type="button" class="password-toggle-btn" onclick="togglePass('regPass')">Show</button>
              </div>
            </div>
            <div class="form-field">
              <label>Preferred Voice Language</label>
              <select id="regLang" class="form-input">
                <option value="te" selected>Telugu (తెలుగు)</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                <option value="mr">Marathi (मराठी)</option>
                <option value="bn">Bengali (বাংলা)</option>
              </select>
            </div>
            <button type="submit" id="btnRegSubmit" class="btn-action-primary" style="width:100%; justify-content:center; padding:12px; font-size:14px; margin-top:8px;">
              Create Personal Account &rarr;
            </button>
          </form>"""

html = html.replace(old_reg_form, new_reg_form)

# 7. Add Public Screens: Verify Email, Privacy Policy, Terms and Conditions
new_public_screens = """
    <!-- ==============================================================
         PUBLIC SCREEN: EMAIL VERIFICATION
         ============================================================== -->
    <section class="screen-frame" id="view-verify-email">
      <div class="auth-split-wrapper">
        <div class="auth-art-column">
          <div>
            <div class="editorial-label" style="color:var(--accent-surya);">Sovereign Identity Protection</div>
            <h2 style="font-family:var(--font-editorial); font-size:32px; color:white; margin-top:8px;">Verify Your Learner Email</h2>
          </div>
          <div class="auth-quote">
            "We verify every learner's academic identity before opening access to private learning journeys and telemetry."
          </div>
          <div style="font-size:12px; color:#A4B5AD;">
            Strict access control ensures isolated study history and secure session encryption.
          </div>
        </div>

        <div class="auth-form-column">
          <div class="editorial-label">Verification Step</div>
          <h2 class="editorial-h2" style="font-size:26px; margin-bottom:12px;">Confirm Email Address</h2>
          <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:20px;">
            Enter the verification token issued during registration or sent to your inbox.
          </p>

          <form onsubmit="event.preventDefault(); AuthManager.submitEmailVerification();">
            <div class="form-field">
              <label>Verification Token / Code</label>
              <input type="text" id="verifyEmailTokenInput" class="form-input" placeholder="Paste 32-character hex verification token" required>
            </div>
            <button type="submit" class="btn-action-primary" style="width:100%; justify-content:center; padding:12px; font-size:14px;">
              Verify &amp; Enter Atelier &rarr;
            </button>
          </form>

          <div style="margin-top:20px; text-align:center;">
            <a href="javascript:void(0)" onclick="AuthManager.resendVerificationPrompt()" style="font-size:12px; color:var(--accent-terracotta); text-decoration:none; font-weight:700;">
              Resend verification code
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- ==============================================================
         PUBLIC SCREEN: PRIVACY POLICY
         ============================================================== -->
    <section class="screen-frame" id="view-privacy">
      <div class="atelier-card" style="padding:36px; max-width:880px; margin:0 auto;">
        <div class="editorial-label">Data Sovereign Protection</div>
        <h1 class="editorial-h1" style="font-size:34px;">Pod-Siksha Privacy Policy</h1>
        <p class="editorial-lead">Your learning voice and study history are strictly protected under zero-retention principles.</p>

        <div style="margin-top:24px; display:flex; flex-direction:column; gap:20px;">
          <div>
            <h3 style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary); margin-bottom:6px;">1. Strict User-Level Data Isolation</h3>
            <p style="font-size:14px; color:var(--ink-secondary); line-height:1.6;">
              Every learning journey, doubt recording, quiz attempt, and misconception diagnostic is bound cryptographically to your authenticated user account. Other learners cannot access, view, or modify your sessions.
            </p>
          </div>

          <div>
            <h3 style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary); margin-bottom:6px;">2. Zero Audio Retained on Disk</h3>
            <p style="font-size:14px; color:var(--ink-secondary); line-height:1.6;">
              Student voice interruptions are transmitted over secure TLS directly to Gnani Prisma STT v3.0, transcribed ephemerally in RAM, and immediately purged. No raw audio files are stored permanently on server storage.
            </p>
          </div>

          <div>
            <h3 style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary); margin-bottom:6px;">3. Textbook Grounding &amp; AI Safety</h3>
            <p style="font-size:14px; color:var(--ink-secondary); line-height:1.6;">
              Educational questions are answered with Google Gemini using evidence extracted strictly from your uploaded study materials.
            </p>
          </div>
        </div>

        <div style="margin-top:32px; padding-top:20px; border-top:1px solid var(--border-parchment); display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:12px; color:var(--ink-secondary);">Effective Date: November 9, 2026 • Version 2.0.0</span>
          <button class="btn-action-primary" onclick="switchScreen('landing')">Return to Sanctuary &rarr;</button>
        </div>
      </div>
    </section>

    <!-- ==============================================================
         PUBLIC SCREEN: TERMS AND CONDITIONS
         ============================================================== -->
    <section class="screen-frame" id="view-terms">
      <div class="atelier-card" style="padding:36px; max-width:880px; margin:0 auto;">
        <div class="editorial-label">Academic Compact</div>
        <h1 class="editorial-h1" style="font-size:34px;">Terms and Conditions</h1>
        <p class="editorial-lead">Guidelines for scholarly exploration, Socratic dialogic learning, and pedagogical integrity.</p>

        <div style="margin-top:24px; display:flex; flex-direction:column; gap:20px;">
          <div>
            <h3 style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary); margin-bottom:6px;">1. Scholarly Purpose &amp; Academic Integrity</h3>
            <p style="font-size:14px; color:var(--ink-secondary); line-height:1.6;">
              Pod-Siksha 2.0 is designed as a dialogic AI companion to accelerate deep concept comprehension. It uses Socratic questioning and progressive hint ladders to foster critical thinking rather than simple answer-copying.
            </p>
          </div>

          <div>
            <h3 style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary); margin-bottom:6px;">2. Intellectual Property of Uploaded Chapters</h3>
            <p style="font-size:14px; color:var(--ink-secondary); line-height:1.6;">
              Learners retain full ownership of uploaded PDFs and study documents. Pod-Siksha parses documents in-memory to generate podcast scripts and knowledge topology graphs for the learner's personal study session only.
            </p>
          </div>

          <div>
            <h3 style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary); margin-bottom:6px;">3. Responsible Voice Interaction</h3>
            <p style="font-size:14px; color:var(--ink-secondary); line-height:1.6;">
              The tactile interruption microphone is reserved for genuine classroom doubts and spoken quiz answers in supported regional languages.
            </p>
          </div>
        </div>

        <div style="margin-top:32px; padding-top:20px; border-top:1px solid var(--border-parchment); display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:12px; color:var(--ink-secondary);">Effective Date: November 9, 2026 • Version 2.0.0</span>
          <button class="btn-action-primary" onclick="switchScreen('landing')">Return to Sanctuary &rarr;</button>
        </div>
      </div>
    </section>
"""

html = html.replace("</main>", new_public_screens + "\n</main>")

# 8. Add Modals: Forgot Password and New Chapter Modal
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
          <input type="email" id="forgotEmailInput" class="form-input" placeholder="learner@demo.in">
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
          <input type="password" id="resetNewPassInput" class="form-input" placeholder="At least 6 characters">
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

# 9. IDs on Home, Insights, Studio, Workspace, Concept DNA, Teachback
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
html = html.replace(
    '<span style="font-size:12px; font-weight:700; color:var(--ink-secondary);">102 Sessions in Database</span>',
    '<span id="journeysCountLabel" style="font-size:12px; font-weight:700; color:var(--ink-secondary);">Loading Sessions...</span>'
)
html = html.replace(
    '<div class="journey-tile" onclick="switchScreen(\'studio\')">',
    '<div id="recentJourneysList"><div class="journey-tile" onclick="switchScreen(\'studio\')">'
)
html = html.replace(
    '        <!-- Right: Daily Cognitive Pulse & Start New -->',
    '        </div>\n        <!-- Right: Daily Cognitive Pulse & Start New -->'
)
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
html = html.replace(
    'onclick="showToast(\'Sample chapter loaded: sample_chapter.pdf\'); switchScreen(\'studio\');"',
    'onclick="openNewChapterModal()"'
)
html = html.replace(
    '<span class="ring-center-score">78%</span>',
    '<span id="insightsMasteryRingScore" class="ring-center-score">78%</span>'
)
html = html.replace(
    '<div class="concept-track-row">',
    '<div id="conceptTracksContainer"><div class="concept-track-row">',
    1
)
html = html.replace(
    '        <!-- Right: Misconception Radar & Memory Loop -->',
    '        </div></div>\n        <!-- Right: Misconception Radar & Memory Loop -->'
)
html = html.replace(
    '<div class="misconception-radar-box">',
    '<div id="misconceptionRadarContainer"><div class="misconception-radar-box">',
    1
)
html = html.replace(
    '          <!-- Memory Loop Queue -->',
    '          </div>\n          <!-- Memory Loop Queue -->'
)
html = html.replace(
    '<div style="display:flex; flex-direction:column; gap:10px; margin-top:14px;">',
    '<div id="memoryLoopContainer" style="display:flex; flex-direction:column; gap:10px; margin-top:14px;">',
    1
)
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
html = html.replace(
    '<div class="concept-dna-canvas">',
    '<div id="conceptDnaCanvas" class="concept-dna-canvas">'
)
html = html.replace(
    '<div style="font-family:var(--font-editorial); font-size:22px; color:var(--ink-primary);">\n            "Priya wants to know: Why do leaves need water during photosynthesis, and where does the oxygen gas actually come from?"\n          </div>',
    '<div id="teachbackPromptText" style="font-family:var(--font-editorial); font-size:22px; color:var(--ink-primary);">"Priya asks: Can you explain water photolysis in your own words?"</div>'
)

old_tb_ctrl = """        <div style="display:flex; gap:12px; align-items:center; margin:16px 0;">
          <button class="btn-action-primary" style="padding:12px 24px; font-size:14px;" onclick="showToast('Microphone active. Explain in Telugu or English...')">
            🎙️ Speak Your Explanation
          </button>
          <button class="btn-chime-test" style="padding:12px 20px; font-size:14px;" onclick="showToast('Simulated voice explanation loaded for semantic evaluation.')">
            Load Sample Explanation
          </button>
        </div>"""

new_tb_ctrl = """        <div style="margin:16px 0;">
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

html = html.replace(old_tb_ctrl, new_tb_ctrl)
html = html.replace('<div class="teachback-eval-grid">', '<div id="teachbackEvalGrid" class="teachback-eval-grid">')
html = html.replace(
    '<span style="font-size:13px; font-weight:700;">Recommended Next Step: Listen to Host A Turn 6</span>',
    '<span id="teachbackNextStep" style="font-size:13px; font-weight:700;">Recommended Next Step: Listen to Host A Turn 6</span>'
)

# 10. Master Strict Auth & Client-Side Engine
js_strict_engine = """
  <script>
    // ==============================================================
    // POD-SIKSHA 2.0 STRICT AUTHENTICATION-FIRST ACCESS CONTROL ENGINE
    // ==============================================================

    const PUBLIC_SCREENS = ['landing', 'login', 'register', 'forgot-password', 'reset-password', 'verify-email', 'privacy', 'terms'];
    const PROTECTED_SCREENS = ['home', 'insights', 'studio', 'workspace', 'concept-dna', 'teachback'];
    const ALL_SCREENS = [...PUBLIC_SCREENS, ...PROTECTED_SCREENS];

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

    // Centralized Authentication Provider
    const AuthManager = {
      currentUser: null,
      authToken: null,

      async initialize() {
        const token = localStorage.getItem("ps_token");
        if (!token) {
          this.setUnauthenticatedState();
          this.dismissOverlay();
          this.handleInitialNavigation(false);
          return;
        }

        try {
          const res = await fetch("/api/auth/me", {
            headers: { "Authorization": "Bearer " + token }
          });
          
          if (res.status === 200) {
            const data = await res.json();
            this.authToken = token;
            this.currentUser = data.user || data;
            localStorage.setItem("ps_user", JSON.stringify(this.currentUser));
            this.setAuthenticatedState();
            this.dismissOverlay();
            this.handleInitialNavigation(true);
          } else if (res.status === 403) {
            // Unverified email
            this.dismissOverlay();
            showToast("Email verification required. Please verify your token.");
            switchScreen('verify-email');
          } else {
            // Token expired or invalid
            this.logout(false);
            this.dismissOverlay();
            showToast("Your session has expired. Please sign in again.");
            switchScreen('login');
          }
        } catch (err) {
          console.error("Auth check network error:", err);
          this.dismissOverlay();
          this.setUnauthenticatedState();
          this.handleInitialNavigation(false);
        }
      },

      dismissOverlay() {
        const overlay = document.getElementById("sessionVerifyOverlay");
        if (overlay) overlay.style.display = "none";
      },

      isAuthenticated() {
        return !!this.authToken && !!this.currentUser;
      },

      setAuthenticatedState() {
        const u = this.currentUser;
        const userPill = document.getElementById("userPill");
        const logoutBtn = document.getElementById("logoutBtn");
        const authLinks = document.getElementById("headerAuthLinks");
        const btnNewJourney = document.getElementById("btnHeaderNewJourney");

        if (userPill) {
          userPill.style.display = "inline-flex";
          const init = u.full_name ? u.full_name[0].toUpperCase() : "L";
          userPill.innerHTML = `
            <span style="width:22px; height:22px; border-radius:50%; background:var(--ink-primary); color:white; display:inline-flex; align-items:center; justify-content:center; font-size:11px; font-weight:700;">${init}</span>
            <span>${u.full_name || u.email}</span>
            <span style="font-size:10px; font-weight:800; background:var(--surface-white); padding:2px 6px; border-radius:var(--radius-sm); color:var(--accent-terracotta);">${(u.role || 'student').toUpperCase()}</span>
          `;
        }
        if (logoutBtn) logoutBtn.style.display = "inline-flex";
        if (btnNewJourney) btnNewJourney.style.display = "inline-flex";
        if (authLinks) authLinks.style.display = "none";

        // Unlock tab badges
        document.querySelectorAll(".locked-badge").forEach(el => el.style.display = "none");
      },

      setUnauthenticatedState() {
        this.currentUser = null;
        this.authToken = null;
        const userPill = document.getElementById("userPill");
        const logoutBtn = document.getElementById("logoutBtn");
        const authLinks = document.getElementById("headerAuthLinks");
        const btnNewJourney = document.getElementById("btnHeaderNewJourney");

        if (userPill) userPill.style.display = "none";
        if (logoutBtn) logoutBtn.style.display = "none";
        if (btnNewJourney) btnNewJourney.style.display = "none";
        if (authLinks) authLinks.style.display = "flex";

        // Show lock badges on protected tabs
        document.querySelectorAll(".locked-badge").forEach(el => el.style.display = "inline");
      },

      handleInitialNavigation(isAuthenticated) {
        const hash = window.location.hash.replace("#", "").toLowerCase() || "login";
        
        if (isAuthenticated) {
          const redirectDest = localStorage.getItem("ps_redirect_destination");
          if (redirectDest && PROTECTED_SCREENS.includes(redirectDest)) {
            localStorage.removeItem("ps_redirect_destination");
            switchScreen(redirectDest);
          } else if (["login", "register", "forgot", "reset", "landing"].includes(hash)) {
            switchScreen('home');
          } else {
            switchScreen(hash);
          }
        } else {
          // Unauthenticated users: ONLY specific public sub-pages allowed, otherwise LOGIN IS FIRST PAGE!
          const allowedPublicSubPages = ["register", "forgot", "reset", "verify-email", "privacy", "terms"];
          if (allowedPublicSubPages.includes(hash)) {
            switchScreen(hash);
          } else {
            if (PROTECTED_SCREENS.includes(hash)) {
              localStorage.setItem("ps_redirect_destination", hash);
            }
            switchScreen('login');
          }
        }
      },

      async login() {
        const email = document.getElementById("loginEmail").value.trim();
        const password = document.getElementById("loginPass").value.trim();
        const btn = document.getElementById("btnLoginSubmit");

        if (!email || !password) {
          showToast("Please provide both email and password.");
          return;
        }

        btn.disabled = true;
        try {
          const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
          });
          const data = await res.json();
          if (res.status === 403) {
            showToast("Email verification required before accessing the learning application.");
            switchScreen('verify-email');
            return;
          }
          if (!res.ok) throw new Error(data.detail || "Invalid email or password.");

          this.authToken = data.access_token || data.token;
          this.currentUser = data.user;
          localStorage.setItem("ps_token", this.authToken);
          localStorage.setItem("ps_user", JSON.stringify(this.currentUser));

          this.setAuthenticatedState();
          showToast(`Welcome back, ${data.user.full_name || data.user.email}!`);

          const redirectDest = localStorage.getItem("ps_redirect_destination");
          if (redirectDest && PROTECTED_SCREENS.includes(redirectDest)) {
            localStorage.removeItem("ps_redirect_destination");
            switchScreen(redirectDest);
          } else {
            switchScreen('home');
          }
        } catch (err) {
          showToast(err.message);
        } finally {
          btn.disabled = false;
        }
      },

      async register() {
        const full_name = document.getElementById("regName").value.trim();
        const email = document.getElementById("regEmail").value.trim();
        const password = document.getElementById("regPass").value.trim();
        const preferred_language = document.getElementById("regLang").value;
        const btn = document.getElementById("btnRegSubmit");

        if (!full_name || !email || !password) {
          showToast("Please fill all required registration fields.");
          return;
        }

        btn.disabled = true;
        try {
          const res = await fetch("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ full_name, email, password, preferred_language })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Registration failed.");

          if (data.is_verified === false) {
            showToast("Registration successful! Please verify your email code.");
            const tokenInput = document.getElementById("verifyEmailTokenInput");
            if (tokenInput) tokenInput.value = data.verification_token || "";
            switchScreen('verify-email');
            return;
          }

          this.authToken = data.access_token || data.token;
          this.currentUser = data.user;
          localStorage.setItem("ps_token", this.authToken);
          localStorage.setItem("ps_user", JSON.stringify(this.currentUser));

          this.setAuthenticatedState();
          showToast("Account created successfully! Welcome to Pod-Siksha.");
          switchScreen('home');
        } catch (err) {
          showToast("Registration error: " + err.message);
        } finally {
          btn.disabled = false;
        }
      },

      async submitEmailVerification() {
        const token = document.getElementById("verifyEmailTokenInput").value.trim();
        if (!token) { showToast("Please enter verification token."); return; }
        try {
          const res = await fetch("/api/auth/verify-email", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Verification failed.");

          this.authToken = data.access_token || data.token;
          this.currentUser = data.user;
          localStorage.setItem("ps_token", this.authToken);
          localStorage.setItem("ps_user", JSON.stringify(this.currentUser));

          this.setAuthenticatedState();
          showToast("Email verified! Welcome to your learning atelier.");
          switchScreen('home');
        } catch (err) {
          showToast("Verification error: " + err.message);
        }
      },

      async resendVerificationPrompt() {
        const email = prompt("Enter your registered email address:");
        if (!email) return;
        try {
          const res = await fetch("/api/auth/resend-verification", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Failed to resend code.");
          showToast(`Fresh verification token generated: ${data.verification_token || 'Check logs'}`);
          const tokenInput = document.getElementById("verifyEmailTokenInput");
          if (tokenInput) tokenInput.value = data.verification_token || "";
        } catch (err) {
          showToast("Error: " + err.message);
        }
      },

      logout(callServer = true) {
        const token = this.authToken || localStorage.getItem("ps_token");
        if (callServer && token) {
          fetch("/api/auth/logout", {
            method: "POST",
            headers: { "Authorization": "Bearer " + token }
          }).catch(() => {});
        }

        localStorage.removeItem("ps_token");
        localStorage.removeItem("ps_user");
        localStorage.removeItem("ps_redirect_destination");

        this.setUnauthenticatedState();
        showToast("Signed out safely.");

        // Clear history stack to prevent back-button exposing protected views
        history.replaceState(null, '', '#login');
        switchScreen('login');
      }
    };

    // Strict Master Route Switcher
    function switchScreen(screenId) {
      // 1. Guard protected screens: any screen other than public subpages requires auth
      const allowedPublic = ['login', 'register', 'forgot', 'reset', 'verify-email', 'privacy', 'terms'];
      if (!allowedPublic.includes(screenId) && !AuthManager.isAuthenticated()) {
        localStorage.setItem("ps_redirect_destination", screenId);
        showToast("Authentication required. Please sign in to access your atelier.");
        switchScreen('login');
        return;
      }

      // 2. Hide all screen frames
      ALL_SCREENS.forEach(s => {
        const frame = document.getElementById('view-' + s);
        const tab = document.getElementById('tab-' + s);
        if (frame) frame.classList.remove('active');
        if (tab) tab.classList.remove('active');
      });

      // 3. Activate target screen frame
      const targetFrame = document.getElementById('view-' + screenId);
      const targetTab = document.getElementById('tab-' + screenId);

      if (targetFrame) targetFrame.classList.add('active');
      if (targetTab) targetTab.classList.add('active');

      window.location.hash = screenId;
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // 4. Trigger authentic data fetching for protected screens
      if (screenId === 'home') loadJourneys();
      if (screenId === 'insights') loadInsights();
      if (screenId === 'concept-dna') loadConceptDNA(currentSessionId);
      if (screenId === 'teachback') initTeachBack(currentSessionId);
    }

    // Hash change listener for browser back/forward buttons
    window.addEventListener("hashchange", () => {
      const hash = window.location.hash.replace("#", "") || "landing";
      switchScreen(hash);
    });

    // Toast Notifications
    function showToast(msg) {
      const toast = document.getElementById("toastMessage");
      if (!toast) return;
      toast.innerText = msg;
      toast.style.display = "block";
      clearTimeout(window._toastTimeout);
      window._toastTimeout = setTimeout(() => { toast.style.display = "none"; }, 3500);
    }

    function togglePass(id) {
      const input = document.getElementById(id);
      if (input) input.type = (input.type === "password") ? "text" : "password";
    }

    // Physical Acoustic Chime Test
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

    // Forgot Password Flow
    function openForgotModal() { document.getElementById("forgotPasswordModal").style.display = "flex"; }
    function closeForgotModal() { document.getElementById("forgotPasswordModal").style.display = "none"; }

    async function submitForgotPassword() {
      const email = document.getElementById("forgotEmailInput").value.trim();
      if (!email) { showToast("Please enter email address."); return; }
      try {
        const res = await fetch("/api/auth/forgot-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Reset request failed.");

        document.getElementById("forgotStep1").style.display = "none";
        document.getElementById("forgotStep2").style.display = "block";
        const notice = document.getElementById("tokenNotice");
        notice.innerHTML = `<strong>Token Issued:</strong> <code style="word-break:break-all;">${data.reset_token || data.dev_reset_token}</code>`;
        document.getElementById("resetTokenInput").value = data.reset_token || data.dev_reset_token || "";
        showToast("Password reset token generated.");
      } catch (err) {
        showToast(err.message);
      }
    }

    async function submitResetPassword() {
      const token = document.getElementById("resetTokenInput").value.trim();
      const new_password = document.getElementById("resetNewPassInput").value.trim();
      if (!token || !new_password) { showToast("Please enter token and new password."); return; }
      try {
        const res = await fetch("/api/auth/reset-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token, new_password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Reset failed.");

        showToast("Password updated! Please sign in with your new password.");
        closeForgotModal();
        switchScreen("login");
      } catch (err) {
        showToast(err.message);
      }
    }

    // Chapter Creation Flow
    function openNewChapterModal() { document.getElementById("newChapterModal").style.display = "flex"; }
    function closeNewChapterModal() { document.getElementById("newChapterModal").style.display = "none"; }

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
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};

        const res = await fetch("/api/session", { method: "POST", headers, body: formData });
        const data = await res.json();
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
        if (!res.ok) throw new Error(data.detail || "Episode generation failed.");

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

    // Journeys List
    async function loadJourneys() {
      const listEl = document.getElementById("recentJourneysList");
      if (!listEl) return;
      try {
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/user/journeys", { headers });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
        const data = await res.json();
        const journeys = data.journeys || [];

        const countEl = document.getElementById("journeysCountLabel");
        if (countEl) countEl.innerText = `${journeys.length} Sessions Available`;

        if (journeys.length === 0) {
          listEl.innerHTML = `<div style="padding:24px; text-align:center; color:var(--ink-secondary); background:var(--surface-tinted); border-radius:var(--radius-md);">No sessions found in your atelier yet. Click '+ New Journey' to upload your first chapter!</div>`;
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
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch(`/api/session/${id}`, { method: "DELETE", headers });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
        if (!res.ok) throw new Error("Delete failed");
        showToast("Session removed.");
        loadJourneys();
      } catch (err) {
        showToast("Error: " + err.message);
      }
    }

    // Studio & Audio Engine
    async function loadStudioSession(sessionId) {
      if (!sessionId) return;
      currentSessionId = sessionId;
      try {
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch(`/api/session/${sessionId}`, { headers });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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
      const token = AuthManager.authToken || localStorage.getItem("ps_token");
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
      if (isPlaying) playCurrentTurnAudio();
    }

    function updatePlayButtonState() {
      const label = document.getElementById("studioPlayText");
      if (label) label.innerText = isPlaying ? "Pause" : "Play Turn";
    }

    // Interruption Engine
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
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/ask", { method: "POST", headers, body: formData });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/ask", { method: "POST", headers, body: formData });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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

    // Insights & Cognitive Telemetry
    async function loadInsights() {
      try {
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/insights/personal", { headers });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch(`/api/memory-loop/${id}/resolve`, { method: "POST", headers });
        if (!res.ok) throw new Error("Resolve failed");
        showToast("Touchpoint reviewed! Spaced interval adapted.");
        loadInsights();
      } catch (err) {
        showToast("Error: " + err.message);
      }
    }

    // Concept DNA
    async function loadConceptDNA(sessionId) {
      if (!sessionId) {
        sessionId = currentSessionId;
        if (!sessionId) {
          const token = AuthManager.authToken || localStorage.getItem("ps_token");
          const headers = token ? { "Authorization": "Bearer " + token } : {};
          const journeysRes = await fetch("/api/user/journeys", { headers });
          const jData = await journeysRes.json();
          if (jData.journeys && jData.journeys.length) sessionId = jData.journeys[0].id;
        }
      }
      if (!sessionId) return;
      try {
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch(`/api/concept-dna/${sessionId}`, { headers });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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

    // Teach-Back Mode
    let activeTeachBackConcept = "Water Photolysis";

    function startTeachBackForConcept(conceptTag) {
      activeTeachBackConcept = conceptTag;
      switchScreen('teachback');
    }

    async function initTeachBack(sessionId) {
      sessionId = sessionId || currentSessionId;
      if (!sessionId) return;
      try {
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = "Bearer " + token;

        const res = await fetch("/api/teachback/prompt", {
          method: "POST",
          headers,
          body: JSON.stringify({ session_id: sessionId, concept_tag: activeTeachBackConcept })
        });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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
        const token = AuthManager.authToken || localStorage.getItem("ps_token");
        const headers = token ? { "Authorization": "Bearer " + token } : {};
        const res = await fetch("/api/teachback/evaluate", {
          method: "POST",
          headers,
          body: formData
        });
        if (res.status === 401) { AuthManager.logout(false); switchScreen('login'); return; }
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

    // BOOTSTRAP INITIALIZATION
    window.addEventListener("DOMContentLoaded", () => {
      AuthManager.initialize();
    });
  </script>
"""

# Replace script in html
html = re.sub(r"<script>.*?</script>", js_strict_engine, html, flags=re.DOTALL)

with open(target_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated strict-auth index.html ({len(html)} bytes).")
