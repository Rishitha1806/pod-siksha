/**
 * Pod-Siksha 2.0 — Universal AI Animated Learning Engine
 * High-performance 60fps HTML5 Canvas simulation renderer with 8 core pedagogical
 * domains, audio synchronization, interactive checkpoints, and client-side video export.
 */

class UniversalAnimationEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) {
      console.warn('Animation canvas not found: ' + canvasId);
      return;
    }
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width = 1280;
    this.height = this.canvas.height = 720;
    
    // Project and Playback State
    this.project = null;
    this.scenes = [];
    this.currentSceneIndex = 0;
    this.isPlaying = false;
    this.sceneStartTime = 0;
    this.sceneDuration = 15; // default 15s
    this.currentTime = 0;
    this.animationFrameId = null;
    
    // Audio Player
    this.audioPlayer = new Audio();
    this.audioPlayer.volume = 1.0;
    this.audioPreloadCache = {};
    
    // Subtitles & Synchronized Teleprompter
    this.currentSubtitles = [];
    this.activeSubtitleText = '';
    this.activeSubtitleIndex = -1;
    
    // Video Recording / Export State
    this.isExporting = false;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    
    // Domain particle pools
    this.particles = [];
    this.initParticles();
    
    // Callbacks
    this.onSceneChange = null;
    this.onProgress = null;
    this.onCheckpointTrigger = null;
    this.onPlaybackEnd = null;

    // Attach Audio Listeners
    this.audioPlayer.addEventListener('ended', () => this.handleAudioEnded());
    this.audioPlayer.addEventListener('timeupdate', () => this.handleAudioTimeUpdate());
    this.audioPlayer.addEventListener('error', (e) => {
      console.warn('Audio playback error or fallback:', e);
    });
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < 90; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        size: Math.random() * 3 + 1.5,
        alpha: Math.random() * 0.7 + 0.2,
        phase: Math.random() * Math.PI * 2,
        color: '#FF9F1C'
      });
    }
  }

  loadProject(projectData) {
    this.project = projectData;
    this.scenes = projectData.scenes || [];
    this.currentSceneIndex = 0;
    this.currentTime = 0;
    if (this.scenes.length > 0) {
      this.prepareScene(0);
    }
    this.renderFrame(0);
  }

  prepareScene(index) {
    if (index < 0 || index >= this.scenes.length) return;
    this.currentSceneIndex = index;
    const scene = this.scenes[index];
    this.sceneDuration = scene.duration_sec || 15;
    this.currentTime = 0;
    this.sceneStartTime = performance.now();
    this.currentSubtitles = scene.subtitles || [];
    this.activeSubtitleText = scene.narration_text || '';

    // Load scene narration audio
    const audioUrl = `/api/animated/scene/${scene.id}/audio`;
    if (this.audioPlayer.src !== window.location.origin + audioUrl) {
      this.audioPlayer.src = audioUrl;
      this.audioPlayer.load();
    }

    // Preload next scene audio
    if (index + 1 < this.scenes.length) {
      const nextId = this.scenes[index + 1].id;
      if (!this.audioPreloadCache[nextId]) {
        const preImg = new Audio();
        preImg.src = `/api/animated/scene/${nextId}/audio`;
        this.audioPreloadCache[nextId] = preImg;
      }
    }

    if (this.onSceneChange) {
      this.onSceneChange(this.currentSceneIndex, scene);
    }
  }

  play() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.sceneStartTime = performance.now() - (this.currentTime * 1000);
    
    // Attempt audio play
    this.audioPlayer.currentTime = this.currentTime;
    const playPromise = this.audioPlayer.play();
    if (playPromise !== undefined) {
      playPromise.catch(err => {
        console.warn('Audio auto-play policy prevented direct audio, running silent visual loop:', err);
      });
    }

    this.startLoop();
  }

  pause() {
    this.isPlaying = false;
    this.audioPlayer.pause();
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
    return this.isPlaying;
  }

  seek(timeInSec) {
    this.currentTime = Math.max(0, Math.min(this.sceneDuration, timeInSec));
    this.sceneStartTime = performance.now() - (this.currentTime * 1000);
    if (this.audioPlayer.duration) {
      this.audioPlayer.currentTime = this.currentTime;
    }
    this.renderFrame(this.currentTime);
  }

  jumpToScene(sceneIndex) {
    const wasPlaying = this.isPlaying;
    this.pause();
    this.prepareScene(sceneIndex);
    if (wasPlaying) {
      this.play();
    } else {
      this.renderFrame(0);
    }
  }

  handleAudioTimeUpdate() {
    if (this.isPlaying && this.audioPlayer.currentTime > 0) {
      this.currentTime = this.audioPlayer.currentTime;
    }
  }

  handleAudioEnded() {
    this.onSceneCompleted();
  }

  onSceneCompleted() {
    const currentScene = this.scenes[this.currentSceneIndex];
    
    // Check if there is an interactive checkpoint question
    if (currentScene && currentScene.checkpoint_question && !currentScene._checkpointAnswered) {
      this.pause();
      if (this.onCheckpointTrigger) {
        this.onCheckpointTrigger(currentScene, (answeredCorrectly) => {
          currentScene._checkpointAnswered = true;
          this.advanceNextScene();
        });
        return;
      }
    }

    this.advanceNextScene();
  }

  advanceNextScene() {
    if (this.currentSceneIndex + 1 < this.scenes.length) {
      this.prepareScene(this.currentSceneIndex + 1);
      if (this.isPlaying) {
        this.audioPlayer.play().catch(() => {});
      }
    } else {
      // Reached end of project
      this.pause();
      if (this.onPlaybackEnd) {
        this.onPlaybackEnd();
      }
    }
  }

  startLoop() {
    const loop = (timestamp) => {
      if (!this.isPlaying) return;

      if (!this.audioPlayer.paused && this.audioPlayer.currentTime > 0) {
        this.currentTime = this.audioPlayer.currentTime;
      } else {
        this.currentTime = (timestamp - this.sceneStartTime) / 1000;
      }

      if (this.currentTime >= this.sceneDuration) {
        this.onSceneCompleted();
        return;
      }

      this.renderFrame(this.currentTime);

      if (this.onProgress) {
        this.onProgress(this.currentTime, this.sceneDuration, this.currentSceneIndex);
      }

      this.animationFrameId = requestAnimationFrame(loop);
    };

    if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId);
    this.animationFrameId = requestAnimationFrame(loop);
  }

  renderFrame(t) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const scene = this.scenes[this.currentSceneIndex];
    if (!scene) return;

    const animType = (scene.animation_type || 'circulation').toLowerCase();
    const spec = scene.visual_spec || {};
    const theme = (spec.theme || 'educational_2d').toLowerCase();

    // 1. Draw Canvas Backdrop
    this.drawBackground(ctx, w, h, theme, t);

    // 2. Dispatch to Domain-Specific Simulation Renderer
    ctx.save();
    switch (animType) {
      case 'circulation':
        this.renderCirculation(ctx, w, h, spec, t);
        break;
      case 'force_vectors':
        this.renderForceVectors(ctx, w, h, spec, t);
        break;
      case 'equation_transform':
        this.renderEquationTransform(ctx, w, h, spec, t);
        break;
      case 'molecular_reaction':
        this.renderMolecularReaction(ctx, w, h, spec, t);
        break;
      case 'sorting_algorithm':
        this.renderSortingAlgorithm(ctx, w, h, spec, t);
        break;
      case 'cycle_loop':
        this.renderCycleLoop(ctx, w, h, spec, t);
        break;
      case 'growth_curve':
        this.renderGrowthCurve(ctx, w, h, spec, t);
        break;
      case 'step_tutorial':
        this.renderStepTutorial(ctx, w, h, spec, t);
        break;
      default:
        this.renderGenericDiagram(ctx, w, h, spec, t);
        break;
    }
    ctx.restore();

    // 3. Render Top HUD: Scene Banner & Concept Pills
    this.renderTopHUD(ctx, w, h, scene, t);

    // 4. Render Teleprompter & Live Synchronized Subtitles
    this.renderSubtitlesHUD(ctx, w, h, scene, t);
  }

  drawBackground(ctx, w, h, theme, t) {
    if (theme === 'simulation' || theme === 'infographic') {
      // Cosmic Emerald-Black deep theater gradient
      const bgGrad = ctx.createLinearGradient(0, 0, w, h);
      bgGrad.addColorStop(0, '#101B18');
      bgGrad.addColorStop(1, '#080E0C');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      // Celestial coordinate grid
      ctx.strokeStyle = 'rgba(82, 130, 113, 0.12)';
      ctx.lineWidth = 1;
      const step = 48;
      for (let x = 0; x < w; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }
    } else if (theme === 'whiteboard') {
      // Clean ivory sketch whiteboard with subtle paper grain
      ctx.fillStyle = '#FCFBF8';
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = 'rgba(19, 34, 30, 0.05)';
      ctx.lineWidth = 1;
      for (let y = 60; y < h; y += 40) {
        ctx.beginPath();
        ctx.moveTo(40, y);
        ctx.lineTo(w - 40, y);
        ctx.stroke();
      }
    } else {
      // Aura Atelier Museum Parchment with warm celestial vignette
      const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 80, w / 2, h / 2, 750);
      bgGrad.addColorStop(0, '#FDFBF7');
      bgGrad.addColorStop(1, '#F3EFE6');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      // Subtle border framing
      ctx.strokeStyle = 'rgba(232, 225, 213, 0.9)';
      ctx.lineWidth = 3;
      ctx.strokeRect(16, 16, w - 32, h - 32);
    }
  }

  renderTopHUD(ctx, w, h, scene, t) {
    // Scene Order Pill & Title
    ctx.save();
    ctx.fillStyle = 'rgba(19, 34, 30, 0.85)';
    this.roundRect(ctx, 36, 32, 380, 56, 12, true, false);

    // Surya Gold Accent Dot
    ctx.fillStyle = '#FF9F1C';
    ctx.beginPath();
    ctx.arc(58, 60, 6, 0, Math.PI * 2);
    ctx.fill();

    // Scene Label
    ctx.fillStyle = '#FF9F1C';
    ctx.font = '700 12px "Plus Jakarta Sans", sans-serif';
    ctx.fillText(`SCENE ${scene.scene_index || (this.currentSceneIndex + 1)} OF ${this.scenes.length}`, 74, 52);

    // Scene Title
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 16px "Newsreader", Georgia, serif';
    const cleanTitle = (scene.title || 'Interactive Visual Lesson').substring(0, 32);
    ctx.fillText(cleanTitle, 74, 73);

    // Visual Type Badge (Top Right)
    const animTypeLabel = (scene.animation_type || 'simulation').toUpperCase();
    ctx.fillStyle = 'rgba(82, 130, 113, 0.9)';
    this.roundRect(ctx, w - 240, 32, 204, 38, 8, true, false);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 12px "Plus Jakarta Sans", sans-serif';
    ctx.fillText(`ENGINE: ${animTypeLabel}`, w - 224, 56);

    ctx.restore();
  }

  renderSubtitlesHUD(ctx, w, h, scene, t) {
    // Teleprompter / Subtitles banner at bottom of stage
    ctx.save();
    const boxY = h - 110;
    const boxH = 76;
    
    // Glassmorphic banner
    ctx.fillStyle = 'rgba(19, 34, 30, 0.92)';
    this.roundRect(ctx, 48, boxY, w - 96, boxH, 16, true, false);
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Sound wave icon
    ctx.fillStyle = '#FF9F1C';
    for (let bar = 0; bar < 4; bar++) {
      const barH = 8 + Math.sin(t * 8 + bar) * 10;
      ctx.fillRect(72 + bar * 6, boxY + 38 - barH / 2, 3, barH);
    }

    // Determine current subtitle segment
    let displayCaption = scene.narration_text || '';
    let englishHint = scene.display_text || '';

    // If subtitles array available, match active segment
    if (this.currentSubtitles && this.currentSubtitles.length > 0) {
      const match = this.currentSubtitles.find(s => t >= s.start && t <= s.end);
      if (match) {
        displayCaption = match.text;
      }
    }

    // Render Native Spoken Subtitle (Primary)
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '600 18px "Plus Jakarta Sans", sans-serif';
    ctx.fillText(displayCaption.substring(0, 95), 108, boxY + 34);

    // Render English Teleprompter / Conceptual Hint (Secondary)
    if (englishHint) {
      ctx.fillStyle = '#CAD8D2';
      ctx.font = '500 13px "Plus Jakarta Sans", sans-serif';
      ctx.fillText(englishHint.substring(0, 110), 108, boxY + 56);
    }

    ctx.restore();
  }

  // ==============================================================
  // 1. BIOLOGY & FLUID DYNAMICS (Circulation)
  // ==============================================================
  renderCirculation(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    // Pulse heartbeat scale rhythm (systole & diastole)
    const pulse = 1 + 0.045 * Math.sin(t * 4.5) * (Math.sin(t * 4.5) > 0 ? 1.2 : 0.6);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(pulse, pulse);

    // Left & Right Heart Chamber Envelopes
    // Right side (Deoxygenated - Blue #2E5BFF)
    ctx.fillStyle = 'rgba(46, 91, 255, 0.18)';
    ctx.strokeStyle = '#2E5BFF';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(-110, 0, 120, 160, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Left side (Oxygenated - Terracotta Red #E05A47)
    ctx.fillStyle = 'rgba(224, 90, 71, 0.18)';
    ctx.strokeStyle = '#E05A47';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(110, 0, 120, 160, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Central Septum Divider
    ctx.strokeStyle = 'rgba(19, 34, 30, 0.4)';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(0, -150);
    ctx.lineTo(0, 150);
    ctx.stroke();

    // Four Chambers Labels
    const chambers = [
      { name: 'Right Atrium (RA)', x: -110, y: -70, color: '#2E5BFF' },
      { name: 'Right Ventricle (RV)', x: -110, y: 70, color: '#2E5BFF' },
      { name: 'Left Atrium (LA)', x: 110, y: -70, color: '#E05A47' },
      { name: 'Left Ventricle (LV)', x: 110, y: 70, color: '#E05A47' }
    ];

    chambers.forEach(ch => {
      ctx.fillStyle = ch.color;
      ctx.beginPath();
      ctx.arc(ch.x, ch.y, 24, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#FFFFFF';
      ctx.font = '700 13px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(ch.name.split(' ')[0], ch.x, ch.y - 32);
    });

    // Tricuspid & Bicuspid Valves Opening & Closing
    const valveOpen = Math.sin(t * 4.5) > 0.1;
    ctx.strokeStyle = '#FF9F1C';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(-130, 0);
    ctx.lineTo(-90, valveOpen ? 18 : 0);
    ctx.moveTo(90, 0);
    ctx.lineTo(130, valveOpen ? 18 : 0);
    ctx.stroke();

    ctx.restore();

    // Flowing Blood Cells / Oxygen Particles along Conduits
    for (let i = 0; i < 28; i++) {
      const progress = ((t * 0.4) + (i / 28)) % 1;
      const angle = progress * Math.PI * 2;
      const rx = 240;
      const ry = 190;
      const px = cx + Math.cos(angle) * rx;
      const py = cy + Math.sin(angle) * ry;

      const isOxygenated = px > cx;
      ctx.fillStyle = isOxygenated ? '#E05A47' : '#2E5BFF';
      ctx.beginPath();
      ctx.arc(px, py, 6 + Math.sin(t * 3 + i) * 2, 0, Math.PI * 2);
      ctx.fill();
    }

    // Focal Highlight Callout from spec
    if (spec.highlight) {
      ctx.save();
      ctx.fillStyle = '#FF9F1C';
      ctx.font = '700 14px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`★ Key Mechanism: ${spec.highlight}`, cx, cy + 220);
      ctx.restore();
    }
  }

  // ==============================================================
  // 2. PHYSICS & MACHINES (Force Vectors & Induction)
  // ==============================================================
  renderForceVectors(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 10;

    // Magnetic Core / Transformer Loop
    ctx.strokeStyle = '#5C6E67';
    ctx.lineWidth = 22;
    this.roundRect(ctx, cx - 280, cy - 140, 560, 280, 24, false, true);

    // Primary Coil (Left)
    ctx.strokeStyle = '#FF9F1C';
    ctx.lineWidth = 6;
    for (let c = 0; c < 7; c++) {
      const py = cy - 100 + c * 32;
      ctx.beginPath();
      ctx.ellipse(cx - 280, py, 36, 16, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Secondary Coil (Right)
    ctx.strokeStyle = '#528271';
    ctx.lineWidth = 6;
    for (let c = 0; c < 12; c++) {
      const py = cy - 110 + c * 20;
      ctx.beginPath();
      ctx.ellipse(cx + 280, py, 36, 12, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Magnetic Flux Lines Looping through Core
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.65)';
    ctx.lineWidth = 3;
    ctx.setLineDash([12, 8]);
    ctx.lineDashOffset = -t * 40;
    this.roundRect(ctx, cx - 260, cy - 120, 520, 240, 16, false, true);
    ctx.setLineDash([]);

    // Vector Force Arrows
    this.drawVectorArrow(ctx, cx - 380, cy, cx - 380, cy - 120 * Math.sin(t * 3), '#FF9F1C', 'Primary AC Voltage (V₁)');
    this.drawVectorArrow(ctx, cx + 380, cy, cx + 380, cy - 160 * Math.sin(t * 3), '#528271', 'Induced Secondary (V₂)');
    this.drawVectorArrow(ctx, cx, cy - 120, cx + 100 * Math.sin(t * 3), cy - 120, '#E05A47', 'Magnetic Flux Φ(t)');

    // Transformer Formula HUD
    ctx.fillStyle = 'rgba(19, 34, 30, 0.88)';
    this.roundRect(ctx, cx - 180, cy - 30, 360, 60, 12, true, false);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 18px "Newsreader", Georgia, serif';
    ctx.textAlign = 'center';
    ctx.fillText('V₁ / V₂  =  N₁ / N₂  =  I₂ / I₁', cx, cy + 8);
  }

  // ==============================================================
  // 3. MATHEMATICS & FORMULAS (Equation Transform)
  // ==============================================================
  renderEquationTransform(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    // Coordinate Grid Axes
    ctx.strokeStyle = 'rgba(19, 34, 30, 0.2)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(120, cy);
    ctx.lineTo(w - 120, cy);
    ctx.moveTo(cx, 100);
    ctx.lineTo(cx, h - 140);
    ctx.stroke();

    // Dynamic Function Curve Plot: f(x) = a * sin(x) or quadratic
    ctx.strokeStyle = '#2E5BFF';
    ctx.lineWidth = 4;
    ctx.beginPath();
    const freq = 0.015;
    const amp = 80 * Math.sin(t * 0.8);
    for (let x = 120; x < w - 120; x += 4) {
      const relX = x - cx;
      const y = cy - Math.sin(relX * freq + t * 2) * amp - (relX * relX * 0.0006);
      if (x === 120) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Step-by-Step Proof Box
    ctx.fillStyle = 'rgba(251, 249, 245, 0.94)';
    this.roundRect(ctx, cx - 260, cy - 140, 520, 130, 16, true, false);
    ctx.strokeStyle = '#E8E1D5';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Formula Morphing Steps
    const step = Math.floor(t % 3);
    const steps = [
      'Step 1: ax² + bx + c = 0',
      'Step 2: x² + (b/a)x = -c/a   [Divide by a]',
      'Step 3: x = (-b ± √(b² - 4ac)) / (2a)'
    ];

    ctx.fillStyle = '#13221E';
    ctx.font = '700 20px "Newsreader", Georgia, serif';
    ctx.textAlign = 'center';
    ctx.fillText(steps[step], cx, cy - 75);

    // Dynamic Highlight Stroke
    ctx.strokeStyle = '#FF9F1C';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx - 160, cy - 50);
    ctx.lineTo(cx + 160, cy - 50);
    ctx.stroke();
  }

  // ==============================================================
  // 4. CHEMISTRY & MATERIALS (Molecular Reaction)
  // ==============================================================
  renderMolecularReaction(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    // Reactant 1: Oxygen / Carbon (Left drifting right)
    const drift = Math.sin(t * 1.8) * 60;
    const atomAX = cx - 140 + drift;
    const atomBX = cx + 140 - drift;

    // Central Nucleus A
    this.drawAtom(ctx, atomAX, cy, 32, '#E05A47', 'C', t, 6);

    // Central Nucleus B
    this.drawAtom(ctx, atomBX, cy, 32, '#2E5BFF', 'O₂', -t, 8);

    // Energy Collision Flash when colliding
    if (Math.abs(drift - 60) < 15) {
      ctx.fillStyle = 'rgba(255, 159, 28, 0.4)';
      ctx.beginPath();
      ctx.arc(cx, cy, 110, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#FFFFFF';
      ctx.font = '700 16px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('★ Exothermic Reaction (CO₂ Formation)', cx, cy - 140);
    }
  }

  drawAtom(ctx, x, y, r, color, symbol, rot, electronCount) {
    // Nucleus
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 18px "Plus Jakarta Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(symbol, x, y);

    // Electron Orbitals
    ctx.strokeStyle = 'rgba(82, 130, 113, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.ellipse(x, y, r * 2.4, r * 1.5, rot * 0.5, 0, Math.PI * 2);
    ctx.stroke();

    // Electrons orbiting
    for (let e = 0; e < electronCount; e++) {
      const angle = (rot * 2) + (e * (Math.PI * 2 / electronCount));
      const ex = x + Math.cos(angle) * (r * 2.4);
      const ey = y + Math.sin(angle) * (r * 1.5);

      ctx.fillStyle = '#FF9F1C';
      ctx.beginPath();
      ctx.arc(ex, ey, 5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // ==============================================================
  // 5. COMPUTER SCIENCE & ALGORITHMS (Sorting Algorithm)
  // ==============================================================
  renderSortingAlgorithm(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    const values = [25, 62, 14, 88, 45, 95, 33, 72, 18, 54];
    const barWidth = 48;
    const gap = 16;
    const startX = cx - ((values.length * (barWidth + gap)) / 2);

    const activeI = Math.floor(t * 1.5) % values.length;
    const activeJ = (activeI + 1) % values.length;

    values.forEach((val, idx) => {
      const bx = startX + idx * (barWidth + gap);
      const barH = val * 2.2;
      const by = cy + 110 - barH;

      let color = '#5C6E67'; // Default un-sorted slate
      if (idx === activeI) color = '#FF9F1C'; // Comparing Surya Gold
      if (idx === activeJ) color = '#E05A47'; // Swapping Terracotta
      if (idx < activeI) color = '#528271';   // Sorted Celadon

      ctx.fillStyle = color;
      this.roundRect(ctx, bx, by, barWidth, barH, 8, true, false);

      // Value Label
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '700 14px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(val, bx + barWidth / 2, by + 22);

      // Array Index
      ctx.fillStyle = '#8E9E97';
      ctx.font = '600 12px "Plus Jakarta Sans", sans-serif';
      ctx.fillText(`[${idx}]`, bx + barWidth / 2, cy + 134);
    });

    // Pointers Arrow (i and j)
    const arrowX = startX + activeI * (barWidth + gap) + barWidth / 2;
    this.drawVectorArrow(ctx, arrowX, cy + 180, arrowX, cy + 150, '#FF9F1C', 'Pointer i');
  }

  // ==============================================================
  // 6. GEOGRAPHY & NATURE (Cycle Loop: Water Cycle)
  // ==============================================================
  renderCycleLoop(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    // Sun with Radiant Rays (Top Left)
    const sunX = 180;
    const sunY = 160;
    ctx.fillStyle = '#FF9F1C';
    ctx.beginPath();
    ctx.arc(sunX, sunY, 44, 0, Math.PI * 2);
    ctx.fill();

    // Radiant Rays
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.4)';
    ctx.lineWidth = 3;
    for (let r = 0; r < 8; r++) {
      const a = (t * 0.5) + (r * Math.PI / 4);
      ctx.beginPath();
      ctx.moveTo(sunX + Math.cos(a) * 54, sunY + Math.sin(a) * 54);
      ctx.lineTo(sunX + Math.cos(a) * 78, sunY + Math.sin(a) * 78);
      ctx.stroke();
    }

    // Clouds (Top Right)
    this.drawCloud(ctx, cx + 180, 160, 60, '#CAD8D2');

    // Ocean / Lake (Bottom Left)
    ctx.fillStyle = 'rgba(46, 91, 255, 0.3)';
    this.roundRect(ctx, 80, cy + 60, 380, 110, 16, true, false);
    ctx.fillStyle = '#2E5BFF';
    ctx.font = '700 15px "Plus Jakarta Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Ocean Collection', 270, cy + 120);

    // Evaporation Rising Particles
    for (let p = 0; p < 12; p++) {
      const epY = (cy + 40) - (((t * 40) + p * 20) % 180);
      const epX = 220 + Math.sin(t * 3 + p) * 30;
      ctx.fillStyle = 'rgba(46, 91, 255, 0.6)';
      ctx.beginPath();
      ctx.arc(epX, epY, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Precipitation Rain Streams
    for (let r = 0; r < 18; r++) {
      const rx = (cx + 120) + (r * 12);
      const ry = 220 + (((t * 120) + r * 15) % 140);
      ctx.strokeStyle = '#2E5BFF';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(rx, ry);
      ctx.lineTo(rx - 4, ry + 16);
      ctx.stroke();
    }
  }

  drawCloud(ctx, x, y, r, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.arc(x + 50, y - 10, r * 0.8, 0, Math.PI * 2);
    ctx.arc(x - 50, y - 5, r * 0.7, 0, Math.PI * 2);
    ctx.fill();
  }

  // ==============================================================
  // 7. FINANCE & ECONOMICS (Growth Curve: Compound Interest)
  // ==============================================================
  renderGrowthCurve(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2;

    const ox = 180;
    const oy = h - 160;
    const gw = w - 360;
    const gh = 280;

    // Coordinate Chart Grid
    ctx.strokeStyle = 'rgba(19, 34, 30, 0.2)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(ox, oy - gh);
    ctx.lineTo(ox, oy);
    ctx.lineTo(ox + gw, oy);
    ctx.stroke();

    // Chart Labels
    ctx.fillStyle = '#8E9E97';
    ctx.font = '600 13px "Plus Jakarta Sans", sans-serif';
    ctx.fillText('Time (Years) →', ox + gw - 90, oy + 28);
    ctx.fillText('Accumulated Wealth ($) ↑', ox - 14, oy - gh - 12);

    // 1. Simple Interest (Linear dashed)
    ctx.strokeStyle = '#8E9E97';
    ctx.lineWidth = 2.5;
    ctx.setLineDash([8, 6]);
    ctx.beginPath();
    ctx.moveTo(ox, oy);
    ctx.lineTo(ox + gw, oy - (gh * 0.42));
    ctx.stroke();
    ctx.setLineDash([]);

    // 2. Compound Interest Exponential Curve (Surya Gold Glowing)
    ctx.strokeStyle = '#FF9F1C';
    ctx.lineWidth = 4.5;
    ctx.beginPath();
    const progressLimit = Math.min(1, (t * 0.15) % 1.2);
    for (let p = 0; p <= gw * progressLimit; p += 6) {
      const norm = p / gw;
      const curveY = oy - (Math.pow(norm, 2.8) * gh);
      if (p === 0) ctx.moveTo(ox + p, curveY);
      else ctx.lineTo(ox + p, curveY);
    }
    ctx.stroke();

    // Milestones Badges (Year 10, 20, 30)
    const milestones = [
      { year: 'Yr 10', mult: '2.6x', x: ox + gw * 0.33, y: oy - gh * 0.18 },
      { year: 'Yr 20', mult: '6.7x', x: ox + gw * 0.66, y: oy - gh * 0.48 },
      { year: 'Yr 30', mult: '18.4x', x: ox + gw * 0.95, y: oy - gh * 0.95 }
    ];

    milestones.forEach(m => {
      ctx.fillStyle = '#528271';
      this.roundRect(ctx, m.x - 30, m.y - 20, 60, 40, 8, true, false);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '700 12px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(m.mult, m.x, m.y - 2);
      ctx.font = '500 10px "Plus Jakarta Sans", sans-serif';
      ctx.fillText(m.year, m.x, m.y + 12);
    });
  }

  // ==============================================================
  // 8. EVERYDAY SKILLS & TUTORIALS (Step-by-Step UI Guide)
  // ==============================================================
  renderStepTutorial(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    // Device Screen Mockup Card
    ctx.fillStyle = '#FFFFFF';
    this.roundRect(ctx, cx - 180, cy - 160, 360, 320, 20, true, false);
    ctx.strokeStyle = '#E8E1D5';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Device Header Bar
    ctx.fillStyle = '#13221E';
    this.roundRect(ctx, cx - 180, cy - 160, 360, 48, 20, true, false);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 15px "Plus Jakarta Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Digital Verification Flow', cx, cy - 130);

    // Step Progress Pills (1, 2, 3)
    const curStep = Math.floor(t * 0.6) % 3;
    for (let s = 0; s < 3; s++) {
      const sx = cx - 80 + s * 80;
      ctx.fillStyle = s <= curStep ? '#528271' : '#E8E1D5';
      ctx.beginPath();
      ctx.arc(sx, cy - 80, 16, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#FFFFFF';
      ctx.font = '700 13px "Plus Jakarta Sans", sans-serif';
      ctx.fillText(s + 1, sx, cy - 75);
    }

    // Interactive Action Box (e.g. Enter OTP / Confirm)
    ctx.fillStyle = '#F3EFE6';
    this.roundRect(ctx, cx - 140, cy - 20, 280, 56, 12, true, false);
    ctx.fillStyle = '#13221E';
    ctx.font = '700 16px "Plus Jakarta Sans", sans-serif';
    ctx.fillText('•••• Secure 6-Digit PIN', cx, cy + 14);

    // Animated Tap Cursor / Pointer Finger
    const tapX = cx + Math.sin(t * 3) * 40;
    const tapY = cy + 80;
    ctx.fillStyle = '#FF9F1C';
    ctx.beginPath();
    ctx.arc(tapX, tapY, 14, 0, Math.PI * 2);
    ctx.fill();

    // Tap Ripple
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.4)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(tapX, tapY, 24 + (t * 20 % 30), 0, Math.PI * 2);
    ctx.stroke();
  }

  // ==============================================================
  // FALLBACK / GENERIC DIAGRAM RENDERER
  // ==============================================================
  renderGenericDiagram(ctx, w, h, spec, t) {
    const cx = w / 2;
    const cy = h / 2 - 20;

    const elements = spec.elements || [
      { name: 'Core Concept', x: 50, y: 50, color: '#FF9F1C' },
      { name: 'Component Alpha', x: 25, y: 30, color: '#528271' },
      { name: 'Component Beta', x: 75, y: 70, color: '#2E5BFF' }
    ];

    // Connective Lines
    ctx.strokeStyle = 'rgba(82, 130, 113, 0.35)';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    elements.forEach((el, idx) => {
      const px = (el.x / 100) * w;
      const py = (el.y / 100) * (h - 180) + 80;
      if (idx === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.stroke();

    // Render Nodes
    elements.forEach(el => {
      const px = (el.x / 100) * w;
      const py = (el.y / 100) * (h - 180) + 80;

      // Pulse highlight
      ctx.fillStyle = el.color || '#FF9F1C';
      ctx.beginPath();
      ctx.arc(px, py, 28 + Math.sin(t * 4) * 3, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#FFFFFF';
      ctx.font = '700 13px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(el.name || '', px, py - 36);
    });
  }

  // ==============================================================
  // HELPER CANVAS UTILITIES
  // ==============================================================
  roundRect(ctx, x, y, width, height, radius, fill, stroke) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
  }

  drawVectorArrow(ctx, fromX, fromY, toX, toY, color, label) {
    const headlen = 14;
    const dx = toX - fromX;
    const dy = toY - fromY;
    const angle = Math.atan2(dy, dx);

    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 3.5;

    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6), toY - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6), toY - headlen * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    if (label) {
      ctx.font = '600 12px "Plus Jakarta Sans", sans-serif';
      ctx.fillStyle = color;
      ctx.fillText(label, toX + 10, toY);
    }
    ctx.restore();
  }

  // ==============================================================
  // VIDEO EXPORT ENGINE (Canvas Capture + Audio Mixing + MediaRecorder)
  // ==============================================================
  async exportCurrentLessonVideo(onProgressCallback) {
    if (!this.project || this.scenes.length === 0) {
      throw new Error('No active animated lesson to export.');
    }
    this.isExporting = true;
    this.pause();

    const stream = this.canvas.captureStream(30); // 30 FPS video stream
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const dest = audioCtx.createMediaStreamDestination();

    // Check supported MIME type
    let mimeType = 'video/webm;codecs=vp9,opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = 'video/webm';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'video/mp4';
      }
    }

    const combinedStream = new MediaStream([
      ...stream.getVideoTracks(),
      ...dest.stream.getAudioTracks()
    ]);

    this.mediaRecorder = new MediaRecorder(combinedStream, { mimeType });
    this.recordedChunks = [];

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        this.recordedChunks.push(e.data);
      }
    };

    const completionPromise = new Promise((resolve, reject) => {
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.recordedChunks, { type: mimeType });
        resolve(blob);
      };
      this.mediaRecorder.onerror = (err) => reject(err);
    });

    this.mediaRecorder.start();

    // Sequentially play and capture each scene
    for (let sIdx = 0; sIdx < this.scenes.length; sIdx++) {
      this.prepareScene(sIdx);
      const scene = this.scenes[sIdx];
      const duration = scene.duration_sec || 12;

      // Play audio into audioCtx destination
      try {
        const resp = await fetch(`/api/animated/scene/${scene.id}/audio`);
        if (resp.ok) {
          const arrayBuf = await resp.arrayBuffer();
          const audioBuffer = await audioCtx.decodeAudioData(arrayBuf);
          const source = audioCtx.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(dest);
          source.start(0);
        }
      } catch (err) {
        console.warn('Audio export mix fallback:', err);
      }

      // Render frames across the scene duration
      const totalFrames = Math.floor(duration * 30);
      for (let f = 0; f < totalFrames; f++) {
        const t = f / 30;
        this.renderFrame(t);
        if (onProgressCallback) {
          onProgressCallback(sIdx, this.scenes.length, f / totalFrames);
        }
        await new Promise(r => setTimeout(r, 1000 / 30));
      }
    }

    this.mediaRecorder.stop();
    const finalBlob = await completionPromise;
    this.isExporting = false;
    audioCtx.close();

    // Trigger download of educational video file
    const safeTitle = (this.project.title || 'PodSiksha_Lesson').replace(/[^a-zA-Z0-9_-]/g, '_');
    const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
    const filename = `${safeTitle}_Animated.${ext}`;
    
    const a = document.createElement('a');
    a.href = URL.createObjectURL(finalBlob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    return filename;
  }
}

// Global instance handle
window.UniversalAnimationEngine = UniversalAnimationEngine;
