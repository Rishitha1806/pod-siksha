import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("\r\n", "\n")

# 1. Clean the banner in view-home to remove age-groups
old_banner_text = """From Children (5?12) to Older Adults (60+), understand complex concepts through dynamic 60fps simulations, synchronized voice narration, and in-video Socratic Q&amp;A."""
new_banner_text = """One continuous AI educator. Every subject. Every language. Understand complex concepts through dynamic simulations, synchronized voice narration, contextual doubt resolution, and a personal Concept DNA knowledge tree."""

html = re.sub(
    r'From Children.*?in-video Socratic Q&amp;A\.',
    new_banner_text,
    html,
    flags=re.DOTALL
)

# Remove 5 Generations line
html = re.sub(
    r'<div style="font-size:12px; color:#A4B5AD;">\s*<strong style="color:white;">5 Generations:</strong>.*?</div>',
    '',
    html,
    flags=re.DOTALL
)

# 2. Remove hardcoded dummy cards in recentJourneysList
old_journeys_list = """            <div id="recentJourneysList"><div class="journey-tile" onclick="switchScreen('studio')">
              <div>
                <div style="font-weight:700; font-size:15px;">Photosynthesis and Cellular Energetics</div>
                <div style="font-size:12px; color:var(--ink-secondary); margin-top:2px;">14 Turns ? Telugu ? 78% Concept Mastery ? Active</div>
              </div>
              <span style="font-size:13px; font-weight:700; color:var(--accent-terracotta);">Continue &rarr;</span>
            </div>

            <div class="journey-tile" onclick="switchScreen('workspace')">
              <div>
                <div style="font-weight:700; font-size:15px;">Quadratic Equations Class 10</div>
                <div style="font-size:12px; color:var(--ink-secondary); margin-top:2px;">14 Turns ? Telugu-English ? 92% Concept Mastery</div>
              </div>
              <span style="font-size:13px; font-weight:700; color:var(--ink-secondary);">Workspace &rarr;</span>
            </div>

            <div class="journey-tile" onclick="switchScreen('insights')">
              <div>
                <div style="font-weight:700; font-size:15px;">Science of Happiness &amp; Well-being</div>
                <div style="font-size:12px; color:var(--ink-secondary); margin-top:2px;">14 Turns ? Telugu ? 4 Completed Quizzes</div>
              </div>
              <span style="font-size:13px; font-weight:700; color:var(--ink-secondary);">Insights &rarr;</span>
            </div>
          </div>"""

new_journeys_list = """            <div id="recentJourneysList">
              <div class="empty-state-atelier" style="margin:8px 0; padding:32px 20px;">
                <div class="empty-glyph">🌱</div>
                <h3 class="editorial-h2" style="font-size:20px; margin-bottom:6px;">Your learning journey starts here</h3>
                <p style="font-size:13px; color:var(--ink-secondary); max-width:380px; margin:0 auto 14px auto;">
                  Enter any topic or upload a study document to begin your interactive visual learning.
                </p>
                <button class="btn-action-primary" style="font-size:13px; padding:8px 16px;" onclick="openAnimatedModal()">+ Start First Learning Journey</button>
              </div>
            </div>"""

if old_journeys_list in html:
    html = html.replace(old_journeys_list, new_journeys_list, 1)
    print("Replaced hardcoded recentJourneysList with honest empty state.")
else:
    # Use regex replacement
    html = re.sub(
        r'<div id="recentJourneysList">.*?</div>\s*</div>\s*</div>\s*</div>\s*<!-- Right: Daily Cognitive Pulse',
        new_journeys_list + '\n        </div>\n        </div>\n        <!-- Right: Daily Cognitive Pulse',
        html,
        flags=re.DOTALL
    )
    print("Replaced recentJourneysList via regex.")

# 3. Update loadJourneys to route to Animated Studio
old_load_journeys = """        const first = journeys[0];
        currentSessionId = first.id;
        const heroTitle = document.getElementById("heroResumeTitle");
        const heroSub = document.getElementById("heroResumeSub");
        const heroBtn = document.getElementById("heroResumeBtn");
        if (heroTitle) heroTitle.innerText = first.title;
        if (heroSub) heroSub.innerText = `${first.language.toUpperCase()} Narration   ${first.total_turns || 14} Turns   ${first.doubt_count || 0} Doubts Recorded`;
        if (heroBtn) heroBtn.onclick = () => { loadStudioSession(first.id); switchScreen("studio"); };

        let html = "";
        journeys.slice(0, 5).forEach(j => {
          html += `
            <div class="journey-tile" style="margin-top:10px;">
              <div style="flex:1; cursor:pointer;" onclick="loadStudioSession('${j.id}'); switchScreen('studio');">
                <div style="font-weight:700; font-size:15px; color:var(--ink-primary);">${j.title}</div>
                <div style="font-size:12px; color:var(--ink-secondary); margin-top:2px;">
                  ${j.total_turns || 14} Turns   ${j.language.toUpperCase()}   ${j.doubt_count || 0} Doubts   Created ${new Date(j.created_at).toLocaleDateString()}
                </div>
              </div>
              <div style="display:flex; gap:8px;">
                <button class="btn-action-primary" style="padding:4px 10px; font-size:11px;" onclick="loadStudioSession('${j.id}'); switchScreen('studio');">Resume &rarr;</button>
              </div>
            </div>
          `;
        });
        listEl.innerHTML = html;"""

new_load_journeys = """        const first = journeys[0];
        const heroCard = document.querySelector('.atelier-home-grid .hero-resume-card');
        const heroTitle = document.getElementById("heroResumeTitle");
        const heroSub = document.getElementById("heroResumeSub");
        const heroBtn = document.getElementById("heroResumeBtn");

        if (first) {
          if (heroCard) heroCard.style.display = 'block';
          if (heroTitle) heroTitle.innerText = first.title;
          if (heroSub) heroSub.innerText = `${(first.language || 'en').toUpperCase()} Narration • ${first.total_turns || 5} Scenes • AI Animated Educator`;
          if (heroBtn) {
            heroBtn.innerText = "Resume Animated Lesson →";
            heroBtn.onclick = () => {
              loadActiveAnimatedProject(first.id);
              switchScreen("animated-studio");
            };
          }
        } else {
          if (heroCard) heroCard.style.display = 'none';
        }

        let html = "";
        journeys.slice(0, 5).forEach(j => {
          html += `
            <div class="journey-tile" style="margin-top:10px;">
              <div style="flex:1; cursor:pointer;" onclick="loadActiveAnimatedProject('${j.id}'); switchScreen('animated-studio');">
                <div style="font-weight:700; font-size:15px; color:var(--ink-primary);">${j.title}</div>
                <div style="font-size:12px; color:var(--ink-secondary); margin-top:2px;">
                  ${j.total_turns || 5} Scenes • ${(j.language || 'en').toUpperCase()} • Visual Simulation • Created ${new Date(j.created_at).toLocaleDateString()}
                </div>
              </div>
              <div style="display:flex; gap:8px;">
                <button class="btn-action-primary" style="padding:6px 12px; font-size:12px;" onclick="loadActiveAnimatedProject('${j.id}'); switchScreen('animated-studio');">Open Lesson &rarr;</button>
              </div>
            </div>
          `;
        });
        listEl.innerHTML = html;"""

if old_load_journeys in html:
    html = html.replace(old_load_journeys, new_load_journeys, 1)
    print("Updated loadJourneys to link directly to Animated Studio.")
else:
    # Use regex replacement
    html = re.sub(
        r'const first = journeys\[0\];.*?listEl\.innerHTML = html;',
        new_load_journeys.strip(),
        html,
        flags=re.DOTALL
    )
    print("Updated loadJourneys via regex.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished cleaning home and library.")
