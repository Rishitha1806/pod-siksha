"""
Integrates the Universal AI Animated Learning Platform frontend views,
components, modals, and controllers into static/index.html.
"""

import sys
import os

INDEX_PATH = r"C:\Users\jvris\Downloads\pod-siksha\static\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS before </style>
NEW_CSS = """
    /* ==============================================================
       UNIVERSAL AI ANIMATED LEARNING PLATFORM STYLES (Aura Atelier)
       ============================================================== */
    .animated-studio-wrap {
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 24px;
      margin-top: 16px;
    }
    @media (max-width: 1024px) {
      .animated-studio-wrap {
        grid-template-columns: 1fr;
      }
    }
    .animated-canvas-container {
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #13221E;
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: var(--shadow-elevated);
      border: 2px solid var(--border-parchment);
    }
    .animated-canvas-container canvas {
      width: 100%;
      height: 100%;
      display: block;
      object-fit: contain;
    }
    .animated-controls-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: white;
      padding: 12px 18px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-parchment);
      margin-top: 12px;
      flex-wrap: wrap;
    }
    .animated-scrubber-wrap {
      flex: 1;
      min-width: 160px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .animated-scrubber {
      flex: 1;
      height: 6px;
      border-radius: 3px;
      accent-color: var(--accent-surya);
      cursor: pointer;
    }
    .scene-pill-nav {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding: 4px 0;
      scrollbar-width: none;
    }
    .scene-pill-nav::-webkit-scrollbar { display: none; }
    .scene-pill-btn {
      padding: 6px 12px;
      font-size: 11px;
      font-weight: 700;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-parchment);
      background: var(--surface-tinted);
      color: var(--ink-secondary);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
    }
    .scene-pill-btn.active {
      background: var(--accent-terracotta);
      color: white;
      border-color: var(--accent-terracotta);
    }
    .profile-badge-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      background: var(--accent-celadon-light);
      color: var(--accent-celadon);
      border: 1px solid rgba(82,130,113,0.25);
    }
    .profile-card-option {
      border: 2px solid var(--border-parchment);
      border-radius: var(--radius-md);
      padding: 14px;
      background: white;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .profile-card-option:hover {
      border-color: var(--accent-surya);
      background: #FFFDF9;
      transform: translateY(-2px);
    }
    .profile-card-option.selected {
      border-color: var(--accent-terracotta);
      background: #FDF7F5;
      box-shadow: 0 0 0 3px rgba(224,90,71,0.15);
    }
    .animated-library-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    .animated-lesson-card {
      background: white;
      border: 1px solid var(--border-parchment);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: var(--shadow-ambient);
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
    }
    .animated-lesson-card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-elevated);
      border-color: var(--accent-surya);
    }
    .animated-thumb-stage {
      height: 140px;
      background: #13221E;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    .socratic-doubt-overlay {
      position: absolute;
      inset: 0;
      background: rgba(19,34,30,0.85);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      z-index: 20;
    }
    .checkpoint-overlay-card {
      position: absolute;
      inset: 20px;
      background: rgba(253,251,247,0.96);
      backdrop-filter: blur(10px);
      border-radius: var(--radius-md);
      padding: 24px;
      display: none;
      flex-direction: column;
      justify-content: center;
      box-shadow: var(--shadow-elevated);
      border: 2px solid var(--accent-surya);
      z-index: 15;
    }
"""

if "animated-studio-wrap" not in content:
    content = content.replace("</style>", NEW_CSS + "\n</style>", 1)
    print("Added CSS styles.")

# 2. Update Master Switcher Navigation Tabs
SWITCHER_SEARCH = '<nav class="screen-switcher-bar" id="mainScreenSwitcher" style="display:none !important;">'
SWITCHER_REPLACE = """<nav class="screen-switcher-bar" id="mainScreenSwitcher" style="display:none !important;">
      <button class="screen-tab-btn active" id="tab-home" onclick="switchScreen('home')">Atelier Home</button>
      <button class="screen-tab-btn highlight" id="tab-animated-studio" onclick="switchScreen('animated-studio')">🎬 Animated Studio</button>
      <button class="screen-tab-btn" id="tab-animated-library" onclick="switchScreen('animated-library')">Library</button>
      <button class="screen-tab-btn" id="tab-insights" onclick="switchScreen('insights')">Insights</button>
      <button class="screen-tab-btn" id="tab-studio" onclick="switchScreen('studio')">Podcast</button>
      <button class="screen-tab-btn" id="tab-workspace" onclick="switchScreen('workspace')">Workspace</button>
      <button class="screen-tab-btn" id="tab-concept-dna" onclick="switchScreen('concept-dna')">Concept DNA</button>
      <button class="screen-tab-btn" id="tab-teachback" onclick="switchScreen('teachback')">Teach-Back</button>
      <button class="screen-tab-btn" id="tab-privacy" onclick="switchScreen('privacy')">Privacy</button>
      <button class="screen-tab-btn" id="tab-terms" onclick="switchScreen('terms')">Terms</button>"""

if 'id="tab-animated-studio"' not in content:
    content = content.replace(SWITCHER_SEARCH, SWITCHER_REPLACE, 1)
    print("Updated navigation bar.")

# 3. Add Universal AI Animated Learning Hero Card to view-home
HERO_SEARCH = '<section class="screen-frame" id="view-home">'
HERO_CARD = """<section class="screen-frame" id="view-home">
      <!-- Universal AI Animated Learning Platform Hero -->
      <div class="hero-resume-card" style="background: linear-gradient(135deg, #13221E 0%, #1A342B 100%); margin-bottom: 24px; border: 2px solid var(--accent-surya); box-shadow: var(--shadow-elevated);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
          <div style="max-width: 650px;">
            <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(255,159,28,0.18); border:1px solid var(--accent-surya); padding:4px 12px; border-radius:var(--radius-full); margin-bottom:10px;">
              <span style="font-size:11px; font-weight:800; color:var(--accent-surya); letter-spacing:1px; text-transform:uppercase;">✨ Universal AI Animated Learning</span>
            </div>
            <h2 style="font-family:var(--font-editorial); font-size:32px; color:white; line-height:1.2; margin-bottom:8px;">
              Learn Anything. In Your Language. Through Animation.
            </h2>
            <p style="font-size:14px; color:#CAD8D2; line-height:1.5;">
              One AI teacher. Every subject. Every language. Every generation. From Children (5–12) to Older Adults (60+), understand complex concepts through dynamic 60fps simulations, synchronized voice narration, and in-video Socratic Q&amp;A.
            </p>
          </div>
          <div style="display:flex; flex-direction:column; gap:10px; align-items:flex-end;">
            <button class="btn-action-primary" style="background:var(--accent-terracotta); font-size:14px; padding:12px 22px;" onclick="openAnimatedModal()">
              <span>+ Create Animated Lesson</span>
            </button>
            <button class="btn-action-outline" style="border-color:#528271; color:#CAD8D2; font-size:13px; padding:8px 16px;" onclick="switchScreen('animated-studio')">
              <span>Enter Animated Studio &rarr;</span>
            </button>
          </div>
        </div>

        <div style="display:flex; gap:16px; margin-top:20px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.12); flex-wrap:wrap;">
          <div style="font-size:12px; color:#A4B5AD;">
            <strong style="color:white;">8 Core Domains:</strong> Biology · Physics · Mathematics · Chemistry · CS · Geography · Finance · Daily Skills
          </div>
          <div style="font-size:12px; color:#A4B5AD;">
            <strong style="color:white;">5 Generations:</strong> Child · Teen · University · Professional · Older Adult
          </div>
          <div style="font-size:12px; color:#A4B5AD;">
            <strong style="color:white;">10 Languages:</strong> Telugu, Hindi, English, Tamil, Kannada, Marathi &amp; more
          </div>
        </div>
      </div>
"""

if "✨ Universal AI Animated Learning" not in content:
    content = content.replace(HERO_SEARCH, HERO_CARD, 1)
    print("Added Hero Card to Atelier Home.")

# 4. Insert view-animated-studio and view-animated-library before </main>
STUDIO_VIEWS = """
    <!-- ==============================================================
         ANIMATED VIDEO STUDIO ("Universal AI Visual Stage")
         ============================================================== -->
    <section class="screen-frame" id="view-animated-studio">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
        <div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="editorial-label" style="margin-bottom:0;">Universal Animated Stage</span>
            <span id="animStudioProfileBadge" class="profile-badge-pill">Teenager (Ages 13–17)</span>
            <span id="animStudioLangBadge" class="profile-badge-pill" style="background:#FFF3E0; color:#E65100; border-color:#FFE0B2;">Telugu</span>
            <span id="animStudioStyleBadge" class="profile-badge-pill" style="background:#EDE7F6; color:#5E35B1; border-color:#D1C4E9;">2D Scientific</span>
          </div>
          <h1 id="animStudioTitle" class="editorial-h1" style="font-size:28px; margin-top:6px;">How the Human Heart Pumps Blood</h1>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
          <button class="btn-action-outline" onclick="openAnimatedDoubtModal()" title="Ask doubt (Spacebar)">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
            <span>Ask Doubt (Space)</span>
          </button>
          <button class="btn-action-primary" style="background:var(--accent-surya); color:#13221E;" onclick="triggerVideoExport()">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span id="btnExportText">Export MP4 Video</span>
          </button>
          <button class="btn-action-primary" style="background:var(--accent-terracotta);" onclick="openAnimatedModal()">
            <span>+ New Lesson</span>
          </button>
        </div>
      </div>

      <div class="animated-studio-wrap">
        <!-- Left: Main 16:9 Canvas Stage & Controls -->
        <div>
          <div class="animated-canvas-container">
            <canvas id="animatedStageCanvas" width="1280" height="720"></canvas>

            <!-- In-Video Checkpoint Overlay -->
            <div id="animCheckpointOverlay" class="checkpoint-overlay-card">
              <div style="font-size:12px; font-weight:800; color:var(--accent-terracotta); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
                Interactive Checkpoint · Test Understanding
              </div>
              <h3 id="cpQuestionText" style="font-family:var(--font-editorial); font-size:22px; color:var(--ink-primary); margin-bottom:14px;">
                How many main chambers are there in the human heart?
              </h3>
              <div id="cpOptionsList" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px;">
                <!-- Injected dynamically -->
              </div>
              <div id="cpFeedbackBox" style="display:none; padding:10px; border-radius:var(--radius-sm); font-size:12px; margin-bottom:12px;"></div>
              <div style="display:flex; justify-content:flex-end; gap:10px;">
                <button id="cpContinueBtn" class="btn-action-primary" style="display:none;" onclick="closeCheckpointOverlay(true)">
                  Continue Next Scene &rarr;
                </button>
              </div>
            </div>

            <!-- In-Video Socratic Ask Doubt Overlay -->
            <div id="animDoubtOverlay" class="socratic-doubt-overlay">
              <div class="atelier-card" style="max-width:520px; width:100%; padding:24px; background:white; position:relative;">
                <button onclick="closeAnimatedDoubtModal()" style="position:absolute; top:12px; right:12px; background:none; border:none; font-size:20px; cursor:pointer;">&times;</button>
                <div class="editorial-label">In-Video Socratic Teacher</div>
                <h3 style="font-size:20px; margin-bottom:6px;">Have a Doubt on this Scene?</h3>
                <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:14px;">
                  Ask in your own language. The AI teacher will explain directly grounded in this scene's visual simulation.
                </p>
                <textarea id="animDoubtInput" class="form-input" rows="3" placeholder="e.g. Why is the left ventricle wall thicker than the right?"></textarea>
                <div id="animDoubtResponseBox" style="display:none; margin-top:12px; padding:12px; background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); font-size:13px;">
                  <div id="animDoubtAnswerText" style="color:var(--ink-primary); line-height:1.5;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px;">
                  <button id="animMicBtn" class="btn-action-outline" style="border-color:var(--accent-celadon); color:var(--accent-celadon);" onclick="toggleVoiceSpeechInput()">
                    <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
                    <span id="animMicLabel">Speak Question</span>
                  </button>
                  <button class="btn-action-primary" onclick="submitAnimatedDoubt()">
                    <span>Ask Teacher &rarr;</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Video Playback Controls Bar -->
          <div class="animated-controls-bar">
            <div style="display:flex; align-items:center; gap:8px;">
              <button class="btn-action-primary" id="btnAnimPlayPause" style="padding:8px 16px;" onclick="toggleAnimatedPlay()">
                <span id="btnAnimPlayIcon">▶ Play</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="stepAnimatedScene(-1)" title="Previous Scene">
                <span>⏮</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="stepAnimatedScene(1)" title="Next Scene">
                <span>⏭</span>
              </button>
            </div>

            <!-- Scrubber Timeline -->
            <div class="animated-scrubber-wrap">
              <span id="animTimeCurrent" style="font-size:12px; font-weight:700; color:var(--ink-secondary); font-variant-numeric:tabular-nums;">00:00</span>
              <input type="range" id="animTimelineScrubber" class="animated-scrubber" min="0" max="100" value="0" oninput="seekAnimatedTimeline(this.value)">
              <span id="animTimeTotal" style="font-size:12px; font-weight:700; color:var(--ink-secondary); font-variant-numeric:tabular-nums;">00:15</span>
            </div>

            <!-- Scene Switcher Pills -->
            <div class="scene-pill-nav" id="animScenePillsNav">
              <!-- Dynamically populated scene buttons -->
            </div>
          </div>
        </div>

        <!-- Right: Storyboard Drawer & Pedagogical Inspector -->
        <div>
          <div class="atelier-card" style="padding:20px;">
            <div class="editorial-label">Storyboard &amp; Concepts</div>
            <h3 class="editorial-h2" style="font-size:18px; margin-bottom:12px;">Lesson Scenes</h3>
            
            <div id="animStoryboardList" style="display:flex; flex-direction:column; gap:10px; max-height:540px; overflow-y:auto; padding-right:4px;">
              <!-- Dynamically rendered scene cards -->
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==============================================================
         ANIMATED LESSONS LIBRARY ("Universal Video Archive")
         ============================================================== -->
    <section class="screen-frame" id="view-animated-library">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
        <div>
          <div class="editorial-label">Universal Animated Video Archive</div>
          <h1 class="editorial-h1">Your Animated Lessons</h1>
          <p class="editorial-lead">Explore, replay, and export educational video lessons generated across all generations.</p>
        </div>
        <button class="btn-action-primary" style="background:var(--accent-terracotta);" onclick="openAnimatedModal()">
          <span>+ Create Animated Lesson</span>
        </button>
      </div>

      <!-- Filter by Profile -->
      <div style="display:flex; gap:8px; margin-bottom:16px; overflow-x:auto; padding-bottom:6px;">
        <button class="scene-pill-btn active" onclick="filterLibraryByProfile('all', this)">All Generations</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('child', this)">🧒 Children (5–12)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('teen', this)">🎒 Teenagers (13–17)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('university', this)">🎓 University (18–25)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('professional', this)">💼 Professionals (26–59)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('older_adult', this)">🌿 Older Adults (60+)</button>
      </div>

      <div id="animatedLibraryGrid" class="animated-library-grid">
        <!-- Injected dynamically -->
      </div>
    </section>
"""

# 5. Insert Creation Modal before </main>
ANIMATED_MODAL = """
  <!-- Universal AI Animated Lesson Creation Modal -->
  <div id="newAnimatedModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(19,34,30,0.65); backdrop-filter:blur(8px); z-index:999; justify-content:center; align-items:center;">
    <div class="atelier-card" style="max-width:680px; width:92%; padding:28px; background:white; position:relative; box-shadow:var(--shadow-elevated); max-height:92vh; overflow-y:auto;">
      <button onclick="closeAnimatedModal()" style="position:absolute; top:18px; right:18px; background:none; border:none; font-size:24px; cursor:pointer; color:var(--ink-secondary);">&times;</button>
      
      <div class="editorial-label">Universal Pedagogical Architect</div>
      <h2 class="editorial-h2" style="font-size:24px; margin-bottom:4px;">Create AI Animated Lesson</h2>
      <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:20px;">
        One AI teacher. Every subject. Every language. Every generation. Tailored specifically for the learner's age and style.
      </p>

      <form id="createAnimatedLessonForm" onsubmit="event.preventDefault(); submitNewAnimatedProject();">
        <!-- Step 1: Learner Generation Profile -->
        <div class="form-field" style="margin-bottom:18px;">
          <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:var(--ink-primary); margin-bottom:8px; display:block;">
            1. Target Generation &amp; Learner Profile
          </label>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(110px, 1fr)); gap:10px;" id="profileSelectGrid">
            <div class="profile-card-option" data-profile="child" onclick="selectAudienceProfile('child')">
              <span style="font-size:22px;">🧒</span>
              <span style="font-size:12px; font-weight:700;">Child</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 5–12</span>
            </div>
            <div class="profile-card-option selected" data-profile="teen" onclick="selectAudienceProfile('teen')">
              <span style="font-size:22px;">🎒</span>
              <span style="font-size:12px; font-weight:700;">Teen</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 13–17</span>
            </div>
            <div class="profile-card-option" data-profile="university" onclick="selectAudienceProfile('university')">
              <span style="font-size:22px;">🎓</span>
              <span style="font-size:12px; font-weight:700;">University</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 18–25</span>
            </div>
            <div class="profile-card-option" data-profile="professional" onclick="selectAudienceProfile('professional')">
              <span style="font-size:22px;">💼</span>
              <span style="font-size:12px; font-weight:700;">Professional</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 26–59</span>
            </div>
            <div class="profile-card-option" data-profile="older_adult" onclick="selectAudienceProfile('older_adult')">
              <span style="font-size:22px;">🌿</span>
              <span style="font-size:12px; font-weight:700;">Older Adult</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 60+</span>
            </div>
          </div>
          <input type="hidden" id="animModalProfileInput" value="teen">
        </div>

        <!-- Step 2: Language & Animation Style -->
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:18px;">
          <div class="form-field">
            <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">2. Spoken Language</label>
            <select id="animModalLangSelect" class="form-input">
              <option value="te" selected>Telugu (తెలుగు)</option>
              <option value="hi">Hindi (हिन्दी)</option>
              <option value="en">English</option>
              <option value="ta">Tamil (தமிழ்)</option>
              <option value="kn">Kannada (ಕನ್ನಡ)</option>
              <option value="mr">Marathi (मराठी)</option>
              <option value="bn">Bengali (বাংলা)</option>
              <option value="ml">Malayalam (മലയാളം)</option>
              <option value="gu">Gujarati (ગુજરાતી)</option>
              <option value="or">Odia (ଓଡ଼ିଆ)</option>
            </select>
          </div>
          <div class="form-field">
            <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">3. Animation Style</label>
            <select id="animModalStyleSelect" class="form-input">
              <option value="educational_2d" selected>2D Scientific / Conceptual</option>
              <option value="cartoon">Playful Cartoon / Illustrated</option>
              <option value="simulation">Dynamic Physics Simulation</option>
              <option value="whiteboard">Minimalist Whiteboard</option>
              <option value="infographic">High-Density Infographic</option>
            </select>
          </div>
        </div>

        <!-- Step 3: What do you want to learn? -->
        <div class="form-field" style="margin-bottom:14px;">
          <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">4. Lesson Title / Concept</label>
          <input type="text" id="animModalTitleInput" class="form-input" placeholder="e.g. Transformers &amp; Electromagnetic Induction">
        </div>

        <!-- Input Modes: Document Upload or Topic Query -->
        <div class="form-field" style="margin-bottom:14px;">
          <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">5. Upload Document (Optional - PDF, DOCX, PPTX, TXT)</label>
          <input type="file" id="animModalFileInput" class="form-input" accept=".pdf,.docx,.pptx,.txt">
        </div>

        <div class="form-field" style="margin-bottom:18px;">
          <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">Or Describe Topic / Paste Notes</label>
          <textarea id="animModalContentText" class="form-input" rows="3" placeholder="Describe the topic or enter questions: e.g. How do step-up and step-down transformers work? Explain mutual induction and formula V1/V2 = N1/N2."></textarea>
        </div>

        <!-- Generating Status Indicator -->
        <div id="animGeneratingStatus" style="display:none; background:var(--surface-tinted); border:1px solid var(--accent-surya); padding:16px; border-radius:var(--radius-sm); margin-bottom:16px; text-align:center;">
          <div style="font-weight:700; color:var(--accent-terracotta); font-size:14px;">Synthesizing AI Animated Lesson...</div>
          <div style="color:var(--ink-secondary); font-size:12px; margin-top:4px;">
            Gemini is tailoring storyboard scenes, declarative simulation parameters, and multilingual narration.
          </div>
        </div>

        <button type="submit" id="btnSubmitAnimated" class="btn-action-primary" style="width:100%; justify-content:center; padding:14px; font-size:15px; background:var(--accent-terracotta);">
          Generate Animated Lesson &amp; Launch Studio &rarr;
        </button>
      </form>
    </div>
  </div>
"""

if 'id="view-animated-studio"' not in content:
    content = content.replace("</main>", STUDIO_VIEWS + "\n" + ANIMATED_MODAL + "\n</main>", 1)
    print("Added Animated Studio, Library, and Creation Modal views.")

# 6. Add animation_engine.js script tag
SCRIPT_TAG = '<script src="/static/animation_engine.js"></script>'
if SCRIPT_TAG not in content:
    content = content.replace("<script>", SCRIPT_TAG + "\n  <script>", 1)
    print("Included animation_engine.js script tag.")

# 7. Update PROTECTED_SCREENS
content = content.replace(
    "const PROTECTED_SCREENS = ['home', 'insights', 'studio', 'workspace', 'concept-dna', 'teachback'];",
    "const PROTECTED_SCREENS = ['home', 'animated-studio', 'animated-library', 'insights', 'studio', 'workspace', 'concept-dna', 'teachback'];"
)

# 8. Update switchScreen to trigger animated data fetching
SWITCH_TRIGGER_SEARCH = "if (screenId === 'teachback') initTeachBack(currentSessionId);"
SWITCH_TRIGGER_REPLACE = """if (screenId === 'teachback') initTeachBack(currentSessionId);
      if (screenId === 'animated-studio') loadActiveAnimatedProject();
      if (screenId === 'animated-library') loadAnimatedProjectsList();"""

if "loadActiveAnimatedProject" not in content:
    content = content.replace(SWITCH_TRIGGER_SEARCH, SWITCH_TRIGGER_REPLACE, 1)
    print("Updated switchScreen data fetching.")

# Write back
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("HTML structure updated successfully!")
