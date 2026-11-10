import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("\r\n", "\n")

# 1. Replace the Landing Page Duo Resonator with the Universal AI Visual Stage Preview
old_resonator = """        <!-- Acoustic Resonator Live Preview -->
        <div class="resonator-stage">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="editorial-label" style="margin-bottom:0;">Live Acoustic Stage</span>
            <span style="font-size:11px; font-weight:700; color:var(--ink-secondary);">Gnani Timbre 24kHz Linear PCM</span>
          </div>

          <div class="stage-hosts-duo">
            <!-- Host A -->
            <div class="host-resonator-card active-voice" id="lHostA">
              <div class="host-badge-row">
                <div class="host-avatar-initial avatar-yash">Y</div>
                <span style="font-size:10px; font-weight:800; text-transform:uppercase; color:var(--accent-terracotta);">Speaking Live</span>
              </div>
              <div style="font-weight:700; font-size:15px; margin-top:4px;">Host A ? Yash</div>
              <div style="font-size:11px; color:var(--ink-secondary);">Warm Explainer ? Shivani Voice</div>
              <div class="waveform-visualizer">
                <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
                <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
              </div>
            </div>

            <!-- Host B -->
            <div class="host-resonator-card host-priya" id="lHostB">
              <div class="host-badge-row">
                <div class="host-avatar-initial avatar-priya">P</div>
                <span style="font-size:10px; font-weight:800; text-transform:uppercase; color:var(--ink-subtle);">Listening</span>
              </div>
              <div style="font-weight:700; font-size:15px; margin-top:4px;">Host B ? Priya</div>
              <div style="font-size:11px; color:var(--ink-secondary);">Inquisitive Co-Host ? Yashraj Voice</div>
              <div class="waveform-visualizer">
                <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
                <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
              </div>
            </div>
          </div>

          <div style="background:var(--surface-tinted); border-radius:var(--radius-sm); padding:12px 16px; font-family:var(--font-editorial); font-size:15px; font-style:italic;">
            "Pod-Siksha ki swagatam! Chettu leaf lo solar energy ela chemical energy ga marutundo asalu epudaina alochinchara?"
          </div>
        </div>"""

new_resonator = """        <!-- Universal AI Animated Stage Live Preview -->
        <div class="resonator-stage" style="background:#13221E; border:2px solid var(--accent-surya); color:white; border-radius:var(--radius-md); padding:20px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:var(--accent-celadon); animation:pulse 1.5s infinite;"></span>
              <span class="editorial-label" style="color:var(--accent-surya); margin-bottom:0;">Universal AI Visual Stage</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:#CAD8D2;">Interactive Animated Explainer</span>
          </div>

          <div style="background:#1A342B; border:1px solid rgba(255,255,255,0.15); border-radius:var(--radius-sm); padding:18px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:1px; color:var(--accent-surya);">Scene 1 &middot; Core Visual Simulation</span>
              <span style="font-size:11px; color:#A4B5AD;">One AI Educator Narration</span>
            </div>
            <div style="font-family:var(--font-editorial); font-size:16px; font-style:italic; line-height:1.45; color:white;">
              "Let us observe how this principle operates in practice. Notice how each component transitions in sequence across the visual stage..."
            </div>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:#CAD8D2;">
            <span>Synchronized Subtitles &amp; Audio</span>
            <span style="color:var(--accent-celadon); font-weight:700;">&bull; Concept DNA Mapping Active</span>
          </div>
        </div>"""

html = re.sub(
    r'<!-- Acoustic Resonator Live Preview -->.*?</div>\s*</div>\s*</div>\s*<!-- The 10-Step Cognitive Learning Loop',
    new_resonator + '\n      </div>\n\n      <!-- The 10-Step Cognitive Learning Loop',
    html,
    flags=re.DOTALL
)

# 2. Update the cognitive loop steps to replace Two-Host Dialogue
html = html.replace(
    '<div class="loop-node-title">Two-Host Dialogue</div>\n            <p class="loop-node-desc">Host A &amp; B unpack concepts with natural questions and vivid metaphors.</p>',
    '<div class="loop-node-title">AI Animated Explainer</div>\n            <p class="loop-node-desc">One continuous AI educator unpacks concepts with dynamic animated simulations and vivid visual models.</p>'
)

html = html.replace(
    '<div class="loop-node-title">Two-Host Dialogue</div>\n            <p class="loop-node-desc">Host A & B unpack concepts with natural questions and vivid metaphors.</p>',
    '<div class="loop-node-title">AI Animated Explainer</div>\n            <p class="loop-node-desc">One continuous AI educator unpacks concepts with dynamic animated simulations and vivid visual models.</p>'
)

# 3. Clean learning journey modal description
html = html.replace(
    'Automatic text extraction &amp; 14-turn podcast generation',
    'Automatic multimodal concept extraction, dynamic visual animation, and personal knowledge tree synthesis'
)

html = html.replace(
    '14-turn 2-host audio dialogue, spoken TTS &amp; doubt clearance',
    'Interactive spoken dialogue, audio synthesis, and voice doubt clearance'
)

html = html.replace(
    ': \'Generating 14-Turn Socratic Podcast...\'',
    ': \'Generating Interactive Learning Journey...\''
)

html = html.replace(
    ': \'Gemini is crafting Host A & Host B dialogue and extracting Concept DNA.\'',
    ': \'Gemini is extracting concepts, planning the visual simulation, and building your knowledge tree.\''
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished cleaning legacy podcast presentation.")
