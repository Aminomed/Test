/**
 * Main Application Controller & Scrollytelling Engine
 * Manages Sidebar toggle, Quick-Switcher Tabs, Viewport Controls and HUD.
 */

import { Scene3D } from './scene3d.js';
import { setupExperiments } from './experiments.js';
import { sound } from './audio.js';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize 3D Visualizer
  const container = document.getElementById('webgl-container');
  const scene3D = new Scene3D(container);

  // 2. Initialize Interactive Experiments
  setupExperiments(scene3D);

  // 3. DOM References
  const hudScale = document.getElementById('hud-scale');
  const hudEpoch = document.getElementById('hud-epoch');
  const hudParadigm = document.getElementById('hud-paradigm');
  const progressBar = document.getElementById('hud-progress-bar');
  const btnAudio = document.getElementById('btn-audio-toggle');
  const sidebar = document.getElementById('story-sidebar');
  const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
  const btnFocusMode = document.getElementById('btn-focus-mode');
  const tabBtns = document.querySelectorAll('.tab-btn');
  const viewportModelName = document.getElementById('viewport-model-name');

  // 3D Viewport Controls
  const btnZoomIn = document.getElementById('btn-zoom-in');
  const btnZoomOut = document.getElementById('btn-zoom-out');
  const btnResetView = document.getElementById('btn-reset-view');
  const btnAutoRotate = document.getElementById('btn-autorotate');

  // Metadata for each stage
  const stageData = [
    { name: 'Makroskopische Flüssigkeit', scale: '10⁰ m (1 Meter)', epoch: 'Gegenwart (Makrowelt)', paradigm: 'Klassische Anschauung' },
    { name: 'Dalton Kugelmodell', scale: '10⁻⁹ m (1 Nanometer)', epoch: '400 v.Chr. / 1803 (Dalton)', paradigm: 'Mechanistische Bausteine' },
    { name: 'Rutherford Kern-Hülle-Atom', scale: '10⁻¹⁴ m (10 Femtometer)', epoch: '1911 (Rutherford)', paradigm: 'Planetarisches Kern-Hülle-Modell' },
    { name: 'Bohrsches Quantenmodell', scale: '10⁻¹⁰ m (0.1 Nanometer)', epoch: '1913 (Niels Bohr)', paradigm: 'Quantisierte Bahnen & Spektren' },
    { name: 'Schrödinger/Heisenberg Orbitale', scale: '10⁻¹⁵ m (Quantenunschärfe)', epoch: '1925+ (Quantenmechanik)', paradigm: 'Probabilistische Orbitale (|ψ|²)' },
    { name: 'Metatheorie & Erkenntnissynthese', scale: 'Metatheorie', epoch: 'Wissenschaftsphilosophie', paradigm: 'Modellpluralismus (Popper/Kuhn/Box)' }
  ];

  // 4. Scrollytelling Observer & Scroll Event
  const sections = document.querySelectorAll('.story-step');

  function updateScrollState() {
    const scrollY = window.scrollY;
    const windowH = window.innerHeight;
    const docH = document.documentElement.scrollHeight - windowH;
    const overallProgress = Math.min(1, Math.max(0, scrollY / (docH || 1)));

    if (progressBar) {
      progressBar.style.width = `${(overallProgress * 100).toFixed(1)}%`;
    }

    // Determine current active section
    let activeIndex = 0;
    let minDistance = Infinity;

    sections.forEach((section, index) => {
      const rect = section.getBoundingClientRect();
      const centerDist = Math.abs(rect.top + rect.height / 2 - windowH / 2);
      if (centerDist < minDistance) {
        minDistance = centerDist;
        activeIndex = index;
      }
    });

    // Update 3D scene stage
    scene3D.setStage(activeIndex);

    // Update HUD Metrics
    const info = stageData[activeIndex];
    if (info) {
      if (hudScale) hudScale.textContent = info.scale;
      if (hudEpoch) hudEpoch.textContent = info.epoch;
      if (hudParadigm) hudParadigm.textContent = info.paradigm;
      if (viewportModelName) viewportModelName.textContent = info.name;
    }

    // Update Top Navigation Tabs
    tabBtns.forEach((tab, idx) => {
      if (idx === activeIndex) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
  }

  window.addEventListener('scroll', updateScrollState, { passive: true });
  updateScrollState();

  // 5. Quick Switcher Tabs Click Handler
  tabBtns.forEach((tab) => {
    tab.addEventListener('click', () => {
      const targetIndex = parseInt(tab.dataset.stage);
      const targetSection = document.getElementById(`step-${targetIndex}`);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth' });
      }
      scene3D.setStage(targetIndex);
      tabBtns.forEach((t, i) => t.classList.toggle('active', i === targetIndex));

      const info = stageData[targetIndex];
      if (info && viewportModelName) {
        viewportModelName.textContent = info.name;
      }

      sound.playClick(350 + targetIndex * 60, 0.03);
    });
  });

  // 6. Sidebar Collapse / Focus Mode Toggle
  function toggleSidebar(forceState) {
    const isCollapsed = forceState !== undefined 
      ? forceState 
      : sidebar.classList.toggle('collapsed');

    if (forceState !== undefined) {
      if (forceState) sidebar.classList.add('collapsed');
      else sidebar.classList.remove('collapsed');
    }

    scene3D.setSidebarCollapsed(sidebar.classList.contains('collapsed'));

    const isNowCollapsed = sidebar.classList.contains('collapsed');
    if (btnToggleSidebar) {
      btnToggleSidebar.innerHTML = isNowCollapsed 
        ? `<span>📖</span> Text einblenden` 
        : `<span>👁️</span> Fokus-Modus`;
    }
    if (btnFocusMode) {
      btnFocusMode.title = isNowCollapsed ? 'Textleiste einblenden' : 'Fokus: Text ausblenden';
    }
  }

  if (btnToggleSidebar) {
    btnToggleSidebar.addEventListener('click', () => toggleSidebar());
  }
  if (btnFocusMode) {
    btnFocusMode.addEventListener('click', () => toggleSidebar());
  }

  // 7. 3D Viewport Controls (Zoom, Reset, Auto-Rotate)
  if (btnZoomIn) {
    btnZoomIn.addEventListener('click', () => {
      scene3D.zoomIn();
      sound.playClick(500, 0.02);
    });
  }
  if (btnZoomOut) {
    btnZoomOut.addEventListener('click', () => {
      scene3D.zoomOut();
      sound.playClick(400, 0.02);
    });
  }
  if (btnResetView) {
    btnResetView.addEventListener('click', () => {
      scene3D.resetView();
      sound.playClick(600, 0.03);
    });
  }
  if (btnAutoRotate) {
    btnAutoRotate.addEventListener('click', () => {
      const isRotating = scene3D.toggleAutoRotate();
      btnAutoRotate.style.borderColor = isRotating ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.1)';
      btnAutoRotate.style.color = isRotating ? 'var(--accent-cyan)' : 'var(--text-muted)';
      sound.playClick(550, 0.02);
    });
  }

  // 8. Audio Toggle
  if (btnAudio) {
    btnAudio.addEventListener('click', () => {
      const isPlaying = sound.toggle();
      btnAudio.innerHTML = isPlaying 
        ? `<span>🔊</span> Sound: An` 
        : `<span>🔇</span> Sound: Aus`;
      btnAudio.style.borderColor = isPlaying ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.15)';
    });
  }
});
