import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Normalize CRLF to LF for reliable pattern matching
html = html.replace("\r\n", "\n")

# -------------------------------------------------------------
# 1. ADD CSS STYLES FOR KNOWLEDGE TREE, DRAWER, MODALS & PROFILE
# -------------------------------------------------------------
css_styles = """
    /* ==============================================================
       CONCEPT DNA KNOWLEDGE TREE & INTERACTIVE TOPOLOGY
       ============================================================== */
    .concept-tree-toolbar {
      background: white;
      border: 1px solid var(--border-parchment);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      margin-bottom: 14px;
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      box-shadow: var(--shadow-ambient);
    }
    .status-filter-pill {
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-parchment);
      background: white;
      cursor: pointer;
      color: var(--ink-secondary);
      transition: all 0.2s;
    }
    .status-filter-pill:hover, .status-filter-pill.active {
      background: var(--ink-primary);
      color: white;
      border-color: var(--ink-primary);
    }
    .status-filter-pill.pill-understood.active {
      background: var(--accent-celadon);
      border-color: var(--accent-celadon);
      color: white;
    }
    .status-filter-pill.pill-learning.active {
      background: var(--accent-surya);
      border-color: var(--accent-surya);
      color: #13221E;
    }
    .status-filter-pill.pill-revision.active {
      background: var(--accent-terracotta);
      border-color: var(--accent-terracotta);
      color: white;
    }
    .tree-ctrl-btn {
      width: 28px;
      height: 28px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-parchment);
      background: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 14px;
      cursor: pointer;
      color: var(--ink-primary);
      transition: all 0.15s;
    }
    .tree-ctrl-btn:hover {
      background: var(--surface-tinted);
      border-color: var(--accent-terracotta);
    }
    .concept-tree-container {
      position: relative;
      height: 640px;
      background: #FAF8F5;
      border: 1px solid var(--border-parchment);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: inset 0 2px 6px rgba(19,34,30,0.03);
    }
    .concept-tree-svg {
      width: 100%;
      height: 100%;
      cursor: grab;
      user-select: none;
    }
    .concept-tree-svg:active {
      cursor: grabbing;
    }
    .tree-link {
      fill: none;
      stroke: var(--border-parchment);
      stroke-width: 2px;
      transition: stroke 0.3s, stroke-width 0.3s;
    }
    .tree-link.prereq-link {
      stroke: var(--accent-terracotta);
      stroke-width: 2px;
      stroke-dasharray: 4 2;
    }
    .tree-link.related-link {
      stroke: var(--accent-surya);
      stroke-width: 1.5px;
    }
    .tree-node-group {
      cursor: pointer;
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .tree-node-group:hover {
      filter: drop-shadow(0 6px 12px rgba(19,34,30,0.12));
    }
    .tree-legend-strip {
      position: absolute;
      bottom: 12px;
      left: 14px;
      display: flex;
      gap: 12px;
      background: rgba(255,255,255,0.92);
      backdrop-filter: blur(6px);
      padding: 6px 14px;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-parchment);
      font-size: 11px;
      font-weight: 700;
      color: var(--ink-secondary);
      box-shadow: var(--shadow-ambient);
      z-index: 5;
    }
    .legend-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      margin-right: 4px;
    }
    .dot-root { background: var(--ink-primary); }
    .dot-understood { background: var(--accent-celadon); }
    .dot-learning { background: var(--accent-surya); }
    .dot-revision { background: var(--accent-terracotta); }

    /* Concept Detail Drawer */
    .concept-detail-drawer {
      position: fixed;
      top: 0;
      right: -480px;
      width: 440px;
      max-width: 90vw;
      height: 100vh;
      background: white;
      box-shadow: -8px 0 24px rgba(19,34,30,0.18);
      z-index: 1000;
      transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      padding: 28px;
      overflow-y: auto;
    }
    .concept-detail-drawer.open {
      right: 0;
    }
    .drawer-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(19,34,30,0.4);
      backdrop-filter: blur(3px);
      z-index: 999;
      display: none;
    }
    .drawer-backdrop.open {
      display: block;
    }

    /* Honest Empty States */
    .empty-state-atelier {
      padding: 48px 24px;
      text-align: center;
      background: white;
      border: 1px dashed var(--border-parchment);
      border-radius: var(--radius-md);
      margin: 16px 0;
    }
    .empty-glyph {
      font-size: 38px;
      margin-bottom: 8px;
    }

    /* Complexity Selector Pills */
    .complexity-pill-btn {
      flex: 1;
      padding: 10px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-parchment);
      background: white;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .complexity-pill-btn.selected {
      border: 2px solid var(--accent-terracotta);
      background: var(--surface-tinted);
    }

    /* Comparison Modal */
    .compare-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin: 16px 0;
    }
    .compare-col {
      background: var(--surface-tinted);
      border: 1px solid var(--border-parchment);
      border-radius: var(--radius-sm);
      padding: 16px;
    }
"""

if "CONCEPT DNA KNOWLEDGE TREE" not in html:
    html = html.replace("</style>", css_styles + "\n</style>", 1)
    print("Added CSS styles for Knowledge Tree and Drawer.")

# -------------------------------------------------------------
# 2. SIMPLIFY TOP NAVIGATION: 6 CORE SCREENS
# -------------------------------------------------------------
nav_target = """    <nav class="screen-switcher-bar" id="mainScreenSwitcher" style="display:none !important;">
      <button class="screen-tab-btn active" id="tab-home" onclick="switchScreen('home')">Atelier Home</button>
      <button class="screen-tab-btn highlight" id="tab-animated-studio" onclick="switchScreen('animated-studio')">dYZ Animated Studio</button>
      <button class="screen-tab-btn" id="tab-animated-library" onclick="switchScreen('animated-library')">Library</button>
      <button class="screen-tab-btn" id="tab-insights" onclick="switchScreen('insights')">Insights</button>
      <button class="screen-tab-btn" id="tab-studio" onclick="switchScreen('studio')">Podcast</button>
      <button class="screen-tab-btn" id="tab-workspace" onclick="switchScreen('workspace')">Workspace</button>
      <button class="screen-tab-btn" id="tab-concept-dna" onclick="switchScreen('concept-dna')">Concept DNA</button>
      <button class="screen-tab-btn" id="tab-teachback" onclick="switchScreen('teachback')">Teach-Back</button>
      <button class="screen-tab-btn" id="tab-privacy" onclick="switchScreen('privacy')">Privacy</button>
      <button class="screen-tab-btn" id="tab-terms" onclick="switchScreen('terms')">Terms</button>
      <button class="screen-tab-btn active" id="tab-home" onclick="switchScreen('home')">Atelier Home</button>
      <button class="screen-tab-btn highlight" id="tab-insights" onclick="switchScreen('insights')">Insights</button>
      <button class="screen-tab-btn" id="tab-studio" onclick="switchScreen('studio')">Studio</button>
      <button class="screen-tab-btn" id="tab-workspace" onclick="switchScreen('workspace')">Workspace</button>
      <button class="screen-tab-btn" id="tab-concept-dna" onclick="switchScreen('concept-dna')">Concept DNA</button>
      <button class="screen-tab-btn" id="tab-teachback" onclick="switchScreen('teachback')">Teach-Back</button>
      <button class="screen-tab-btn" id="tab-privacy" onclick="switchScreen('privacy')">Privacy</button>
      <button class="screen-tab-btn" id="tab-terms" onclick="switchScreen('terms')">Terms</button>
    </nav>"""

nav_replacement = """    <nav class="screen-switcher-bar" id="mainScreenSwitcher" style="display:none !important;">
      <button class="screen-tab-btn active" id="tab-home" onclick="switchScreen('home')">Home</button>
      <button class="screen-tab-btn highlight" id="tab-learn" onclick="switchScreen('animated-studio')">Learn</button>
      <button class="screen-tab-btn" id="tab-library" onclick="switchScreen('animated-library')">Library</button>
      <button class="screen-tab-btn" id="tab-concept-dna" onclick="switchScreen('concept-dna')">Concept DNA</button>
      <button class="screen-tab-btn" id="tab-insights" onclick="switchScreen('insights')">Insights</button>
      <button class="screen-tab-btn" id="tab-profile" onclick="switchScreen('profile')">Profile</button>
    </nav>"""

# Match loosely if exact string differs slightly
if nav_target in html:
    html = html.replace(nav_target, nav_replacement, 1)
    print("Replaced main navigation with 6 clean items.")
else:
    # Use regex replacement for the screen-switcher-bar
    html = re.sub(
        r'<nav class="screen-switcher-bar" id="mainScreenSwitcher"[^>]*>.*?</nav>',
        nav_replacement.strip(),
        html,
        flags=re.DOTALL
    )
    print("Replaced screen-switcher-bar via regex.")

# Remove "Test Speakers" button from header
html = re.sub(
    r'<button class="btn-chime-test" onclick="triggerHarmonicChime\(\)"[^>]*>.*?</button>',
    '',
    html,
    flags=re.DOTALL
)

# -------------------------------------------------------------
# 3. REDESIGN CONCEPT DNA: INTERACTIVE KNOWLEDGE TREE
# -------------------------------------------------------------
concept_dna_old = """    <section class="screen-frame" id="view-concept-dna">
      <div class="editorial-label">Knowledge Topology</div>
      <h1 class="editorial-h1">Concept DNA</h1>
      <p class="editorial-lead">An interactive map of concept relationships extracted from your chapter. See prerequisites, dependencies, and mastery status.</p>

      <div id="conceptDnaCanvas" class="concept-dna-canvas">
        <div class="dna-cluster-row">
          <div class="dna-node mastered" onclick="showToast('Selected: Chloroplast Structure (100% Mastery)')">
            <span class="dna-node-label">Chloroplast Organelle</span>
            <span class="dna-node-status" style="color:var(--accent-celadon);">100% ? Mastered</span>
          </div>
          <div style="font-size:20px; color:var(--ink-secondary);">&rarr;</div>
          <div class="dna-node mastered" onclick="showToast('Selected: Thylakoid Membranes (100% Mastery)')">
            <span class="dna-node-label">Thylakoid Grana Stacks</span>
            <span class="dna-node-status" style="color:var(--accent-celadon);">100% ? Mastered</span>
          </div>
        </div>

        <div style="font-size:20px; color:var(--ink-secondary); margin:4px 0;">&darr;</div>

        <div class="dna-cluster-row">
          <div class="dna-node selected" onclick="showToast('Selected: Water Photolysis (13% Mastery - Revision Needed)')">
            <span class="dna-node-label">Water Photolysis ($2\\text{H}_2\\text{O} \\to 4\\text{H}^+ + 4e^-$)</span>
            <span class="dna-node-status" style="color:var(--accent-terracotta);">13% ? Revision Needed</span>
          </div>
          <div style="font-size:20px; color:var(--ink-secondary);">&rarr;</div>
          <div class="dna-node" onclick="showToast('Selected: RuBisCO Carbon Fixation (25% Mastery)')">
            <span class="dna-node-label">RuBisCO Calvin Cycle</span>
            <span class="dna-node-status" style="color:var(--accent-terracotta);">25% ? Revision Needed</span>
          </div>
        </div>

        <div style="margin-top:28px; text-align:center;">
          <button class="btn-action-primary" onclick="switchScreen('teachback')">
            Explain Selected Node in Teach-Back Mode &rarr;
          </button>
        </div>
      </div>
    </section>"""

concept_dna_new = """    <!-- ==============================================================
         8. CONCEPT DNA ("Interactive Personal Knowledge Tree")
         ============================================================== -->
    <section class="screen-frame" id="view-concept-dna">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
        <div>
          <div class="editorial-label">Interactive Knowledge Topology</div>
          <h1 class="editorial-h1" style="margin-bottom:4px;">Concept DNA Knowledge Tree</h1>
          <p class="editorial-lead" style="margin-bottom:0;">
            Your personal, growing knowledge tree. Explore concepts, directed prerequisites, mastery evidence, and diagnosed revision points.
          </p>
        </div>
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
          <button class="btn-action-outline" onclick="openCompareModal()">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg>
            <span>Compare Concepts</span>
          </button>
          <button class="btn-action-primary" onclick="openAnimatedModal()">
            <span>+ New Learning Journey</span>
          </button>
        </div>
      </div>

      <!-- Controls & Filter Toolbar -->
      <div class="concept-tree-toolbar">
        <div style="display:flex; gap:10px; align-items:center; flex:1; flex-wrap:wrap;">
          <select id="conceptTreeProjectSelect" class="form-input" style="max-width:280px; padding:6px 12px; font-size:13px;" onchange="handleConceptTreeProjectChange(this.value)">
            <option value="all">🌳 Entire Knowledge Forest (All Lessons)</option>
          </select>
          <div style="position:relative; flex:1; min-width:180px; max-width:320px;">
            <input type="text" id="conceptTreeSearch" class="form-input" placeholder="Search concepts in tree..." style="padding:6px 12px 6px 32px; font-size:13px;" oninput="handleConceptTreeSearch(this.value)">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="position:absolute; left:10px; top:50%; transform:translateY(-50%); color:var(--ink-secondary);"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
        </div>

        <div style="display:flex; gap:6px; align-items:center;">
          <span style="font-size:11px; font-weight:700; color:var(--ink-secondary); text-transform:uppercase; letter-spacing:0.5px;">Filter:</span>
          <button class="status-filter-pill active" data-filter="all" onclick="filterTreeStatus('all', this)">All (<span id="cntAll">0</span>)</button>
          <button class="status-filter-pill pill-understood" data-filter="understood" onclick="filterTreeStatus('understood', this)">Understood (<span id="cntUnderstood">0</span>)</button>
          <button class="status-filter-pill pill-learning" data-filter="learning" onclick="filterTreeStatus('learning', this)">Learning (<span id="cntLearning">0</span>)</button>
          <button class="status-filter-pill pill-revision" data-filter="needs_revision" onclick="filterTreeStatus('needs_revision', this)">Needs Revision (<span id="cntRevision">0</span>)</button>
        </div>

        <div style="display:flex; gap:4px; align-items:center; margin-left:auto;">
          <button class="tree-ctrl-btn" onclick="zoomConceptTree(1.2)" title="Zoom In">+</button>
          <button class="tree-ctrl-btn" onclick="zoomConceptTree(0.8)" title="Zoom Out">-</button>
          <button class="tree-ctrl-btn" onclick="resetConceptTreeView()" title="Fit to Screen" style="font-size:11px; padding:0 8px; width:auto;">Fit Screen</button>
        </div>
      </div>

      <!-- Tree Viewport Container -->
      <div id="conceptTreeContainer" class="concept-tree-container">
        <svg id="conceptTreeSvg" class="concept-tree-svg">
          <defs>
            <marker id="arrowPrereq" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="var(--accent-terracotta)" />
            </marker>
            <marker id="arrowRelated" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="var(--accent-surya)" />
            </marker>
          </defs>
          <g id="conceptTreeViewport"></g>
        </svg>

        <div id="conceptTreeEmptyState" class="empty-state-atelier" style="display:none; position:absolute; inset:40px; margin:auto; max-width:500px; height:max-content; border:none; box-shadow:var(--shadow-elevated);">
          <div class="empty-glyph">🌱</div>
          <h3 class="editorial-h2" style="font-size:24px; margin-bottom:8px;">Your Knowledge Tree Will Grow Here</h3>
          <p style="font-size:14px; color:var(--ink-secondary); max-width:440px; line-height:1.5; margin:0 auto 20px auto;">
            As you explore topics or upload study materials, Pod-Siksha extracts core concepts, structures prerequisites, and maps your understanding into a living knowledge garden.
          </p>
          <button class="btn-action-primary" onclick="openAnimatedModal()">+ Start First Learning Journey</button>
        </div>

        <div class="tree-legend-strip">
          <div class="legend-item"><span class="legend-dot dot-root"></span> Root Topic</div>
          <div class="legend-item"><span class="legend-dot dot-understood"></span> Understood (Quiz / Teach-Back)</div>
          <div class="legend-item"><span class="legend-dot dot-learning"></span> Currently Learning</div>
          <div class="legend-item"><span class="legend-dot dot-revision"></span> Needs Revision (Flagged / Misconception)</div>
        </div>
      </div>

      <!-- Concept Detail Drawer (Opens on node selection) -->
      <div id="conceptDrawerBackdrop" class="drawer-backdrop" onclick="closeConceptDetailDrawer()"></div>
      <div id="conceptDetailDrawer" class="concept-detail-drawer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px;">
          <div>
            <div id="drawerStatusBadge" style="display:inline-block; font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; padding:3px 8px; border-radius:var(--radius-full); margin-bottom:6px;">UNDERSTOOD</div>
            <h2 id="drawerConceptName" style="font-family:var(--font-editorial); font-size:26px; color:var(--ink-primary); line-height:1.2;">Concept Name</h2>
          </div>
          <button onclick="closeConceptDetailDrawer()" style="background:none; border:none; font-size:24px; cursor:pointer; color:var(--ink-secondary);">&times;</button>
        </div>

        <div id="drawerEvidenceBox" style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:10px 14px; font-size:12px; color:var(--ink-primary); margin-bottom:16px;">
          <strong>Evidence:</strong> <span id="drawerEvidenceText">Mastered in Checkpoint Quiz</span>
        </div>

        <div style="margin-bottom:16px;">
          <div class="editorial-label">Explanation & Why It Matters</div>
          <p id="drawerDefinition" style="font-size:14px; color:var(--ink-primary); line-height:1.55; margin-top:4px;"></p>
        </div>

        <div id="drawerPrereqsSection" style="margin-bottom:16px;">
          <div class="editorial-label">Prerequisites</div>
          <div id="drawerPrereqsList" style="display:flex; gap:6px; flex-wrap:wrap; margin-top:6px;"></div>
        </div>

        <div id="drawerRelatedSection" style="margin-bottom:20px;">
          <div class="editorial-label">Related Concepts</div>
          <div id="drawerRelatedList" style="display:flex; gap:6px; flex-wrap:wrap; margin-top:6px;"></div>
        </div>

        <!-- 6 Core Concept Actions -->
        <div style="margin-top:auto; display:flex; flex-direction:column; gap:8px;">
          <button class="btn-action-primary" id="btnDrawerExplain" onclick="triggerConceptExplainModal()" style="width:100%; justify-content:center;">
            Explain This Concept &rarr;
          </button>
          <button class="btn-action-outline" id="btnDrawerWatchAgain" onclick="watchConceptSceneAgain()" style="width:100%; justify-content:center;">
            Watch Original Animated Scene Again
          </button>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
            <button class="btn-action-outline" onclick="triggerConceptPractice()" style="justify-content:center; font-size:12px;">
              Practice (Quiz)
            </button>
            <button class="btn-action-outline" id="btnDrawerMarkRevision" onclick="markConceptRevisionAction()" style="justify-content:center; font-size:12px; border-color:var(--accent-terracotta); color:var(--accent-terracotta);">
              Mark for Revision
            </button>
          </div>
        </div>
      </div>
    </section>"""

html = re.sub(
    r'<section class="screen-frame"[^>]*id="view-concept-dna".*?</section>',
    concept_dna_new.strip(),
    html,
    flags=re.DOTALL
)
print("Replaced view-concept-dna with Interactive Knowledge Tree.")

# -------------------------------------------------------------
# 4. REDESIGN TEACH-BACK: REMOVE SAMPLE DATA & WIRE AUTHENTIC EVAL
# -------------------------------------------------------------
teachback_new = """    <!-- ==============================================================
         9. TEACH-BACK MODE ("Signature Cognitive Feature")
         ============================================================== -->
    <section class="screen-frame" id="view-teachback">
      <div class="editorial-label">Cognitive Assessment</div>
      <h1 class="editorial-h1">Teach-Back &middot; Explain What You Learned</h1>
      <p class="editorial-lead">Don't just watch animations. Explain the concept back to the AI educator in your own words. Gemini evaluates deep semantic understanding and identifies misconceptions.</p>

      <div class="teachback-console">
        <!-- Concept Selection Strip -->
        <div style="display:flex; gap:12px; align-items:center; margin-bottom:16px; flex-wrap:wrap;">
          <div style="font-weight:700; font-size:13px; color:var(--ink-secondary);">Select Concept to Explain:</div>
          <select id="teachbackConceptSelect" class="form-input" style="max-width:320px; font-size:13px; padding:6px 12px;" onchange="handleTeachbackConceptChange(this.value)">
            <option value="">Loading your concepts...</option>
          </select>
        </div>

        <div class="teachback-prompt-banner">
          <div class="editorial-label" style="margin-bottom:4px;">AI Educator Prompt</div>
          <div id="teachbackPromptText" style="font-family:var(--font-editorial); font-size:20px; color:var(--ink-primary);">"Can you explain this concept in your own words?"</div>
        </div>

        <div style="margin:16px 0;">
          <div class="form-field" style="margin-bottom:10px;">
            <label style="font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Your Explanation (Text or Voice)</label>
            <textarea id="teachbackTextInput" class="form-input" rows="4" placeholder="Explain how this concept works in your own words..."></textarea>
          </div>
          <div style="display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap;">
            <div style="display:flex; gap:10px; align-items:center;">
              <button type="button" class="btn-action-primary" style="padding:10px 22px; font-size:13px;" onclick="submitTeachBackExplanation()">
                Evaluate Explanation &rarr;
              </button>
              <button type="button" id="btnTeachbackMic" class="btn-action-outline" style="border-color:var(--accent-celadon); color:var(--accent-celadon); padding:10px 16px; font-size:13px;" onclick="toggleTeachbackVoiceInput()">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
                <span id="teachbackMicLabel">Speak Explanation</span>
              </button>
            </div>
            <span id="teachbackEvaluatingStatus" style="display:none; font-size:12px; font-weight:700; color:var(--accent-terracotta);">
              AI Educator is analyzing semantic understanding...
            </span>
          </div>
        </div>

        <!-- Semantic Diagnostic Breakdown (Hidden until submitted) -->
        <div id="teachbackEvalGrid" class="teachback-eval-grid" style="display:none;">
          <div class="eval-box understood">
            <div style="font-weight:700; color:var(--accent-celadon); font-size:14px; margin-bottom:6px;">
              ✓ What You Understood Correctly
            </div>
            <div id="tbUnderstoodList" style="font-size:13px; color:var(--ink-primary); line-height:1.5;"></div>
          </div>

          <div class="eval-box misconception" id="tbMiscBox" style="display:none;">
            <div style="font-weight:700; color:var(--accent-terracotta); font-size:14px; margin-bottom:6px;">
              ⚠ Diagnosed Misconception
            </div>
            <div id="tbMiscList" style="font-size:13px; color:var(--ink-primary); line-height:1.5;"></div>
          </div>

          <div class="eval-box" id="tbMissingBox" style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:14px; grid-column:1/-1;">
            <div style="font-weight:700; color:var(--ink-primary); font-size:13px; margin-bottom:4px;">
              Key Knowledge Points to Clarify:
            </div>
            <div id="tbMissingList" style="font-size:13px; color:var(--ink-secondary); line-height:1.5;"></div>
          </div>
        </div>

        <div id="teachbackFooterStrip" style="display:none; justify-content:space-between; align-items:center; margin-top:20px; padding-top:16px; border-top:1px solid var(--border-parchment); flex-wrap:wrap; gap:10px;">
          <span id="teachbackNextStep" style="font-size:13px; font-weight:700;">Recommended Next Step</span>
          <button class="btn-action-primary" id="btnTbRevisitScene" onclick="switchScreen('animated-studio')">Revisit Scene in Studio &rarr;</button>
        </div>
      </div>
    </section>"""

html = re.sub(
    r'<section class="screen-frame"[^>]*id="view-teachback".*?</section>',
    teachback_new.strip(),
    html,
    flags=re.DOTALL
)
print("Replaced view-teachback with authentic Teach-Back workflow.")

# -------------------------------------------------------------
# 5. ADD VIEW-PROFILE SCREEN
# -------------------------------------------------------------
profile_view = """    <!-- ==============================================================
         NEW: USER PROFILE & LEARNER PREFERENCES
         ============================================================== -->
    <section class="screen-frame" id="view-profile">
      <div class="editorial-label">Sovereign Account</div>
      <h1 class="editorial-h1">Learner Profile &amp; Preferences</h1>
      <p class="editorial-lead">Manage your explanation complexity, preferred instruction language, and view your verified learning telemetry.</p>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; max-width:880px;">
        <div class="atelier-card" style="padding:24px;">
          <div class="editorial-label">Learner Identity</div>
          <div style="display:flex; align-items:center; gap:14px; margin-top:10px; margin-bottom:18px;">
            <div id="profileAvatarLetter" style="width:48px; height:48px; border-radius:50%; background:var(--ink-primary); color:white; font-family:var(--font-editorial); font-size:24px; display:flex; align-items:center; justify-content:center;">L</div>
            <div>
              <div id="profileFullName" style="font-weight:700; font-size:17px; color:var(--ink-primary);">Verified Learner</div>
              <div id="profileEmail" style="font-size:13px; color:var(--ink-secondary);">learner@pod-siksha.edu</div>
            </div>
          </div>

          <div class="form-field" style="margin-bottom:14px;">
            <label style="font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Default Explanation Complexity</label>
            <select id="prefComplexity" class="form-input" onchange="saveLearnerPreference('complexity', this.value)">
              <option value="beginner">Beginner (Foundational principles, visual analogies)</option>
              <option value="intermediate" selected>Intermediate (Balanced academic depth, step-by-step)</option>
              <option value="advanced">Advanced (Rigorous technical derivations, formal mechanics)</option>
            </select>
          </div>

          <div class="form-field" style="margin-bottom:14px;">
            <label style="font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Instruction &amp; Voice Language</label>
            <select id="prefLanguage" class="form-input" onchange="saveLearnerPreference('language', this.value)">
              <option value="te" selected>Telugu (తెలుగు)</option>
              <option value="hi">Hindi (हिन्दी)</option>
              <option value="ta">Tamil (தமிழ்)</option>
              <option value="kn">Kannada (ಕನ್ನಡ)</option>
              <option value="mr">Marathi (मराठी)</option>
              <option value="bn">Bengali (বাংলা)</option>
              <option value="en">English (Universal)</option>
            </select>
          </div>

          <div style="margin-top:24px; padding-top:16px; border-top:1px solid var(--border-parchment);">
            <button class="btn-action-outline" style="border-color:var(--accent-terracotta); color:var(--accent-terracotta); width:100%; justify-content:center;" onclick="AuthManager.logout()">
              Sign Out of Session
            </button>
          </div>
        </div>

        <div class="atelier-card" style="padding:24px;">
          <div class="editorial-label">Learning Telemetry Summary</div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:14px;">
            <div style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:14px; text-align:center;">
              <div id="profStatUnderstood" style="font-size:28px; font-weight:800; color:var(--accent-celadon);">0</div>
              <div style="font-size:11px; font-weight:700; color:var(--ink-secondary); text-transform:uppercase;">Concepts Understood</div>
            </div>
            <div style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:14px; text-align:center;">
              <div id="profStatLearning" style="font-size:28px; font-weight:800; color:var(--accent-surya);">0</div>
              <div style="font-size:11px; font-weight:700; color:var(--ink-secondary); text-transform:uppercase;">In Progress</div>
            </div>
            <div style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:14px; text-align:center;">
              <div id="profStatRevision" style="font-size:28px; font-weight:800; color:var(--accent-terracotta);">0</div>
              <div style="font-size:11px; font-weight:700; color:var(--ink-secondary); text-transform:uppercase;">Needs Revision</div>
            </div>
            <div style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:14px; text-align:center;">
              <div id="profStatLessons" style="font-size:28px; font-weight:800; color:var(--ink-primary);">0</div>
              <div style="font-size:11px; font-weight:700; color:var(--ink-secondary); text-transform:uppercase;">Lessons Generated</div>
            </div>
          </div>

          <div style="margin-top:20px; font-size:12px; color:var(--ink-secondary); line-height:1.5;">
            🔒 All learning telemetry is strictly tenant-isolated and stored in Neon PostgreSQL.
          </div>
        </div>
      </div>
    </section>"""

if "id=\"view-profile\"" not in html:
    html = html.replace('</section>\n\n  <!-- New Chapter Creation Modal', '</section>\n\n' + profile_view + '\n\n  <!-- New Chapter Creation Modal')
    print("Added view-profile screen.")

# -------------------------------------------------------------
# 6. COMPARE CONCEPTS MODAL & EXPLAIN IT AGAIN MODAL
# -------------------------------------------------------------
modals_html = """
  <!-- Compare Concepts Modal -->
  <div id="compareConceptsModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(19,34,30,0.55); backdrop-filter:blur(6px); z-index:1002; justify-content:center; align-items:center;">
    <div class="atelier-card" style="max-width:680px; width:92%; padding:28px; background:white; position:relative; max-height:90vh; overflow-y:auto;">
      <button onclick="closeCompareModal()" style="position:absolute; top:16px; right:16px; background:none; border:none; font-size:22px; cursor:pointer; color:var(--ink-secondary);">&times;</button>
      <div class="editorial-label">Cognitive Contrast Analysis</div>
      <h3 class="editorial-h2" style="font-size:22px; margin-bottom:4px;">Compare Two Concepts</h3>
      <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:16px;">
        Select any two concepts from your learning tree. Gemini will generate side-by-side distinctions, similarities, and a knowledge-check question.
      </p>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:14px;">
        <div class="form-field">
          <label style="font-weight:700; font-size:11px; text-transform:uppercase;">Concept A</label>
          <select id="cmpConceptA" class="form-input"></select>
        </div>
        <div class="form-field">
          <label style="font-weight:700; font-size:11px; text-transform:uppercase;">Concept B</label>
          <select id="cmpConceptB" class="form-input"></select>
        </div>
      </div>

      <button class="btn-action-primary" style="width:100%; justify-content:center;" onclick="submitCompareConcepts()">
        Generate Comparative Analysis &rarr;
      </button>

      <!-- Results Container -->
      <div id="compareResultsArea" style="display:none; margin-top:20px; border-top:1px solid var(--border-parchment); padding-top:16px;">
        <div id="cmpOverviewText" style="font-size:14px; line-height:1.5; color:var(--ink-primary); margin-bottom:14px;"></div>
        
        <div class="compare-grid">
          <div class="compare-col">
            <strong style="color:var(--accent-celadon); font-size:13px;">Key Similarities:</strong>
            <ul id="cmpSimilaritiesList" style="margin-top:6px; font-size:12px; color:var(--ink-primary); padding-left:18px;"></ul>
          </div>
          <div class="compare-col">
            <strong style="color:var(--accent-terracotta); font-size:13px;">Important Differences:</strong>
            <ul id="cmpDifferencesList" style="margin-top:6px; font-size:12px; color:var(--ink-primary); padding-left:18px;"></ul>
          </div>
        </div>

        <div id="cmpTableWrap" style="margin:16px 0; overflow-x:auto;">
          <!-- Table dynamically injected -->
        </div>

        <div id="cmpCheckQuestionBox" style="background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm); padding:16px; margin-top:14px;">
          <div style="font-size:11px; font-weight:800; color:var(--accent-terracotta); text-transform:uppercase;">Concept Distinction Check</div>
          <div id="cmpQText" style="font-family:var(--font-editorial); font-size:16px; margin:6px 0 10px 0;"></div>
          <div id="cmpQOptions" style="display:flex; flex-direction:column; gap:6px;"></div>
          <div id="cmpQFeedback" style="display:none; margin-top:8px; font-size:12px; font-weight:700;"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Explain It Again Modal (During Animated Lessons) -->
  <div id="explainAgainModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(19,34,30,0.55); backdrop-filter:blur(6px); z-index:1002; justify-content:center; align-items:center;">
    <div class="atelier-card" style="max-width:540px; width:92%; padding:24px; background:white; position:relative; max-height:90vh; overflow-y:auto;">
      <button onclick="closeExplainAgainModal()" style="position:absolute; top:14px; right:14px; background:none; border:none; font-size:22px; cursor:pointer; color:var(--ink-secondary);">&times;</button>
      <div class="editorial-label">Adaptive AI Explanation</div>
      <h3 class="editorial-h2" style="font-size:20px; margin-bottom:4px;">Explain It Again</h3>
      <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:14px;">
        Choose how you would like the AI educator to re-explain this active scene:
      </p>

      <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:16px;">
        <label class="complexity-pill-btn" onclick="selectExplainMode('simpler', this)">
          <strong>Explain More Simply</strong>
          <div style="font-size:11px; color:var(--ink-secondary);">Crystal-clear, everyday vocabulary with zero confusing jargon</div>
        </label>
        <label class="complexity-pill-btn" onclick="selectExplainMode('step_by_step', this)">
          <strong>Explain Step by Step</strong>
          <div style="font-size:11px; color:var(--ink-secondary);">Sequential 1-2-3 logical steps showing cause and effect</div>
        </label>
        <label class="complexity-pill-btn" onclick="selectExplainMode('analogy', this)">
          <strong>Use a Real-World Analogy</strong>
          <div style="font-size:11px; color:var(--ink-secondary);">A memorable everyday metaphor that anchors the concept</div>
        </label>
        <label class="complexity-pill-btn" onclick="selectExplainMode('real_world', this)">
          <strong>Practical Application</strong>
          <div style="font-size:11px; color:var(--ink-secondary);">How this concept is used in real technology, nature, or engineering</div>
        </label>
        <label class="complexity-pill-btn" onclick="selectExplainMode('visual_focus', this)">
          <strong>Show Concept Visually Again</strong>
          <div style="font-size:11px; color:var(--ink-secondary);">Replays this scene animation with focused visual callouts</div>
        </label>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:10px;">
        <button class="btn-action-outline" onclick="closeExplainAgainModal()">Cancel</button>
        <button class="btn-action-primary" onclick="submitExplainAgainAction()">Generate Explanation &rarr;</button>
      </div>

      <div id="explainAgainResultBox" style="display:none; margin-top:16px; padding:14px; background:var(--surface-tinted); border:1px solid var(--border-parchment); border-radius:var(--radius-sm);">
        <div id="explainAgainText" style="font-size:13px; line-height:1.55; color:var(--ink-primary);"></div>
      </div>
    </div>
  </div>
"""

if "id=\"compareConceptsModal\"" not in html:
    html = html.replace('</body>', modals_html + '\n</body>', 1)
    print("Added Compare Concepts & Explain It Again Modals.")

# -------------------------------------------------------------
# 7. ADD "ASK THIS SCENE" AND "EXPLAIN IT AGAIN" BUTTONS TO STAGE
# -------------------------------------------------------------
studio_buttons_old = """          <div class="animated-controls-bar">
            <div style="display:flex; align-items:center; gap:8px;">
              <button class="btn-action-primary" id="btnAnimPlayPause" style="padding:8px 16px;" onclick="toggleAnimatedPlay()">
                <span id="btnAnimPlayIcon">-  Play</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="stepAnimatedScene(-1)" title="Previous Scene">
                <span>?r</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="stepAnimatedScene(1)" title="Next Scene">
                <span>?-</span>
              </button>
            </div>"""

studio_buttons_new = """          <div class="animated-controls-bar">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <button class="btn-action-primary" id="btnAnimPlayPause" style="padding:8px 16px;" onclick="toggleAnimatedPlay()">
                <span id="btnAnimPlayIcon">▶ Play</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="stepAnimatedScene(-1)" title="Previous Scene">
                <span>◀</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="stepAnimatedScene(1)" title="Next Scene">
                <span>▶</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px; border-color:var(--accent-surya); color:var(--ink-primary);" onclick="openAnimatedDoubtModal()" title="Ask question about active scene">
                <span>💬 Ask This Scene</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px; border-color:var(--accent-celadon); color:var(--ink-primary);" onclick="openExplainAgainModal()" title="Adaptive re-explanation">
                <span>💡 Explain It Again</span>
              </button>
              <button class="btn-action-outline" style="padding:8px 12px;" onclick="switchScreen('teachback')" title="Practice in Teach-Back">
                <span>🎓 Teach-Back</span>
              </button>
            </div>"""

if "Ask This Scene" not in html:
    html = re.sub(
        r'<div class="animated-controls-bar">\s*<div style="display:flex; align-items:center; gap:8px;">.*?</div>',
        studio_buttons_new,
        html,
        count=1,
        flags=re.DOTALL
    )
    print("Added Ask This Scene and Explain It Again buttons to stage controls.")

# -------------------------------------------------------------
# 8. REMOVE AGE-BASED NAVIGATION IN ANIMATED LIBRARY
# -------------------------------------------------------------
library_age_old = """      <!-- Filter by Profile -->
      <div style="display:flex; gap:8px; margin-bottom:16px; overflow-x:auto; padding-bottom:6px;">
        <button class="scene-pill-btn active" onclick="filterLibraryByProfile('all', this)">All Generations</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('child', this)">?? Children (5-12)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('teen', this)">?? Teenagers (13-17)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('university', this)">?? University (18-25)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('professional', this)">?? Professionals (26-59)</button>
        <button class="scene-pill-btn" onclick="filterLibraryByProfile('older_adult', this)">?? Older Adults (60+)</button>
      </div>"""

library_age_new = """      <!-- Search & Filters -->
      <div style="display:flex; gap:10px; margin-bottom:16px; align-items:center; flex-wrap:wrap;">
        <input type="text" id="librarySearchInput" class="form-input" placeholder="Search lessons by topic or subject..." style="max-width:320px; font-size:13px;" oninput="filterLibraryBySearch(this.value)">
        <select id="libraryLangFilter" class="form-input" style="max-width:180px; font-size:13px;" onchange="filterLibraryByLanguage(this.value)">
          <option value="all">All Languages</option>
          <option value="te">Telugu (తెలుగు)</option>
          <option value="en">English</option>
          <option value="hi">Hindi (हिन्दी)</option>
        </select>
      </div>"""

html = re.sub(
    r'<!-- Filter by Profile -->\s*<div style="display:flex; gap:8px; margin-bottom:16px;.*?</div>',
    library_age_new.strip(),
    html,
    flags=re.DOTALL
)
print("Replaced age filters in Library with search and language filters.")

# Write updated HTML
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished patching index.html HTML structure.")
