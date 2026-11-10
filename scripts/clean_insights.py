import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("\r\n", "\n")

# Replace hardcoded concept tracks with empty state
clean_tracks = """          <div id="conceptTracksContainer">
            <div class="empty-state-atelier" style="margin:8px 0; padding:32px 20px;">
              <div class="empty-glyph">📊</div>
              <h3 class="editorial-h2" style="font-size:18px; margin-bottom:4px;">No Learning Telemetry Yet</h3>
              <p style="font-size:12px; color:var(--ink-secondary); max-width:320px; margin:0 auto 12px auto;">
                Complete your first animated lesson to see your mastery matrix and concept progress.
              </p>
              <button class="btn-action-primary" style="font-size:12px; padding:6px 14px;" onclick="openAnimatedModal()">+ Start First Lesson</button>
            </div>
          </div>"""

html = re.sub(
    r'<div id="conceptTracksContainer">.*?</div>\s*</div>\s*</div></div>\s*<!-- Right: Misconception Radar',
    clean_tracks + '\n        </div></div>\n        <!-- Right: Misconception Radar',
    html,
    flags=re.DOTALL
)

# Replace hardcoded misconception radar
clean_misconceptions = """            <div id="misconceptionRadarContainer">
              <div style="font-size:12px; color:var(--ink-secondary); padding:16px; background:var(--surface-tinted); border-radius:var(--radius-sm); text-align:center;">
                No misconceptions diagnosed in your learning history. Excellent comprehension!
              </div>
            </div>"""

html = re.sub(
    r'<div id="misconceptionRadarContainer">.*?</div>\s*</div>\s*</div>\s*<!-- Memory Loop Queue',
    clean_misconceptions + '\n          </div>\n          <!-- Memory Loop Queue',
    html,
    flags=re.DOTALL
)

# Replace hardcoded memory loop
clean_memory_loop = """            <div id="memoryLoopContainer" style="display:flex; flex-direction:column; gap:10px; margin-top:14px;">
              <div style="font-size:12px; color:var(--ink-secondary); padding:16px; background:var(--surface-tinted); border-radius:var(--radius-sm); text-align:center;">
                All concept recall touchpoints are clear. Check back after quizzes or lessons.
              </div>
            </div>"""

html = re.sub(
    r'<div id="memoryLoopContainer"[^>]*>.*?</div>\s*</div>\s*</div>\s*</div>\s*</section>\s*<!-- ==============================================================\s*6\. LEARNING STUDIO',
    clean_memory_loop + '\n          </div>\n        </div>\n      </div>\n    </section>\n\n    <!-- ==============================================================\n         6. LEARNING STUDIO',
    html,
    flags=re.DOTALL
)

# Replace initial 78% in score ring with "--"
html = html.replace('<span id="insightsMasteryRingScore" class="ring-center-score">78%</span>', '<span id="insightsMasteryRingScore" class="ring-center-score">--</span>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished cleaning insights dummy data.")
