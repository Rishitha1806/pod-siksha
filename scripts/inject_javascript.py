import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
html_path = os.path.abspath(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("\r\n", "\n")

# 1. Update PROTECTED_SCREENS to include 'profile'
old_screens = "const PROTECTED_SCREENS = ['home', 'animated-studio', 'animated-library', 'insights', 'studio', 'workspace', 'concept-dna', 'teachback'];"
new_screens = "const PROTECTED_SCREENS = ['home', 'animated-studio', 'animated-library', 'insights', 'studio', 'workspace', 'concept-dna', 'teachback', 'profile'];"

if old_screens in html:
    html = html.replace(old_screens, new_screens, 1)
    print("Updated PROTECTED_SCREENS to include profile.")

# 2. Update switchScreen to map 'learn', 'library', 'profile' to their screen tabs
old_switch_target = """      // 3. Activate target screen frame
      const targetFrame = document.getElementById('view-' + screenId);
      const targetTab = document.getElementById('tab-' + screenId);

      if (targetFrame) targetFrame.classList.add('active');
      if (targetTab) targetTab.classList.add('active');"""

new_switch_target = """      // 3. Activate target screen frame
      const targetFrame = document.getElementById('view-' + screenId);
      
      // Determine corresponding navbar tab
      let activeTabId = 'tab-' + screenId;
      if (screenId === 'animated-studio') activeTabId = 'tab-learn';
      if (screenId === 'animated-library') activeTabId = 'tab-library';
      
      // Clear all active tabs
      document.querySelectorAll('.screen-tab-btn').forEach(btn => btn.classList.remove('active'));
      const activeTab = document.getElementById(activeTabId) || document.getElementById('tab-' + screenId);
      if (activeTab) activeTab.classList.add('active');

      if (targetFrame) targetFrame.classList.add('active');

      // Trigger screen-specific data loaders
      if (screenId === 'concept-dna') loadConceptTree();
      if (screenId === 'teachback') loadTeachBackConcepts();
      if (screenId === 'insights') loadInsights();
      if (screenId === 'home') loadJourneys();
      if (screenId === 'animated-library') loadAnimatedProjectsList();
      if (screenId === 'profile') loadUserProfile();"""

if old_switch_target in html:
    html = html.replace(old_switch_target, new_switch_target, 1)
    print("Updated switchScreen with tab mappings and screen loaders.")
else:
    print("Warning: old_switch_target not found.")

# 3. Add complete Concept DNA Knowledge Tree, Teach-Back, and Understanding Tracker Engine
engine_code = """
    // ==============================================================
    // POD-SIKSHA 3.0: CONCEPT DNA KNOWLEDGE TREE ENGINE
    // ==============================================================
    let currentTreeData = null;
    let allTreeNodes = [];
    let treeZoomLevel = 1.0;
    let treePanX = 60;
    let treePanY = 80;
    let isTreePanning = false;
    let treePanStartX = 0;
    let treePanStartY = 0;
    let selectedConceptNode = null;
    let activeStatusFilter = 'all';

    async function loadConceptTree(projectId = null) {
      const container = document.getElementById('conceptTreeContainer');
      const emptyState = document.getElementById('conceptTreeEmptyState');
      const viewport = document.getElementById('conceptTreeViewport');
      const projSelect = document.getElementById('conceptTreeProjectSelect');

      try {
        const token = AuthManager.authToken;
        const headers = token ? { 'Authorization': 'Bearer ' + token } : {};
        const url = projectId && projectId !== 'all' ? `/api/concept-tree?project_id=${projectId}` : '/api/concept-tree';
        const res = await fetch(url, { headers });
        if (!res.ok) throw new Error('Could not fetch concept tree');

        const data = await res.json();
        currentTreeData = data;
        allTreeNodes = [];

        // Update counts
        const total = data.total_concepts || 0;
        const understood = data.understood_count || 0;
        const learning = data.learning_count || 0;
        const revision = data.revision_count || 0;

        document.getElementById('cntAll').textContent = total;
        document.getElementById('cntUnderstood').textContent = understood;
        document.getElementById('cntLearning').textContent = learning;
        document.getElementById('cntRevision').textContent = revision;

        // Populate projects dropdown if needed
        if (projSelect && projSelect.options.length <= 1 && data.trees && data.trees.length > 0) {
          projSelect.innerHTML = '<option value="all">🌳 Entire Knowledge Forest (All Lessons)</option>';
          data.trees.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.project_id;
            opt.textContent = `📖 ${t.title} (${t.total_concepts} concepts)`;
            projSelect.appendChild(opt);
          });
        }

        if (!data.trees || data.trees.length === 0 || total === 0) {
          if (emptyState) emptyState.style.display = 'block';
          if (viewport) viewport.innerHTML = '';
          return;
        }

        if (emptyState) emptyState.style.display = 'none';

        // Collect all nodes
        data.trees.forEach(t => {
          if (t.all_nodes) allTreeNodes.push(...t.all_nodes);
        });

        // Render Tree in SVG
        renderConceptTreeSvg(data);

      } catch (err) {
        console.error('Error loading concept tree:', err);
        if (emptyState) emptyState.style.display = 'block';
      }
    }

    function handleConceptTreeProjectChange(pId) {
      loadConceptTree(pId);
    }

    function filterTreeStatus(status, btnEl) {
      activeStatusFilter = status;
      document.querySelectorAll('.status-filter-pill').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');

      if (!currentTreeData) return;
      renderConceptTreeSvg(currentTreeData);
    }

    function handleConceptTreeSearch(query) {
      const q = query.trim().toLowerCase();
      document.querySelectorAll('.tree-node-group').forEach(group => {
        const name = (group.getAttribute('data-name') || '').toLowerCase();
        if (!q) {
          group.style.opacity = '1';
        } else if (name.includes(q)) {
          group.style.opacity = '1';
          group.querySelector('rect')?.setAttribute('stroke', 'var(--accent-terracotta)');
          group.querySelector('rect')?.setAttribute('stroke-width', '3');
        } else {
          group.style.opacity = '0.25';
        }
      });
    }

    function renderConceptTreeSvg(data) {
      const viewport = document.getElementById('conceptTreeViewport');
      if (!viewport) return;
      viewport.innerHTML = '';

      let currentX = 80;
      let currentY = 80;
      const nodeWidth = 220;
      const nodeHeight = 72;
      const levelGapX = 280;
      const nodeGapY = 96;

      const placedNodes = [];
      const linksToDraw = [];

      data.trees.forEach((treeObj, treeIdx) => {
        const root = treeObj.tree;
        if (!root) return;

        // Place Root Node
        const rootX = currentX;
        const rootY = currentY + 120;
        placedNodes.push({
          id: root.id,
          name: root.name,
          isRoot: true,
          status: 'root',
          x: rootX,
          y: rootY,
          raw: root
        });

        // Place Level 1 Major Concepts
        const majorChildren = root.children || [];
        majorChildren.forEach((major, mIdx) => {
          if (activeStatusFilter !== 'all' && major.status !== activeStatusFilter) return;

          const mX = rootX + levelGapX;
          const mY = currentY + mIdx * nodeGapY;
          placedNodes.push({
            id: major.id,
            name: major.name,
            status: major.status,
            x: mX,
            y: mY,
            raw: major
          });

          linksToDraw.push({
            fromX: rootX + nodeWidth,
            fromY: rootY + nodeHeight / 2,
            toX: mX,
            toY: mY + nodeHeight / 2,
            type: 'hierarchy'
          });

          // Place Level 2 Subconcepts
          const subChildren = major.children || [];
          subChildren.forEach((sub, sIdx) => {
            if (activeStatusFilter !== 'all' && sub.status !== activeStatusFilter) return;

            const sX = mX + levelGapX;
            const sY = mY + (sIdx - (subChildren.length - 1) / 2) * 80;
            placedNodes.push({
              id: sub.id,
              name: sub.name,
              status: sub.status,
              x: sX,
              y: sY,
              raw: sub
            });

            linksToDraw.push({
              fromX: mX + nodeWidth,
              fromY: mY + nodeHeight / 2,
              toX: sX,
              toY: sY + nodeHeight / 2,
              type: 'prerequisite'
            });
          });
        });

        currentY += Math.max(majorChildren.length * nodeGapY, 260) + 60;
      });

      // 1. Draw Links (Cubic Bezier curves)
      linksToDraw.forEach(l => {
        const dx = (l.toX - l.fromX) / 2;
        const d = `M ${l.fromX} ${l.fromY} C ${l.fromX + dx} ${l.fromY}, ${l.toX - dx} ${l.toY}, ${l.toX} ${l.toY}`;
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        path.setAttribute('class', `tree-link ${l.type === 'prerequisite' ? 'prereq-link' : ''}`);
        if (l.type === 'prerequisite') path.setAttribute('marker-end', 'url(#arrowPrereq)');
        viewport.appendChild(path);
      });

      // 2. Draw Nodes
      placedNodes.forEach(node => {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'tree-node-group');
        g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
        g.setAttribute('data-id', node.id);
        g.setAttribute('data-name', node.name);

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', nodeWidth);
        rect.setAttribute('height', nodeHeight);
        rect.setAttribute('rx', '8');
        rect.setAttribute('ry', '8');

        // Color by learning status
        let strokeCol = 'var(--border-parchment)';
        let fillCol = 'white';
        let statusBadgeText = 'LEARNING';
        let badgeColor = 'var(--accent-surya)';

        if (node.isRoot) {
          fillCol = 'var(--ink-primary)';
          strokeCol = 'var(--accent-surya)';
          statusBadgeText = 'TOPIC ROOT';
          badgeColor = 'var(--accent-surya)';
        } else if (node.status === 'understood') {
          strokeCol = 'var(--accent-celadon)';
          statusBadgeText = 'UNDERSTOOD';
          badgeColor = 'var(--accent-celadon)';
        } else if (node.status === 'needs_revision') {
          strokeCol = 'var(--accent-terracotta)';
          statusBadgeText = 'NEEDS REVISION';
          badgeColor = 'var(--accent-terracotta)';
        } else {
          strokeCol = 'var(--accent-surya)';
          statusBadgeText = 'LEARNING';
          badgeColor = 'var(--accent-surya)';
        }

        rect.setAttribute('fill', fillCol);
        rect.setAttribute('stroke', strokeCol);
        rect.setAttribute('stroke-width', node.isRoot ? '2.5' : '1.8');
        g.appendChild(rect);

        // Status Badge Pill inside Node
        const badge = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        badge.setAttribute('x', '12');
        badge.setAttribute('y', '20');
        badge.setAttribute('fill', badgeColor);
        badge.setAttribute('font-size', '9');
        badge.setAttribute('font-weight', '800');
        badge.setAttribute('letter-spacing', '0.6px');
        badge.textContent = statusBadgeText;
        g.appendChild(badge);

        // Concept Title
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        title.setAttribute('x', '12');
        title.setAttribute('y', '42');
        title.setAttribute('fill', node.isRoot ? 'white' : 'var(--ink-primary)');
        title.setAttribute('font-family', 'var(--font-sans)');
        title.setAttribute('font-size', '13');
        title.setAttribute('font-weight', '700');
        const truncated = node.name.length > 22 ? node.name.slice(0, 22) + '...' : node.name;
        title.textContent = truncated;
        g.appendChild(title);

        // Subtitle / Scene Reference
        const sub = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        sub.setAttribute('x', '12');
        sub.setAttribute('y', '58');
        sub.setAttribute('fill', node.isRoot ? '#CAD8D2' : 'var(--ink-secondary)');
        sub.setAttribute('font-size', '10');
        sub.textContent = node.raw.scene_title ? `Scene ${node.raw.scene_index}: ${node.raw.scene_title.slice(0, 20)}` : (node.isRoot ? `${node.raw.total_concepts || 0} Core Concepts` : 'Click to inspect');
        g.appendChild(sub);

        // Click Handler: Open Concept Detail Drawer
        g.addEventListener('click', () => {
          if (!node.isRoot) {
            openConceptDetail(node.raw);
          }
        });

        viewport.appendChild(g);
      });

      applyTreeTransform();
      setupTreePanZoom();
    }

    function setupTreePanZoom() {
      const container = document.getElementById('conceptTreeContainer');
      if (!container || container._panZoomBound) return;
      container._panZoomBound = true;

      container.addEventListener('mousedown', (e) => {
        if (e.target.closest('.tree-node-group')) return;
        isTreePanning = true;
        treePanStartX = e.clientX - treePanX;
        treePanStartY = e.clientY - treePanY;
      });

      window.addEventListener('mousemove', (e) => {
        if (!isTreePanning) return;
        treePanX = e.clientX - treePanStartX;
        treePanY = e.clientY - treePanStartY;
        applyTreeTransform();
      });

      window.addEventListener('mouseup', () => {
        isTreePanning = false;
      });

      container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.1 : 0.9;
        zoomConceptTree(factor);
      });
    }

    function zoomConceptTree(factor) {
      treeZoomLevel = Math.max(0.4, Math.min(2.5, treeZoomLevel * factor));
      applyTreeTransform();
    }

    function resetConceptTreeView() {
      treeZoomLevel = 1.0;
      treePanX = 60;
      treePanY = 80;
      applyTreeTransform();
    }

    function applyTreeTransform() {
      const viewport = document.getElementById('conceptTreeViewport');
      if (viewport) {
        viewport.setAttribute('transform', `translate(${treePanX}, ${treePanY}) scale(${treeZoomLevel})`);
      }
    }

    // Concept Detail Drawer
    function openConceptDetail(nodeData) {
      selectedConceptNode = nodeData;
      const drawer = document.getElementById('conceptDetailDrawer');
      const backdrop = document.getElementById('conceptDrawerBackdrop');
      if (!drawer) return;

      document.getElementById('drawerConceptName').textContent = nodeData.name;
      document.getElementById('drawerDefinition').textContent = nodeData.definition || nodeData.summary || 'Core educational concept.';
      document.getElementById('drawerEvidenceText').textContent = nodeData.status_reason || 'Introduced in lesson';

      const badge = document.getElementById('drawerStatusBadge');
      if (badge) {
        badge.textContent = (nodeData.status || 'learning').replace('_', ' ').toUpperCase();
        if (nodeData.status === 'understood') {
          badge.style.background = 'var(--accent-celadon)';
          badge.style.color = 'white';
        } else if (nodeData.status === 'needs_revision') {
          badge.style.background = 'var(--accent-terracotta)';
          badge.style.color = 'white';
        } else {
          badge.style.background = 'var(--accent-surya)';
          badge.style.color = '#13221E';
        }
      }

      // Prerequisites List
      const prereqsList = document.getElementById('drawerPrereqsList');
      if (prereqsList) {
        prereqsList.innerHTML = '';
        const prereqs = nodeData.prerequisites || [];
        if (prereqs.length === 0) {
          prereqsList.innerHTML = '<span style="font-size:12px; color:var(--ink-secondary);">None (Foundational concept)</span>';
        } else {
          prereqs.forEach(p => {
            const span = document.createElement('span');
            span.className = 'status-filter-pill';
            span.textContent = p;
            span.onclick = () => handleConceptTreeSearch(p);
            prereqsList.appendChild(span);
          });
        }
      }

      // Related List
      const relatedList = document.getElementById('drawerRelatedList');
      if (relatedList) {
        relatedList.innerHTML = '';
        const related = nodeData.related || [];
        if (related.length === 0) {
          relatedList.innerHTML = '<span style="font-size:12px; color:var(--ink-secondary);">No related concepts mapped</span>';
        } else {
          related.forEach(r => {
            const span = document.createElement('span');
            span.className = 'status-filter-pill';
            span.textContent = r;
            span.onclick = () => handleConceptTreeSearch(r);
            relatedList.appendChild(span);
          });
        }
      }

      drawer.classList.add('open');
      if (backdrop) backdrop.classList.add('open');
    }

    function closeConceptDetailDrawer() {
      const drawer = document.getElementById('conceptDetailDrawer');
      const backdrop = document.getElementById('conceptDrawerBackdrop');
      if (drawer) drawer.classList.remove('open');
      if (backdrop) backdrop.classList.remove('open');
    }

    function watchConceptSceneAgain() {
      if (!selectedConceptNode) return;
      closeConceptDetailDrawer();
      switchScreen('animated-studio');

      if (selectedConceptNode.project_id) {
        loadActiveAnimatedProject(selectedConceptNode.project_id).then(() => {
          if (animEngine && selectedConceptNode.scene_index) {
            animEngine.seekScene(selectedConceptNode.scene_index - 1);
            showToast(`Jumped to Scene ${selectedConceptNode.scene_index}: ${selectedConceptNode.name}`);
          }
        });
      }
    }

    async function markConceptRevisionAction() {
      if (!selectedConceptNode) return;
      try {
        const token = AuthManager.authToken;
        const res = await fetch('/api/concept-tree/mark-revision', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': 'Bearer ' + token } : {})
          },
          body: JSON.stringify({
            concept_name: selectedConceptNode.name,
            reason: 'Flagged by learner for spaced recall',
            project_id: selectedConceptNode.project_id
          })
        });
        if (res.ok) {
          showToast(`Marked '${selectedConceptNode.name}' for revision!`);
          selectedConceptNode.status = 'needs_revision';
          selectedConceptNode.status_reason = 'Flagged by learner for spaced recall';
          openConceptDetail(selectedConceptNode);
          loadConceptTree();
        }
      } catch (err) {
        showToast('Could not mark for revision.');
      }
    }

    // Compare Concepts
    function openCompareModal() {
      const modal = document.getElementById('compareConceptsModal');
      const selA = document.getElementById('cmpConceptA');
      const selB = document.getElementById('cmpConceptB');
      if (!modal || !selA || !selB) return;

      selA.innerHTML = '';
      selB.innerHTML = '';

      if (allTreeNodes.length < 2) {
        showToast('Generate at least one lesson to compare concepts.');
        return;
      }

      const uniqueNames = [...new Set(allTreeNodes.map(n => n.name))];
      uniqueNames.forEach((name, idx) => {
        const optA = document.createElement('option');
        optA.value = name;
        optA.textContent = name;
        selA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = name;
        optB.textContent = name;
        if (idx === 1) optB.selected = true;
        selB.appendChild(optB);
      });

      document.getElementById('compareResultsArea').style.display = 'none';
      modal.style.display = 'flex';
    }

    function closeCompareModal() {
      const modal = document.getElementById('compareConceptsModal');
      if (modal) modal.style.display = 'none';
    }

    async function submitCompareConcepts() {
      const a = document.getElementById('cmpConceptA')?.value;
      const b = document.getElementById('cmpConceptB')?.value;
      if (!a || !b) return;

      const area = document.getElementById('compareResultsArea');
      if (area) area.style.display = 'block';
      document.getElementById('cmpOverviewText').textContent = 'Gemini is generating comparative analysis...';

      try {
        const token = AuthManager.authToken;
        const res = await fetch('/api/concept-tree/compare', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': 'Bearer ' + token } : {})
          },
          body: JSON.stringify({ concept_a: a, concept_b: b, language: 'en' })
        });
        const data = await res.json();

        document.getElementById('cmpOverviewText').textContent = data.overview || '';

        const simList = document.getElementById('cmpSimilaritiesList');
        simList.innerHTML = (data.similarities || []).map(s => `<li>${s}</li>`).join('');

        const diffList = document.getElementById('cmpDifferencesList');
        diffList.innerHTML = (data.differences || []).map(d => `<li>${d}</li>`).join('');

        // Table
        const tblWrap = document.getElementById('cmpTableWrap');
        if (data.comparison_table && data.comparison_table.length > 0) {
          let rows = data.comparison_table.map(row => `
            <tr>
              <td style="padding:8px 12px; font-weight:700; border-bottom:1px solid var(--border-parchment);">${row.attribute}</td>
              <td style="padding:8px 12px; border-bottom:1px solid var(--border-parchment);">${row.concept_a_val}</td>
              <td style="padding:8px 12px; border-bottom:1px solid var(--border-parchment);">${row.concept_b_val}</td>
            </tr>
          `).join('');
          tblWrap.innerHTML = `
            <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left; background:white; border:1px solid var(--border-parchment); border-radius:var(--radius-sm);">
              <thead>
                <tr style="background:var(--surface-tinted);">
                  <th style="padding:8px 12px; border-bottom:2px solid var(--border-parchment);">Attribute</th>
                  <th style="padding:8px 12px; border-bottom:2px solid var(--border-parchment);">${a}</th>
                  <th style="padding:8px 12px; border-bottom:2px solid var(--border-parchment);">${b}</th>
                </tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>
          `;
        }

        // Quiz check
        const q = data.check_question;
        if (q && q.question) {
          document.getElementById('cmpQText').textContent = q.question;
          const optDiv = document.getElementById('cmpQOptions');
          optDiv.innerHTML = q.options.map((opt, idx) => `
            <button class="scene-pill-btn" style="text-align:left; padding:8px 12px;" onclick="checkCompareQuizAnswer(${idx}, ${q.correct_index}, '${encodeURIComponent(q.explanation || '')}')">
              ${opt}
            </button>
          `).join('');
          document.getElementById('cmpQFeedback').style.display = 'none';
        }
      } catch (err) {
        document.getElementById('cmpOverviewText').textContent = 'Could not generate comparison.';
      }
    }

    function checkCompareQuizAnswer(selected, correct, expEnc) {
      const fb = document.getElementById('cmpQFeedback');
      if (!fb) return;
      fb.style.display = 'block';
      const explanation = decodeURIComponent(expEnc);
      if (selected === correct) {
        fb.style.color = 'var(--accent-celadon)';
        fb.textContent = `✓ Correct! ${explanation}`;
      } else {
        fb.style.color = 'var(--accent-terracotta)';
        fb.textContent = `✗ Not quite. ${explanation}`;
      }
    }

    // Explain It Again in Animated Studio
    let currentExplainMode = 'simpler';
    function openExplainAgainModal() {
      if (animEngine) animEngine.pause();
      const modal = document.getElementById('explainAgainModal');
      if (modal) {
        document.getElementById('explainAgainResultBox').style.display = 'none';
        modal.style.display = 'flex';
      }
    }

    function closeExplainAgainModal() {
      const modal = document.getElementById('explainAgainModal');
      if (modal) modal.style.display = 'none';
    }

    function selectExplainMode(mode, el) {
      currentExplainMode = mode;
      document.querySelectorAll('#explainAgainModal .complexity-pill-btn').forEach(b => b.classList.remove('selected'));
      if (el) el.classList.add('selected');
    }

    async function submitExplainAgainAction() {
      const activeScene = animEngine ? animEngine.scenes[animEngine.currentSceneIndex] : null;
      if (!activeScene) return;

      const resBox = document.getElementById('explainAgainResultBox');
      const resText = document.getElementById('explainAgainText');
      if (resBox) resBox.style.display = 'block';
      if (resText) resText.textContent = 'AI Educator is generating an adaptive explanation...';

      try {
        const token = AuthManager.authToken;
        const res = await fetch(`/api/animated/scene/${activeScene.id}/explain-again`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': 'Bearer ' + token } : {})
          },
          body: JSON.stringify({ mode: currentExplainMode, complexity: 'intermediate' })
        });
        const data = await res.json();
        if (resText) {
          resText.innerHTML = `
            <strong>${data.key_takeaway || 'Core Insight'}:</strong><br><br>
            ${data.explanation || 'Explanation generated.'}<br><br>
            <em>Visual Cue: ${data.visual_cue || ''}</em>
          `;
        }

        if (currentExplainMode === 'visual_focus' && animEngine) {
          animEngine.seek(0);
          animEngine.play();
        }
      } catch (err) {
        if (resText) resText.textContent = 'Could not generate explanation.';
      }
    }

    // Teach-Back Implementation
    async function loadTeachBackConcepts() {
      const select = document.getElementById('teachbackConceptSelect');
      if (!select) return;

      try {
        const token = AuthManager.authToken;
        const res = await fetch('/api/teachback/concepts', {
          headers: token ? { 'Authorization': 'Bearer ' + token } : {}
        });
        const data = await res.json();
        const concepts = data.concepts || [];

        select.innerHTML = '';
        if (concepts.length === 0) {
          select.innerHTML = '<option value="">No concepts available yet. Create a lesson first!</option>';
          return;
        }

        concepts.forEach((c, idx) => {
          const opt = document.createElement('option');
          opt.value = c.concept_name;
          opt.textContent = `${c.concept_name} (${(c.status || 'learning').replace('_', ' ')})`;
          if (idx === 0) opt.selected = true;
          select.appendChild(opt);
        });

        handleTeachbackConceptChange(concepts[0].concept_name);
      } catch (err) {
        console.error('Error loading teachback concepts:', err);
      }
    }

    function handleTeachbackConceptChange(conceptName) {
      const promptEl = document.getElementById('teachbackPromptText');
      if (promptEl) {
        promptEl.textContent = `Can you explain ${conceptName} in your own words? What is its core mechanism and why does it matter?`;
      }
      document.getElementById('teachbackEvalGrid').style.display = 'none';
      document.getElementById('teachbackFooterStrip').style.display = 'none';
    }

    async function submitTeachBackExplanation() {
      const select = document.getElementById('teachbackConceptSelect');
      const concept = select ? select.value : 'Core Concept';
      const input = document.getElementById('teachbackTextInput');
      const text = input ? input.value.trim() : '';

      if (!text) {
        showToast('Please type or speak your explanation first.');
        return;
      }

      const statusEl = document.getElementById('teachbackEvaluatingStatus');
      if (statusEl) statusEl.style.display = 'inline';

      try {
        const token = AuthManager.authToken;
        const formData = new FormData();
        formData.append('concept_tag', concept);
        formData.append('explanation_text', text);
        formData.append('ai_prompt', `Explain ${concept} in your own words.`);

        const res = await fetch('/api/teachback/evaluate', {
          method: 'POST',
          headers: token ? { 'Authorization': 'Bearer ' + token } : {},
          body: formData
        });

        if (statusEl) statusEl.style.display = 'none';

        if (res.ok) {
          const data = await res.json();
          document.getElementById('teachbackEvalGrid').style.display = 'grid';
          document.getElementById('teachbackFooterStrip').style.display = 'flex';

          // Understood points
          const uList = document.getElementById('tbUnderstoodList');
          if (uList) {
            uList.innerHTML = (data.understood_points || []).map(p => `• ${p}`).join('<br>') || 'Demonstrated understanding of core elements.';
          }

          // Misconceptions
          const miscBox = document.getElementById('tbMiscBox');
          const mList = document.getElementById('tbMiscList');
          if (data.misconceptions && data.misconceptions.length > 0) {
            miscBox.style.display = 'block';
            mList.innerHTML = data.misconceptions.map(m => `⚠ ${m}`).join('<br>');
          } else {
            miscBox.style.display = 'none';
          }

          // Missing points
          const missList = document.getElementById('tbMissingList');
          if (missList) {
            missList.innerHTML = (data.missing_points || []).map(m => `• ${m}`).join('<br>') || 'No critical gaps identified.';
          }

          // Next step
          const nextStepEl = document.getElementById('teachbackNextStep');
          if (nextStepEl) {
            nextStepEl.textContent = `Recommended Next Step: ${data.next_step || 'Review original animated scene'}`;
          }

          showToast('Teach-Back evaluated! Concept DNA updated.');
        } else {
          showToast('Could not evaluate explanation. Please try again.');
        }
      } catch (err) {
        if (statusEl) statusEl.style.display = 'none';
        showToast('Network error during Teach-Back evaluation.');
      }
    }

    // Personal Insights & Understanding Tracker Loader
    async function loadInsights() {
      try {
        const token = AuthManager.authToken;
        const res = await fetch('/api/insights/personal', {
          headers: token ? { 'Authorization': 'Bearer ' + token } : {}
        });
        if (!res.ok) return;
        const data = await res.json();

        // Update score ring
        const ring = document.getElementById('insightsMasteryRingScore');
        if (ring) {
          ring.textContent = (data.overall_mastery && data.overall_mastery > 0) ? `${data.overall_mastery}%` : '--';
        }

        // Render genuine concept matrix
        const tracksContainer = document.getElementById('conceptTracksContainer');
        if (tracksContainer) {
          const breakdown = data.concept_breakdown || [];
          if (breakdown.length === 0) {
            tracksContainer.innerHTML = '<div class="empty-state-atelier" style="margin:8px 0; padding:24px;"><div class="empty-glyph">📊</div><div style="font-size:14px; font-weight:700; color:var(--ink-primary);">No learning telemetry recorded yet</div><div style="font-size:12px; color:var(--ink-secondary); margin-top:4px;">Complete your first animated lesson to see your mastery matrix.</div></div>';
          } else {
            tracksContainer.innerHTML = breakdown.map(c => `
              <div class="concept-track-row">
                <div class="track-meta-line">
                  <span class="track-name">${c.concept_tag}</span>
                  <span class="track-pill ${c.status === 'Understood' ? 'pill-mastered' : (c.status === 'Needs Revision' ? 'pill-danger' : 'pill-progress')}">
                    ${c.mastery_score ? c.mastery_score + '% • ' : ''}${c.status}
                  </span>
                </div>
                <div class="track-bar-container">
                  <div class="track-bar-fill" style="width: ${c.mastery_score || 50}%; background: ${c.status === 'Understood' ? 'var(--accent-celadon)' : (c.status === 'Needs Revision' ? 'var(--accent-terracotta)' : 'var(--accent-surya)')};"></div>
                </div>
              </div>
            `).join('');
          }
        }

        // Misconceptions container
        const miscContainer = document.getElementById('misconceptionRadarContainer');
        if (miscContainer) {
          const miscs = data.diagnosed_misconceptions || [];
          if (miscs.length === 0) {
            miscContainer.innerHTML = '<div style="font-size:12px; color:var(--ink-secondary); padding:14px; background:var(--surface-tinted); border-radius:var(--radius-sm); text-align:center;">No misconceptions diagnosed in your learning history. Excellent work!</div>';
          } else {
            miscContainer.innerHTML = miscs.map(m => `
              <div class="misconception-radar-box">
                <span class="misconception-kicker">Concept: ${m.concept_tag}</span>
                <p class="misconception-body"><strong>Mental model:</strong> "${m.misconception_text}"</p>
                <div class="misconception-citation"><strong>Textbook truth:</strong> ${m.grounded_truth}</div>
              </div>
            `).join('');
          }
        }

        // Memory loop container
        const memContainer = document.getElementById('memoryLoopContainer');
        if (memContainer) {
          const mems = data.memory_loop_touchpoints || [];
          if (mems.length === 0) {
            memContainer.innerHTML = '<div style="font-size:12px; color:var(--ink-secondary); padding:14px; background:var(--surface-tinted); border-radius:var(--radius-sm); text-align:center;">All concept recall schedules are clear.</div>';
          } else {
            memContainer.innerHTML = mems.map(item => `
              <div class="journey-tile" style="margin-top:0; padding:12px;">
                <div>
                  <div style="font-weight:700; font-size:13px;">${item.concept_tag}</div>
                  <div style="font-size:11px; color:var(--ink-secondary);">Spaced recall queued • Due in ${item.interval_hours || 24}h</div>
                </div>
              </div>
            `).join('');
          }
        }

      } catch (err) {
        console.error('Error loading insights:', err);
      }
    }

    // User Profile Loader
    function loadUserProfile() {
      const user = AuthManager.user || {};
      const nameEl = document.getElementById('profileFullName');
      const emailEl = document.getElementById('profileEmail');
      const avatarEl = document.getElementById('profileAvatarLetter');

      if (nameEl) nameEl.textContent = user.full_name || 'Verified Sovereign Learner';
      if (emailEl) emailEl.textContent = user.email || 'learner@pod-siksha.edu';
      if (avatarEl) avatarEl.textContent = (user.full_name || 'L')[0].toUpperCase();

      // Load stats from concept tree
      if (currentTreeData) {
        document.getElementById('profStatUnderstood').textContent = currentTreeData.understood_count || 0;
        document.getElementById('profStatLearning').textContent = currentTreeData.learning_count || 0;
        document.getElementById('profStatRevision').textContent = currentTreeData.revision_count || 0;
        document.getElementById('profStatLessons').textContent = currentTreeData.trees ? currentTreeData.trees.length : 0;
      }
    }

    function saveLearnerPreference(key, val) {
      localStorage.setItem('ps_pref_' + key, val);
      showToast(`Saved ${key} preference: ${val}`);
    }
"""

if "CONCEPT DNA KNOWLEDGE TREE ENGINE" not in html:
    last_script_idx = html.rfind('</script>')
    if last_script_idx != -1:
        html = html[:last_script_idx] + "\n" + engine_code + "\n" + html[last_script_idx:]
        print("Injected Concept DNA Knowledge Tree Engine into index.html before last </script>.")
    else:
        print("ERROR: </script> not found in index.html")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Finished updating index.html JavaScript.")
