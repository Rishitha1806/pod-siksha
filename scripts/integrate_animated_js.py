"""
Appends the Universal AI Animated Learning JavaScript controller logic
before </script> in static/index.html.
"""

INDEX_PATH = r"C:\Users\jvris\Downloads\pod-siksha\static\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

JS_LOGIC = """
    // ==============================================================
    // UNIVERSAL AI ANIMATED LEARNING PLATFORM CONTROLLER
    // ==============================================================

    let animEngine = null;
    let currentAnimatedProjectId = null;
    let currentAnimatedProjectData = null;
    let currentActiveProfile = 'teen';

    function initAnimationEngine() {
      if (!animEngine) {
        animEngine = new UniversalAnimationEngine('animatedStageCanvas');
        
        animEngine.onSceneChange = (sceneIdx, scene) => {
          updateScenePillsUI(sceneIdx);
          updateStudioHeaderUI(scene);
          updateStoryboardSelectionUI(sceneIdx);
        };

        animEngine.onProgress = (curr, total, sceneIdx) => {
          const scrubber = document.getElementById('animTimelineScrubber');
          const timeCurr = document.getElementById('animTimeCurrent');
          const timeTot = document.getElementById('animTimeTotal');
          if (scrubber && total > 0) {
            scrubber.value = (curr / total) * 100;
          }
          if (timeCurr) {
            const m = Math.floor(curr / 60);
            const s = Math.floor(curr % 60);
            timeCurr.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
          }
          if (timeTot) {
            const m = Math.floor(total / 60);
            const s = Math.floor(total % 60);
            timeTot.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
          }
        };

        animEngine.onCheckpointTrigger = (scene, onComplete) => {
          showCheckpointOverlay(scene, onComplete);
        };

        animEngine.onPlaybackEnd = () => {
          const btn = document.getElementById('btnAnimPlayIcon');
          if (btn) btn.textContent = '▶ Replay';
          showToast('Lesson completed! Concepts recorded to your Sovereign DNA.');
        };
      }
    }

    async function loadActiveAnimatedProject(projectId) {
      initAnimationEngine();
      const token = AuthManager.authToken;
      const headers = token ? { "Authorization": "Bearer " + token } : {};

      try {
        let url = '/api/animated/projects';
        if (projectId) {
          url = `/api/animated/project/${projectId}`;
        }

        const resp = await fetch(url, { headers });
        if (!resp.ok) {
          console.warn('Could not fetch animated project:', resp.status);
          return;
        }

        let projData = null;
        if (projectId) {
          projData = await resp.json();
        } else {
          const list = await resp.json();
          if (list && list.length > 0) {
            const pId = list[0].id;
            const fullResp = await fetch(`/api/animated/project/${pId}`, { headers });
            if (fullResp.ok) projData = await fullResp.json();
          }
        }

        if (projData) {
          currentAnimatedProjectId = projData.id;
          currentAnimatedProjectData = projData;
          animEngine.loadProject(projData);

          // Populate Studio Header
          const titleEl = document.getElementById('animStudioTitle');
          if (titleEl) titleEl.textContent = projData.title || 'Interactive Visual Lesson';

          const profBadge = document.getElementById('animStudioProfileBadge');
          if (profBadge) profBadge.textContent = (projData.learner_profile || 'teen').toUpperCase();

          const langBadge = document.getElementById('animStudioLangBadge');
          if (langBadge) langBadge.textContent = (projData.language || 'te').toUpperCase();

          const styleBadge = document.getElementById('animStudioStyleBadge');
          if (styleBadge) styleBadge.textContent = (projData.animation_style || '2D').replace('_', ' ').toUpperCase();

          // Populate Scene Pills
          renderScenePills(projData.scenes || []);

          // Populate Storyboard List
          renderStoryboardList(projData.scenes || []);
        }
      } catch (err) {
        console.error('Error loading animated project:', err);
      }
    }

    function renderScenePills(scenes) {
      const container = document.getElementById('animScenePillsNav');
      if (!container) return;
      container.innerHTML = '';

      scenes.forEach((s, idx) => {
        const btn = document.createElement('button');
        btn.className = `scene-pill-btn ${idx === 0 ? 'active' : ''}`;
        btn.id = `animPillScene_${idx}`;
        btn.textContent = `Scene ${idx + 1}`;
        btn.onclick = () => jumpToAnimatedScene(idx);
        container.appendChild(btn);
      });
    }

    function updateScenePillsUI(activeIdx) {
      const container = document.getElementById('animScenePillsNav');
      if (!container) return;
      const pills = container.querySelectorAll('.scene-pill-btn');
      pills.forEach((p, idx) => {
        p.classList.toggle('active', idx === activeIdx);
      });
    }

    function updateStudioHeaderUI(scene) {
      const titleEl = document.getElementById('animStudioTitle');
      if (titleEl && scene) {
        titleEl.textContent = scene.title || currentAnimatedProjectData?.title || 'Interactive Lesson';
      }
    }

    function renderStoryboardList(scenes) {
      const listEl = document.getElementById('animStoryboardList');
      if (!listEl) return;
      listEl.innerHTML = '';

      scenes.forEach((s, idx) => {
        const card = document.createElement('div');
        card.id = `storyboardCard_${idx}`;
        card.style.cssText = 'padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-parchment); background:white; cursor:pointer; transition:all 0.2s;';
        card.onclick = () => jumpToAnimatedScene(idx);

        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:11px; font-weight:800; color:var(--accent-surya); text-transform:uppercase;">Scene ${idx + 1} · ${(s.animation_type || 'simulation').toUpperCase()}</span>
            <span style="font-size:11px; color:var(--ink-secondary); font-weight:600;">${s.duration_sec || 15}s</span>
          </div>
          <div style="font-weight:700; font-size:13px; color:var(--ink-primary); margin-bottom:4px;">${s.title || ''}</div>
          <div style="font-size:11px; color:var(--ink-secondary); line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
            ${s.narration_text || s.display_text || ''}
          </div>
        `;
        listEl.appendChild(card);
      });
    }

    function updateStoryboardSelectionUI(activeIdx) {
      const listEl = document.getElementById('animStoryboardList');
      if (!listEl) return;
      const cards = listEl.children;
      for (let i = 0; i < cards.length; i++) {
        if (i === activeIdx) {
          cards[i].style.borderColor = 'var(--accent-terracotta)';
          cards[i].style.background = '#FDF7F5';
        } else {
          cards[i].style.borderColor = 'var(--border-parchment)';
          cards[i].style.background = 'white';
        }
      }
    }

    function toggleAnimatedPlay() {
      if (!animEngine) return;
      const isNowPlaying = animEngine.togglePlay();
      const btn = document.getElementById('btnAnimPlayIcon');
      if (btn) btn.textContent = isNowPlaying ? '⏸ Pause' : '▶ Play';
    }

    function jumpToAnimatedScene(idx) {
      if (!animEngine) return;
      animEngine.jumpToScene(idx);
      const btn = document.getElementById('btnAnimPlayIcon');
      if (btn) btn.textContent = animEngine.isPlaying ? '⏸ Pause' : '▶ Play';
    }

    function stepAnimatedScene(delta) {
      if (!animEngine) return;
      const targetIdx = animEngine.currentSceneIndex + delta;
      if (targetIdx >= 0 && targetIdx < animEngine.scenes.length) {
        jumpToAnimatedScene(targetIdx);
      }
    }

    function seekAnimatedTimeline(percent) {
      if (!animEngine) return;
      const total = animEngine.sceneDuration || 15;
      const targetSec = (percent / 100) * total;
      animEngine.seek(targetSec);
    }

    // Interactive Checkpoint Overlay Handler
    function showCheckpointOverlay(scene, onComplete) {
      const overlay = document.getElementById('animCheckpointOverlay');
      const qText = document.getElementById('cpQuestionText');
      const optsList = document.getElementById('cpOptionsList');
      const feedback = document.getElementById('cpFeedbackBox');
      const continueBtn = document.getElementById('cpContinueBtn');

      if (!overlay || !scene.checkpoint_question) return;

      const cp = scene.checkpoint_question;
      qText.textContent = cp.question || 'Check your understanding:';
      optsList.innerHTML = '';
      feedback.style.display = 'none';
      continueBtn.style.display = 'none';

      const options = cp.options || [];
      const correctIdx = cp.correct_index ?? 0;

      options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'btn-action-outline';
        btn.style.cssText = 'padding:12px; text-align:left; justify-content:flex-start; font-size:13px; line-height:1.4;';
        btn.textContent = `${String.fromCharCode(65 + idx)}. ${opt}`;
        
        btn.onclick = () => {
          const isCorrect = (idx === correctIdx);
          feedback.style.display = 'block';
          if (isCorrect) {
            feedback.style.background = 'var(--accent-celadon-light)';
            feedback.style.color = '#1B5E20';
            feedback.style.border = '1px solid #C8E6C9';
            feedback.innerHTML = `<strong>✓ Correct!</strong> ${cp.explanation || 'Great comprehension.'}`;
          } else {
            feedback.style.background = 'var(--accent-danger-soft)';
            feedback.style.color = '#B71C1C';
            feedback.style.border = '1px solid #FFCDD2';
            feedback.innerHTML = `<strong>Explanation:</strong> ${cp.explanation || 'Review the scene concept.'}`;
          }

          // Record Checkpoint in Concept DNA
          recordAnimatedCheckpoint(scene.id, cp.question, idx, isCorrect);

          continueBtn.style.display = 'inline-flex';
          continueBtn.onclick = () => {
            overlay.style.display = 'none';
            if (onComplete) onComplete(isCorrect);
          };
        };
        optsList.appendChild(btn);
      });

      overlay.style.display = 'flex';
    }

    function closeCheckpointOverlay() {
      const overlay = document.getElementById('animCheckpointOverlay');
      if (overlay) overlay.style.display = 'none';
      if (animEngine) animEngine.advanceNextScene();
    }

    async function recordAnimatedCheckpoint(sceneId, question, selectedIdx, isCorrect) {
      if (!currentAnimatedProjectId) return;
      try {
        const token = AuthManager.authToken;
        await fetch(`/api/animated/project/${currentAnimatedProjectId}/checkpoint`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': 'Bearer ' + token } : {})
          },
          body: JSON.stringify({
            scene_id: sceneId,
            question: question,
            selected_idx: selectedIdx,
            is_correct: isCorrect
          })
        });
      } catch (e) {
        console.warn('Could not record checkpoint DNA:', e);
      }
    }

    // In-Video Socratic Ask Doubt
    function openAnimatedDoubtModal() {
      if (animEngine) animEngine.pause();
      const overlay = document.getElementById('animDoubtOverlay');
      if (overlay) {
        overlay.style.display = 'flex';
        document.getElementById('animDoubtInput').focus();
      }
    }

    function closeAnimatedDoubtModal() {
      const overlay = document.getElementById('animDoubtOverlay');
      if (overlay) overlay.style.display = 'none';
    }

    async function submitAnimatedDoubt() {
      const input = document.getElementById('animDoubtInput');
      const doubtText = input?.value?.trim();
      if (!doubtText) {
        showToast('Please type or speak your doubt first.');
        return;
      }

      const activeScene = animEngine ? animEngine.scenes[animEngine.currentSceneIndex] : null;
      if (!activeScene) return;

      const respBox = document.getElementById('animDoubtResponseBox');
      const ansText = document.getElementById('animDoubtAnswerText');
      if (respBox) respBox.style.display = 'block';
      if (ansText) ansText.textContent = 'AI Teacher is contemplating the visual mechanics...';

      try {
        const token = AuthManager.authToken;
        const res = await fetch(`/api/animated/scene/${activeScene.id}/ask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': 'Bearer ' + token } : {})
          },
          body: JSON.stringify({ doubt_text: doubtText })
        });

        if (res.ok) {
          const data = await res.json();
          if (ansText) ansText.textContent = data.answer_text || 'Understood.';
          
          // Play audio response if available
          if (data.audio_b64) {
            const snd = new Audio('data:audio/mp3;base64,' + data.audio_b64);
            snd.play().catch(() => {});
          }
        } else {
          if (ansText) ansText.textContent = 'Could not process question. Please try again.';
        }
      } catch (err) {
        if (ansText) ansText.textContent = 'Network error while contacting AI teacher.';
      }
    }

    // Video Export Trigger
    async function triggerVideoExport() {
      if (!animEngine) {
        showToast('Please load an animated lesson first.');
        return;
      }

      const btn = document.getElementById('btnExportText');
      const origText = btn ? btn.textContent : 'Export MP4 Video';
      if (btn) btn.textContent = 'Compiling Video...';

      showToast('Rendering high-fidelity animated video with narration audio...');

      try {
        const exportedFile = await animEngine.exportCurrentLessonVideo((sIdx, totalS, pct) => {
          if (btn) btn.textContent = `Scene ${sIdx + 1}/${totalS} (${Math.round(pct * 100)}%)`;
        });
        showToast(`Export complete! Saved ${exportedFile}`);
      } catch (err) {
        console.error('Export error:', err);
        showToast('Video export completed or fallback triggered.');
      } finally {
        if (btn) btn.textContent = origText;
      }
    }

    // Animated Creation Modal Controls
    function openAnimatedModal() {
      document.getElementById('newAnimatedModal').style.display = 'flex';
    }

    function closeAnimatedModal() {
      document.getElementById('newAnimatedModal').style.display = 'none';
    }

    function selectAudienceProfile(profKey) {
      currentActiveProfile = profKey;
      const input = document.getElementById('animModalProfileInput');
      if (input) input.value = profKey;

      const grid = document.getElementById('profileSelectGrid');
      if (grid) {
        const cards = grid.querySelectorAll('.profile-card-option');
        cards.forEach(c => {
          c.classList.toggle('selected', c.getAttribute('data-profile') === profKey);
        });
      }
    }

    async function submitNewAnimatedProject() {
      const title = document.getElementById('animModalTitleInput')?.value?.trim();
      const profile = document.getElementById('animModalProfileInput')?.value || 'teen';
      const lang = document.getElementById('animModalLangSelect')?.value || 'te';
      const style = document.getElementById('animModalStyleSelect')?.value || 'educational_2d';
      const contentText = document.getElementById('animModalContentText')?.value?.trim();
      const fileInput = document.getElementById('animModalFileInput');
      const file = fileInput?.files?.[0];

      if (!title && !contentText && !file) {
        showToast('Please enter a topic title, concept notes, or upload a document.');
        return;
      }

      const status = document.getElementById('animGeneratingStatus');
      const btn = document.getElementById('btnSubmitAnimated');
      if (status) status.style.display = 'block';
      if (btn) btn.disabled = true;

      const formData = new FormData();
      if (title) formData.append('title', title);
      formData.append('learner_profile', profile);
      formData.append('language', lang);
      formData.append('animation_style', style);
      if (contentText) formData.append('content_text', contentText);
      if (file) formData.append('file', file);

      try {
        const token = AuthManager.authToken;
        const res = await fetch('/api/animated/project', {
          method: 'POST',
          headers: token ? { 'Authorization': 'Bearer ' + token } : {},
          body: formData
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          showToast(errData.detail || 'Could not generate animated lesson.');
          return;
        }

        const project = await res.json();
        closeAnimatedModal();
        showToast(`Created Animated Lesson: "${project.title}"! Launching studio.`);
        switchScreen('animated-studio');
        loadActiveAnimatedProject(project.project_id || project.id);
      } catch (err) {
        console.error('Submission error:', err);
        showToast('Error communicating with generation engine.');
      } finally {
        if (status) status.style.display = 'none';
        if (btn) btn.disabled = false;
      }
    }

    // Animated Video Library Loader
    async function loadAnimatedProjectsList(profileFilter) {
      const container = document.getElementById('animatedLibraryGrid');
      if (!container) return;
      container.innerHTML = '<div style="color:var(--ink-secondary); font-size:13px;">Loading animated lessons...</div>';

      try {
        const token = AuthManager.authToken;
        const res = await fetch('/api/animated/projects', {
          headers: token ? { 'Authorization': 'Bearer ' + token } : {}
        });

        if (!res.ok) {
          container.innerHTML = '<div style="color:var(--ink-secondary); font-size:13px;">No animated lessons found. Create your first one above!</div>';
          return;
        }

        let projects = await res.json();
        if (profileFilter && profileFilter !== 'all') {
          projects = projects.filter(p => p.learner_profile === profileFilter);
        }

        if (!projects || projects.length === 0) {
          container.innerHTML = `
            <div style="grid-column: 1 / -1; padding:36px; text-align:center; background:white; border-radius:var(--radius-md); border:1px dashed var(--border-parchment);">
              <h3 style="font-size:18px; color:var(--ink-primary); margin-bottom:6px;">No animated lessons in this category yet</h3>
              <p style="font-size:13px; color:var(--ink-secondary); margin-bottom:14px;">Generate an educational video lesson tailored to this audience.</p>
              <button class="btn-action-primary" style="background:var(--accent-terracotta);" onclick="openAnimatedModal()">
                + Create Animated Lesson
              </button>
            </div>
          `;
          return;
        }

        container.innerHTML = '';
        projects.forEach(p => {
          const card = document.createElement('div');
          card.className = 'animated-lesson-card';
          
          card.innerHTML = `
            <div class="animated-thumb-stage">
              <div style="text-align:center;">
                <div style="font-size:32px; margin-bottom:4px;">🎬</div>
                <div style="font-size:11px; font-weight:800; letter-spacing:1px; text-transform:uppercase; color:var(--accent-surya);">
                  ${(p.animation_style || '2D').replace('_', ' ')}
                </div>
              </div>
              <span style="position:absolute; bottom:8px; right:8px; background:rgba(0,0,0,0.65); color:white; font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px;">
                ${p.total_scenes || 5} Scenes
              </span>
            </div>
            <div style="padding:16px; flex:1; display:flex; flex-direction:column; justify-content:space-between;">
              <div>
                <div style="display:flex; gap:6px; margin-bottom:8px; flex-wrap:wrap;">
                  <span class="profile-badge-pill" style="font-size:9px; padding:2px 6px;">
                    ${(p.learner_profile || 'teen').toUpperCase()}
                  </span>
                  <span class="profile-badge-pill" style="font-size:9px; padding:2px 6px; background:#FFF3E0; color:#E65100; border-color:#FFE0B2;">
                    ${(p.language || 'te').toUpperCase()}
                  </span>
                </div>
                <h4 style="font-family:var(--font-editorial); font-size:18px; color:var(--ink-primary); line-height:1.3; margin-bottom:6px;">
                  ${p.title || 'Animated Lesson'}
                </h4>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; pt:12px; border-top:1px solid var(--border-parchment);">
                <button class="btn-action-primary" style="padding:6px 14px; font-size:12px;" onclick="openProjectInStudio('${p.id}')">
                  ▶ Play Lesson
                </button>
                <button class="btn-action-outline" style="padding:6px 10px; font-size:12px; border-color:var(--border-parchment);" onclick="deleteAnimatedProject('${p.id}')" title="Delete">
                  🗑
                </button>
              </div>
            </div>
          `;
          container.appendChild(card);
        });
      } catch (err) {
        container.innerHTML = '<div style="color:var(--ink-secondary); font-size:13px;">Error loading animated library.</div>';
      }
    }

    function openProjectInStudio(projectId) {
      switchScreen('animated-studio');
      loadActiveAnimatedProject(projectId);
    }

    async function deleteAnimatedProject(projectId) {
      if (!confirm('Are you sure you want to delete this animated lesson?')) return;
      try {
        const token = AuthManager.authToken;
        await fetch(`/api/animated/project/${projectId}`, {
          method: 'DELETE',
          headers: token ? { 'Authorization': 'Bearer ' + token } : {}
        });
        showToast('Lesson deleted.');
        loadAnimatedProjectsList();
      } catch (e) {
        showToast('Could not delete lesson.');
      }
    }

    function filterLibraryByProfile(profileKey, btnEl) {
      const buttons = btnEl.parentElement.querySelectorAll('.scene-pill-btn');
      buttons.forEach(b => b.classList.remove('active'));
      btnEl.classList.add('active');
      loadAnimatedProjectsList(profileKey);
    }

    // Keyboard Spacebar Shortcut for In-Video Play/Pause or Doubt
    window.addEventListener('keydown', (e) => {
      const activeScreen = window.location.hash.replace('#', '');
      if (activeScreen === 'animated-studio' && e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        toggleAnimatedPlay();
      }
    });
"""

# Insert before </script>
if "UniversalAnimationEngine" not in content:
    content = content.replace("</script>", JS_LOGIC + "\n  </script>", 1)
    print("Appended Animated Learning JavaScript controller.")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html fully updated!")
