/**
 * Interactive Lab Widgets & Epistemological Simulations
 */

import { sound } from './audio.js';

export function setupExperiments(scene3D) {
  setupDaltonExperiment(scene3D);
  setupRutherfordExperiment(scene3D);
  setupBohrExperiment(scene3D);
  setupOrbitalExperiment(scene3D);
  setupCompassExperiment();
}

// === 1. DALTON GAS EXPERIMENT ===
function setupDaltonExperiment(scene3D) {
  const tempSlider = document.getElementById('dalton-temp');
  const pressureVal = document.getElementById('dalton-pressure');
  const tempVal = document.getElementById('dalton-temp-val');

  if (!tempSlider) return;

  tempSlider.addEventListener('input', (e) => {
    const temp = parseInt(e.target.value);
    tempVal.textContent = `${temp} K`;
    
    // Calculate pressure based on ideal gas law P ~ T
    const pressure = (temp * 0.34).toFixed(1);
    pressureVal.textContent = `${pressure} kPa`;

    // Update particle velocities in 3D scene
    const speedFactor = (temp / 300) * 0.09;
    if (scene3D.daltonParticles) {
      scene3D.daltonParticles.forEach(p => {
        p.vel.normalize().multiplyScalar(speedFactor);
      });
    }

    sound.playClick(200 + temp, 0.02);
  });
}

// === 2. RUTHERFORD GOLD FOIL EXPERIMENT ===
function setupRutherfordExperiment(scene3D) {
  const btnFire = document.getElementById('btn-rutherford-fire');
  const countPassed = document.getElementById('count-passed');
  const countDeflected = document.getElementById('count-deflected');
  const countReflected = document.getElementById('count-reflected');

  if (!btnFire) return;

  let passed = 0;
  let deflected = 0;
  let reflected = 0;

  btnFire.addEventListener('click', () => {
    btnFire.disabled = true;
    btnFire.textContent = "Strahle Alpha-Teilchen...";

    let burstCount = 0;
    const interval = setInterval(() => {
      burstCount++;
      // Spawn extra alpha wave in 3D scene
      if (scene3D.alphaParticles) {
        scene3D.alphaParticles.forEach(p => {
          if (p.position.x > 15) {
            scene3D.resetAlphaParticle(p);
          }
        });
      }

      // Statistical simulation matching Rutherford's experiment (1 in 8000 reflected)
      const roll = Math.random();
      if (roll < 0.94) {
        passed += 100;
      } else if (roll < 0.998) {
        deflected += 10;
        sound.playScatter();
      } else {
        reflected += 1;
        sound.playScatter();
      }

      countPassed.textContent = passed.toLocaleString('de-DE');
      countDeflected.textContent = deflected.toLocaleString('de-DE');
      countReflected.textContent = reflected.toLocaleString('de-DE');

      if (burstCount >= 15) {
        clearInterval(interval);
        btnFire.disabled = false;
        btnFire.textContent = "Alpha-Teilchen abfeuern";
      }
    }, 100);
  });
}

// === 3. BOHR QUANTUM JUMP & SPECTRUM ===
function setupBohrExperiment(scene3D) {
  const chips = document.querySelectorAll('.bohr-jump-chip');
  const energyVal = document.getElementById('bohr-energy-val');
  const wavelengthVal = document.getElementById('bohr-wave-val');
  const spectralBar = document.getElementById('bohr-spectrum');

  const transitions = {
    '3-2': { from: 2, to: 1, lambda: '656 nm (Rot)', energy: '1.89 eV', color: '#f43f5e', left: '85%' },
    '4-2': { from: 3, to: 1, lambda: '486 nm (Türkis)', energy: '2.55 eV', color: '#00f0ff', left: '55%' },
    '5-2': { from: 3, to: 1, lambda: '434 nm (Blau)', energy: '2.86 eV', color: '#818cf8', left: '35%' },
    '6-2': { from: 3, to: 1, lambda: '410 nm (Violett)', energy: '3.02 eV', color: '#a855f7', left: '15%' }
  };

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      const transKey = chip.dataset.transition;
      const data = transitions[transKey];
      if (!data) return;

      energyVal.textContent = data.energy;
      wavelengthVal.textContent = data.lambda;

      // Update 3D scene electron transition & expanding photon ring
      scene3D.triggerBohrJump(data.from, data.to);

      // Play audio chime
      sound.playQuantumJump(parseInt(transKey.split('-')[0]));

      // Update spectral line visual
      if (spectralBar) {
        let line = spectralBar.querySelector('.active-spectral-line');
        if (!line) {
          line = document.createElement('div');
          line.className = 'spectral-line active-spectral-line';
          spectralBar.appendChild(line);
        }
        line.style.left = data.left;
        line.style.backgroundColor = data.color;
        line.style.color = data.color;
      }
    });
  });
}

// === 4. QUANTUM ORBITAL CONTROLLER ===
function setupOrbitalExperiment(scene3D) {
  const buttons = document.querySelectorAll('.orbital-btn');
  const orbitalName = document.getElementById('orbital-current-name');
  const orbitalDesc = document.getElementById('orbital-current-desc');
  const orbitalNodes = document.getElementById('orbital-current-nodes');

  const orbitalInfo = {
    '1s': {
      title: '1s Orbital (Grundzustand)',
      desc: 'Kugelsymmetrische Aufenthaltswahrscheinlichkeit. Höchste Dichte am Kern.',
      nodes: '0 Knotenebenen'
    },
    '2s': {
      title: '2s Orbital (Kugelsphäre mit Knotenfläche)',
      desc: 'Zwei konzentrische Kugelschalen, getrennt durch eine radiale Knotensphäre bei r=2 a₀.',
      nodes: '1 radiale Knotensphäre'
    },
    '2pz': {
      title: '2p_z Orbital (Hantelform)',
      desc: 'Zwei keulenförmige Wahrscheinlichkeitskeulen entlang der z-Achse. Getrennt durch die xy-Knotenebene (z=0).',
      nodes: '1 Knotenebene (z=0)'
    },
    '2px': {
      title: '2p_x Orbital (Orientiert)',
      desc: 'Hantelform entlang der x-Achse. Bildet mit 2py und 2pz das p-Niveau und ermöglicht Hybridisierung (sp², sp³).',
      nodes: '1 Knotenebene (x=0)'
    },
    '3dz2': {
      title: '3d_{z²} Orbital (Komplexe Geometrie)',
      desc: 'Zwei Hauptkeulen entlang der z-Achse mit einem ringförmigen Torus („Donut“) in der Äquatorebene.',
      nodes: '2 Kegel-Knotenflächen'
    },
    '3dxy': {
      title: '3d_{xy} Orbital (Kleeblatt)',
      desc: 'Vier keulenförmige Lappen in den Quadranten der xy-Ebene.',
      nodes: '2 senkrechte Knotenebenen'
    }
  };

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const type = btn.dataset.orbital;
      scene3D.setOrbitalType(type);
      sound.playQuantumShimmer();

      const info = orbitalInfo[type];
      if (info) {
        if (orbitalName) orbitalName.textContent = info.title;
        if (orbitalDesc) orbitalDesc.textContent = info.desc;
        if (orbitalNodes) orbitalNodes.textContent = info.nodes;
      }
    });
  });
}

// === 5. EPISTEMOLOGY MODEL COMPASS ===
function setupCompassExperiment() {
  const cards = document.querySelectorAll('.matrix-card');
  const resultBox = document.getElementById('compass-result');
  const resultTitle = document.getElementById('compass-result-title');
  const resultModel = document.getElementById('compass-result-model');
  const resultReason = document.getElementById('compass-result-reason');
  const resultQuote = document.getElementById('compass-result-quote');

  const problems = {
    'tire': {
      title: 'Reifendruck bei 80°C auf der Autobahn berechnen',
      model: 'Dalton / Ideales Gasgesetz (Klassisch)',
      reason: 'Perfekt geeignet! Die Annahme von starren, unteilbaren Billardkugeln liefert mit minimalem Rechenaufwand ein Ergebnis mit 99.9% Genauigkeit.',
      quote: '„Mit Quantenmechanik Reifendruck zu berechnen, ist wie mit einem Laser ein Streichholz anzuzünden.“'
    },
    'laser': {
      title: 'Funktionsweise eines Lasers & Spektrallinien erklären',
      model: 'Bohr-Modell (Diskrete Energieniveaus)',
      reason: 'Das Bohr-Modell reicht hier völlig aus. Quantensprünge zwischen diskreten Energieniveaus erklären stimulierte Emission und monochromatische Lichtwellen perfekt.',
      quote: '„Das Bohr-Modell ist physikalisch falsch (keine Planetenbahnen), aber für Spektroskopie phänomenal nützlich.“'
    },
    'water': {
      title: 'Chemische Bindung & Dipol-Eigenschaft von Wasser erklären',
      model: 'Orbitaltheorie & Hybridisierung (sp³)',
      reason: 'Weder Dalton noch Bohr können den Bindungswinkel von 104.5° erklären. Erst die räumliche Überlappung von Elektronen-Wahrscheinlichkeitswolken löst das Rätsel.',
      quote: '„Hier stoßen alle anschaulichen Modelle an ihre absolute Grenze.“'
    },
    'semiconductor': {
      title: 'Transistoren in modernen 3nm-Computerchips entwickeln',
      model: 'Quantenmechanik & Quanten-Tunneleffekt',
      reason: 'Bei Strukturgrößen von wenigen Atomen tunneln Elektronen schlicht durch Barrieren hindurch. Nur die Schrödinger-Gleichung und Bandstrukturtheorie erlauben die Chipfertigung.',
      quote: '„Ohne das Aufgeben klassischer Anschauung gäbe es kein Smartphone.“'
    }
  };

  cards.forEach(card => {
    card.addEventListener('click', () => {
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      const problemKey = card.dataset.problem;
      const data = problems[problemKey];
      if (!data) return;

      sound.playClick(440, 0.04);

      if (resultBox) resultBox.style.display = 'block';
      if (resultTitle) resultTitle.textContent = data.title;
      if (resultModel) resultModel.textContent = `Optimale Modell-Wahl: ${data.model}`;
      if (resultReason) resultReason.textContent = data.reason;
      if (resultQuote) resultQuote.textContent = data.quote;
    });
  });
}
