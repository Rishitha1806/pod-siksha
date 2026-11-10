import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("\r\n", "\n")

# Replace the generation profile grid with complexity
old_gen_grid = """        <!-- Step 1: Learner Generation Profile -->
        <div class="form-field" style="margin-bottom:18px;">
          <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:var(--ink-primary); margin-bottom:8px; display:block;">
            1. Target Generation &amp; Learner Profile
          </label>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(110px, 1fr)); gap:10px;" id="profileSelectGrid">
            <div class="profile-card-option" data-profile="child" onclick="selectAudienceProfile('child')">
              <span style="font-size:22px;">??</span>
              <span style="font-size:12px; font-weight:700;">Child</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 5-12</span>
            </div>
            <div class="profile-card-option selected" data-profile="teen" onclick="selectAudienceProfile('teen')">
              <span style="font-size:22px;">??</span>
              <span style="font-size:12px; font-weight:700;">Teen</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 13-17</span>
            </div>
            <div class="profile-card-option" data-profile="university" onclick="selectAudienceProfile('university')">
              <span style="font-size:22px;">??</span>
              <span style="font-size:12px; font-weight:700;">University</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 18-25</span>
            </div>
            <div class="profile-card-option" data-profile="professional" onclick="selectAudienceProfile('professional')">
              <span style="font-size:22px;">??</span>
              <span style="font-size:12px; font-weight:700;">Professional</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 26-59</span>
            </div>
            <div class="profile-card-option" data-profile="older_adult" onclick="selectAudienceProfile('older_adult')">
              <span style="font-size:22px;">??</span>
              <span style="font-size:12px; font-weight:700;">Older Adult</span>
              <span style="font-size:10px; color:var(--ink-secondary);">Ages 60+</span>
            </div>
          </div>
          <input type="hidden" id="animModalProfileInput" value="teen">
        </div>"""

new_complexity_grid = """        <!-- Step 1: Explanation Complexity & Pedagogical Depth -->
        <div class="form-field" style="margin-bottom:18px;">
          <label style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:var(--ink-primary); margin-bottom:8px; display:block;">
            1. Explanation Complexity &amp; Depth
          </label>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px;" id="profileSelectGrid">
            <div class="profile-card-option" data-profile="beginner" onclick="selectExplanationComplexity('beginner')">
              <span style="font-size:20px;">🌱</span>
              <span style="font-size:13px; font-weight:700;">Beginner</span>
              <span style="font-size:11px; color:var(--ink-secondary);">Visual analogies &amp; fundamentals</span>
            </div>
            <div class="profile-card-option selected" data-profile="intermediate" onclick="selectExplanationComplexity('intermediate')">
              <span style="font-size:20px;">🌿</span>
              <span style="font-size:13px; font-weight:700;">Intermediate</span>
              <span style="font-size:11px; color:var(--ink-secondary);">Balanced depth &amp; step-by-step</span>
            </div>
            <div class="profile-card-option" data-profile="advanced" onclick="selectExplanationComplexity('advanced')">
              <span style="font-size:20px;">🌳</span>
              <span style="font-size:13px; font-weight:700;">Advanced</span>
              <span style="font-size:11px; color:var(--ink-secondary);">Rigorous technical derivations</span>
            </div>
          </div>
          <input type="hidden" id="animModalProfileInput" value="intermediate">
        </div>"""

if old_gen_grid in html:
    html = html.replace(old_gen_grid, new_complexity_grid, 1)
    print("Replaced generation profile grid with complexity.")
else:
    # Use regex replacement
    html = re.sub(
        r'<!-- Step 1: Learner Generation Profile -->.*?<input type="hidden" id="animModalProfileInput" value="[^"]*">\s*</div>',
        new_complexity_grid.strip(),
        html,
        flags=re.DOTALL
    )
    print("Replaced generation profile grid via regex.")

# Add selectExplanationComplexity JS function
js_complexity = """
    function selectExplanationComplexity(lvl) {
      document.querySelectorAll('#profileSelectGrid .profile-card-option').forEach(el => {
        el.classList.remove('selected');
        if (el.getAttribute('data-profile') === lvl) el.classList.add('selected');
      });
      const input = document.getElementById('animModalProfileInput');
      if (input) input.value = lvl;
    }
    // Backward compatibility alias
    function selectAudienceProfile(p) { selectExplanationComplexity(p); }
"""

if "function selectExplanationComplexity" not in html:
    html = html.replace('</script>\n</body>', js_complexity + '\n</script>\n</body>', 1)
    print("Added selectExplanationComplexity JS function.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished modal complexity cleanup.")
