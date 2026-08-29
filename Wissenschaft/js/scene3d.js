/**
 * Three.js 3D Visualizer & Morphing Engine (High-Vibrancy Center-Stage Version)
 * Guarantees high-contrast visibility on all devices without dark transmission artifacts.
 */

export class Scene3D {
  constructor(containerElement) {
    this.container = containerElement;
    this.currentStage = 0;
    this.targetStage = 0;
    this.stageProgress = 0;
    this.time = 0;
    this.autoRotate = true;
    this.sidebarCollapsed = false;

    // Viewport & Model Offsets (Desktop: shift right of sidebar, Mobile/Collapsed: center)
    this.modelOffsetX = (window.innerWidth > 900) ? 2.6 : 0;
    this.targetModelOffsetX = this.modelOffsetX;

    // Camera & Zoom
    this.cameraDistance = 18;
    this.targetCameraDistance = 18;
    this.minDistance = 6;
    this.maxDistance = 35;

    // Interactive Drag Rotation
    this.mouse = {
      isDragging: false,
      prevX: 0,
      prevY: 0,
      velX: 0,
      velY: 0
    };

    this.rotations = [
      { x: 0.1, y: 0.2 }, // 0: Droplet
      { x: 0.2, y: 0.3 }, // 1: Dalton
      { x: 0.3, y: 0.1 }, // 2: Rutherford
      { x: 0.5, y: 0.2 }, // 3: Bohr
      { x: 0.25, y: 0.4 }, // 4: Orbitals
      { x: 0.2, y: 0.2 }  // 5: Epilogue
    ];

    this.currentOrbitalType = '2pz';
    this.init();
  }

  init() {
    // 1. Scene & Camera
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x040711, 0.025);

    this.camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    this.camera.position.set(0, 0, this.cameraDistance);
    this.camera.lookAt(0, 0, 0);

    // 2. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.container.appendChild(this.renderer.domElement);

    // 3. Robust High-Visibility Lighting
    this.ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    this.scene.add(this.ambientLight);

    this.pointLight1 = new THREE.PointLight(0x00f0ff, 4, 60);
    this.pointLight1.position.set(10, 12, 14);
    this.scene.add(this.pointLight1);

    this.pointLight2 = new THREE.PointLight(0xa855f7, 4, 60);
    this.pointLight2.position.set(-10, -10, 10);
    this.scene.add(this.pointLight2);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
    dirLight.position.set(5, 15, 15);
    this.scene.add(dirLight);

    // 4. Cosmic Particle Dust
    this.createCosmicDust();

    // 5. Build Stage Groups
    this.stageGroups = [
      this.createDropletStage(),     // 0
      this.createDaltonStage(),      // 1
      this.createRutherfordStage(),  // 2
      this.createBohrStage(),        // 3
      this.createOrbitalStage(),     // 4
      this.createEpilogueStage()     // 5
    ];

    this.stageGroups.forEach((group, idx) => {
      this.scene.add(group);
      group.position.x = this.modelOffsetX;
      group.position.y = 0;
      group.visible = (idx === 0);
    });

    // 6. Interactive Event Listeners
    this.setupEventListeners();

    // Start loop
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  setupEventListeners() {
    window.addEventListener('resize', this.onResize.bind(this));

    // Mouse Drag Rotation
    window.addEventListener('mousedown', (e) => {
      if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT' || e.target.closest('.story-sidebar')) {
        return;
      }
      this.mouse.isDragging = true;
      this.mouse.prevX = e.clientX;
      this.mouse.prevY = e.clientY;
      this.mouse.velX = 0;
      this.mouse.velY = 0;
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.mouse.isDragging) return;
      const deltaX = e.clientX - this.mouse.prevX;
      const deltaY = e.clientY - this.mouse.prevY;
      this.mouse.prevX = e.clientX;
      this.mouse.prevY = e.clientY;

      const rot = this.rotations[this.currentStage];
      if (rot) {
        rot.y += deltaX * 0.008;
        rot.x += deltaY * 0.008;
        this.mouse.velX = deltaX * 0.008;
        this.mouse.velY = deltaY * 0.008;
      }
    });

    window.addEventListener('mouseup', () => {
      this.mouse.isDragging = false;
    });

    // Mouse Wheel Zoom
    window.addEventListener('wheel', (e) => {
      if (e.target.closest('.story-sidebar')) return;
      this.targetCameraDistance = Math.max(
        this.minDistance,
        Math.min(this.maxDistance, this.targetCameraDistance + e.deltaY * 0.015)
      );
    }, { passive: true });
  }

  zoomIn() {
    this.targetCameraDistance = Math.max(this.minDistance, this.targetCameraDistance - 3);
  }

  zoomOut() {
    this.targetCameraDistance = Math.min(this.maxDistance, this.targetCameraDistance + 3);
  }

  resetView() {
    this.targetCameraDistance = 18;
    this.rotations.forEach(r => { r.x = 0.2; r.y = 0.3; });
  }

  toggleAutoRotate() {
    this.autoRotate = !this.autoRotate;
    return this.autoRotate;
  }

  setSidebarCollapsed(collapsed) {
    this.sidebarCollapsed = collapsed;
    this.targetModelOffsetX = (collapsed || window.innerWidth <= 900) ? 0 : 2.6;
  }

  // === BACKGROUND COSMIC PARTICLES ===
  createCosmicDust() {
    const count = 1000;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 90;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 90;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 70 - 10;

      col[i * 3] = 0.2 + Math.random() * 0.3;
      col[i * 3 + 1] = 0.7 + Math.random() * 0.3;
      col[i * 3 + 2] = 1.0;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));

    const mat = new THREE.PointsMaterial({
      size: 0.15,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending
    });

    this.cosmicDust = new THREE.Points(geo, mat);
    this.scene.add(this.cosmicDust);
  }

  // === STAGE 0: Vibrant Water Droplet & Orbiting H2O Molecules ===
  createDropletStage() {
    const group = new THREE.Group();

    // 1. Shimmering Vibrant Blue Droplet Core
    const geo = new THREE.IcosahedronGeometry(4.6, 24);
    const mat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      emissive: 0x0369a1,
      emissiveIntensity: 0.6,
      roughness: 0.15,
      metalness: 0.3,
      transparent: true,
      opacity: 0.92
    });
    this.dropletMesh = new THREE.Mesh(geo, mat);
    group.add(this.dropletMesh);

    // 2. Glowing Inner Core
    const innerGeo = new THREE.SphereGeometry(3.0, 20, 20);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.5
    });
    group.add(new THREE.Mesh(innerGeo, innerMat));

    // 3. Glowing Outer Wireframe
    const wireGeo = new THREE.IcosahedronGeometry(4.85, 12);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.45
    });
    this.dropletWire = new THREE.Mesh(wireGeo, wireMat);
    group.add(this.dropletWire);

    // 4. Orbiting Water Molecules (H2O: Red Oxygen + 2 Cyan Hydrogens)
    this.moleculesGroup = new THREE.Group();
    const oxyGeo = new THREE.SphereGeometry(0.45, 16, 16);
    const hydGeo = new THREE.SphereGeometry(0.25, 16, 16);
    const bondGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 8);

    const oxyMat = new THREE.MeshStandardMaterial({ color: 0xf43f5e, emissive: 0xe11d48, emissiveIntensity: 0.6 });
    const hydMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x0284c7, emissiveIntensity: 0.6 });
    const bondMat = new THREE.MeshBasicMaterial({ color: 0x94a3b8 });

    for (let i = 0; i < 10; i++) {
      const mol = new THREE.Group();
      const o = new THREE.Mesh(oxyGeo, oxyMat);
      const h1 = new THREE.Mesh(hydGeo, hydMat);
      const h2 = new THREE.Mesh(hydGeo, hydMat);
      const b1 = new THREE.Mesh(bondGeo, bondMat);
      const b2 = new THREE.Mesh(bondGeo, bondMat);

      h1.position.set(0.55, 0.35, 0);
      h2.position.set(-0.55, 0.35, 0);
      b1.position.set(0.28, 0.18, 0);
      b1.rotation.z = -Math.PI / 4;
      b2.position.set(-0.28, 0.18, 0);
      b2.rotation.z = Math.PI / 4;

      mol.add(o, h1, h2, b1, b2);

      const angle = (i / 10) * Math.PI * 2;
      const radius = 6.8 + (i % 2) * 1.2;
      mol.position.set(Math.cos(angle) * radius, Math.sin(angle) * radius, (Math.random() - 0.5) * 3);
      this.moleculesGroup.add(mol);
    }
    group.add(this.moleculesGroup);

    return group;
  }

  // === STAGE 1: Dalton Billiard Balls Containment Box ===
  createDaltonStage() {
    const group = new THREE.Group();

    this.daltonCount = 70;
    this.daltonParticles = [];
    this.daltonBoxSize = 7.0;

    const sphereGeo = new THREE.SphereGeometry(0.55, 20, 20);
    const matA = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      metalness: 0.5,
      roughness: 0.2,
      emissive: 0x0284c7,
      emissiveIntensity: 0.6
    });
    const matB = new THREE.MeshStandardMaterial({
      color: 0xc084fc,
      metalness: 0.5,
      roughness: 0.2,
      emissive: 0x9333ea,
      emissiveIntensity: 0.6
    });

    for (let i = 0; i < this.daltonCount; i++) {
      const isA = i % 2 === 0;
      const mesh = new THREE.Mesh(sphereGeo, isA ? matA : matB);
      mesh.position.set(
        (Math.random() - 0.5) * this.daltonBoxSize * 1.8,
        (Math.random() - 0.5) * this.daltonBoxSize * 1.8,
        (Math.random() - 0.5) * this.daltonBoxSize * 1.4
      );
      const vel = new THREE.Vector3(
        (Math.random() - 0.5) * 0.09,
        (Math.random() - 0.5) * 0.09,
        (Math.random() - 0.5) * 0.09
      );
      this.daltonParticles.push({ mesh, vel });
      group.add(mesh);
    }

    // Glowing Containment Cube
    const boxGeo = new THREE.BoxGeometry(
      this.daltonBoxSize * 2,
      this.daltonBoxSize * 2,
      this.daltonBoxSize * 1.6
    );
    const boxWireMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true,
      transparent: true,
      opacity: 0.35
    });
    group.add(new THREE.Mesh(boxGeo, boxWireMat));

    return group;
  }

  // === STAGE 2: Rutherford Nucleus & Gold Foil Scattering ===
  createRutherfordStage() {
    const group = new THREE.Group();

    // Central Dense Nucleus (Protons & Neutrons)
    this.nucleusGroup = new THREE.Group();
    const nucleonGeo = new THREE.SphereGeometry(0.42, 18, 18);
    const protonMat = new THREE.MeshStandardMaterial({
      color: 0xf43f5e,
      emissive: 0xe11d48,
      emissiveIntensity: 0.9,
      roughness: 0.2
    });
    const neutronMat = new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      emissive: 0x475569,
      emissiveIntensity: 0.4,
      roughness: 0.2
    });

    for (let i = 0; i < 30; i++) {
      const isProton = i % 2 === 0;
      const nucleon = new THREE.Mesh(nucleonGeo, isProton ? protonMat : neutronMat);
      const r = Math.random() * 0.9;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;
      nucleon.position.set(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      );
      this.nucleusGroup.add(nucleon);
    }
    group.add(this.nucleusGroup);

    // Atom Boundary Ring (Demonstrates 99.999% Empty Space)
    const ringGeo = new THREE.RingGeometry(7.8, 8.0, 72);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35
    });
    const atomBoundary = new THREE.Mesh(ringGeo, ringMat);
    group.add(atomBoundary);

    // Gold Foil Detector Screen
    const detectorGeo = new THREE.CylinderGeometry(9.0, 9.0, 5.5, 32, 1, true, Math.PI * 0.6, Math.PI * 0.8);
    const detectorMat = new THREE.MeshBasicMaterial({
      color: 0x34d399,
      wireframe: true,
      transparent: true,
      opacity: 0.28,
      side: THREE.DoubleSide
    });
    group.add(new THREE.Mesh(detectorGeo, detectorMat));

    // Alpha Particle Stream
    this.alphaParticles = [];
    const alphaGeo = new THREE.SphereGeometry(0.24, 14, 14);
    const alphaMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24 });

    for (let i = 0; i < 40; i++) {
      const p = new THREE.Mesh(alphaGeo, alphaMat);
      this.resetAlphaParticle(p);
      p.position.x = -18 - Math.random() * 12;
      this.alphaParticles.push(p);
      group.add(p);
    }

    return group;
  }

  resetAlphaParticle(p) {
    p.position.x = -18;
    p.position.y = (Math.random() - 0.5) * 9;
    p.position.z = (Math.random() - 0.5) * 3;
    p.userData = {
      vx: 0.38 + Math.random() * 0.08,
      vy: 0,
      vz: 0,
      deflected: false
    };
  }

  // === STAGE 3: Bohr Quantized Rings & Quantum Jumps ===
  createBohrStage() {
    const group = new THREE.Group();

    // Central Glowing Nucleus
    const core = new THREE.Mesh(
      new THREE.SphereGeometry(1.0, 32, 32),
      new THREE.MeshStandardMaterial({ color: 0xf43f5e, emissive: 0xf43f5e, emissiveIntensity: 1.5 })
    );
    group.add(core);

    // Quantized Orbits (n = 1, 2, 3, 4)
    this.bohrRadii = [2.2, 4.4, 6.6, 8.8];
    this.bohrRings = [];

    this.bohrRadii.forEach((r, idx) => {
      const ringGeo = new THREE.RingGeometry(r - 0.05, r + 0.05, 90);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.45
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2.2;
      group.add(ring);
      this.bohrRings.push(ring);
    });

    // Orbiting Electron with Glow
    const electronGeo = new THREE.SphereGeometry(0.35, 24, 24);
    const electronMat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00f0ff,
      emissiveIntensity: 2.0
    });
    this.bohrElectron = new THREE.Mesh(electronGeo, electronMat);
    this.bohrElectronState = {
      level: 2,
      targetLevel: 2,
      currentRadius: this.bohrRadii[2],
      angle: 0,
      speed: 0.038
    };
    group.add(this.bohrElectron);

    // Emitted Photon Wave Packets
    this.photons = [];
    return group;
  }

  triggerBohrJump(fromLevel, toLevel) {
    if (this.bohrElectronState) {
      this.bohrElectronState.targetLevel = toLevel;
      this.spawnPhoton(fromLevel, toLevel);
    }
  }

  spawnPhoton(fromLevel, toLevel) {
    const isEmission = fromLevel > toLevel;
    const colors = [0xf43f5e, 0x00f0ff, 0x818cf8, 0xa855f7];
    const photonColor = colors[Math.abs(fromLevel - toLevel) % colors.length];

    const waveGeo = new THREE.RingGeometry(0.2, 0.4, 32);
    const waveMat = new THREE.MeshBasicMaterial({
      color: photonColor,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 1
    });
    const wave = new THREE.Mesh(waveGeo, waveMat);
    wave.position.copy(this.bohrElectron.position);

    const dir = wave.position.clone().normalize();
    if (!isEmission) dir.negate();

    wave.userData = {
      dir: dir.multiplyScalar(0.28),
      scaleGrowth: 0.15,
      life: 0,
      maxLife: 45
    };

    this.groupBohr.add(wave);
    this.photons.push(wave);
  }

  // === STAGE 4: Quantum Orbitals (Schrödinger Wavefunctions) ===
  createOrbitalStage() {
    const group = new THREE.Group();
    this.orbitalPointsCount = 20000;
    this.orbitalGeo = new THREE.BufferGeometry();

    const positions = new Float32Array(this.orbitalPointsCount * 3);
    const colors = new Float32Array(this.orbitalPointsCount * 3);

    this.orbitalGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.orbitalGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    this.orbitalMat = new THREE.PointsMaterial({
      size: 0.14,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    this.orbitalCloud = new THREE.Points(this.orbitalGeo, this.orbitalMat);
    group.add(this.orbitalCloud);

    // 3D Coordinate Axis Rings for Spatial Guidance
    const axisMatX = new THREE.MeshBasicMaterial({ color: 0xf43f5e, wireframe: true, transparent: true, opacity: 0.2 });
    const axisMatY = new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true, transparent: true, opacity: 0.2 });
    const axisMatZ = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.2 });

    const ringX = new THREE.Mesh(new THREE.RingGeometry(6.5, 6.55, 64), axisMatX);
    const ringY = new THREE.Mesh(new THREE.RingGeometry(6.5, 6.55, 64), axisMatY);
    const ringZ = new THREE.Mesh(new THREE.RingGeometry(6.5, 6.55, 64), axisMatZ);
    ringX.rotation.y = Math.PI / 2;
    ringY.rotation.x = Math.PI / 2;
    group.add(ringX, ringY, ringZ);

    this.computeOrbitalPoints('2pz');
    return group;
  }

  setOrbitalType(type) {
    this.currentOrbitalType = type;
    this.computeOrbitalPoints(type);
  }

  computeOrbitalPoints(type) {
    if (!this.orbitalGeo) return;
    const pos = this.orbitalGeo.attributes.position.array;
    const col = this.orbitalGeo.attributes.color.array;

    let index = 0;
    let attempts = 0;
    const maxAttempts = 400000;

    // Monte Carlo Sampling of exact Hydrogen Wavefunctions |psi|^2
    while (index < this.orbitalPointsCount && attempts < maxAttempts) {
      attempts++;
      const x = (Math.random() - 0.5) * 15;
      const y = (Math.random() - 0.5) * 15;
      const z = (Math.random() - 0.5) * 15;
      const r = Math.sqrt(x*x + y*y + z*z);
      if (r < 0.1 || r > 8.0) continue;

      const theta = Math.acos(z / r);
      const phi = Math.atan2(y, x);

      let prob = 0;
      let phase = 1;

      if (type === '1s') {
        prob = Math.exp(-1.3 * r) * 1.8;
        phase = 1;
      } else if (type === '2s') {
        const psi = (2 - r) * Math.exp(-0.65 * r);
        prob = psi * psi * 1.5;
        phase = Math.sign(2 - r);
      } else if (type === '2pz') {
        const psi = r * Math.exp(-0.75 * r) * Math.cos(theta);
        prob = psi * psi * 4.5;
        phase = Math.sign(Math.cos(theta));
      } else if (type === '2px') {
        const psi = r * Math.exp(-0.75 * r) * Math.sin(theta) * Math.cos(phi);
        prob = psi * psi * 4.5;
        phase = Math.sign(Math.sin(theta) * Math.cos(phi));
      } else if (type === '3dz2') {
        const psi = (r * r) * Math.exp(-0.65 * r) * (3 * Math.cos(theta) * Math.cos(theta) - 1);
        prob = psi * psi * 0.9;
        phase = Math.sign(3 * Math.cos(theta) * Math.cos(theta) - 1);
      } else if (type === '3dxy') {
        const psi = (r * r) * Math.exp(-0.65 * r) * Math.sin(theta) * Math.sin(theta) * Math.sin(2 * phi);
        prob = psi * psi * 2.8;
        phase = Math.sign(Math.sin(2 * phi));
      }

      if (Math.random() < prob) {
        pos[index * 3] = x;
        pos[index * 3 + 1] = y;
        pos[index * 3 + 2] = z;

        if (phase >= 0) {
          col[index * 3] = 0.0;     // R
          col[index * 3 + 1] = 0.94; // G
          col[index * 3 + 2] = 1.0;  // B (Cyan)
        } else {
          col[index * 3] = 0.9;     // R
          col[index * 3 + 1] = 0.4;  // G
          col[index * 3 + 2] = 1.0;  // B (Purple)
        }
        index++;
      }
    }

    this.orbitalGeo.attributes.position.needsUpdate = true;
    this.orbitalGeo.attributes.color.needsUpdate = true;
  }

  // === STAGE 5: Epilogue / Multi-Model Superposition ===
  createEpilogueStage() {
    const group = new THREE.Group();

    const torusGeo1 = new THREE.TorusGeometry(4.8, 0.1, 16, 100);
    const torusGeo2 = new THREE.TorusGeometry(3.6, 0.1, 16, 100);
    const torusGeo3 = new THREE.TorusGeometry(2.4, 0.1, 16, 100);

    const mat1 = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00f0ff, emissiveIntensity: 0.9 });
    const mat2 = new THREE.MeshStandardMaterial({ color: 0xc084fc, emissive: 0xc084fc, emissiveIntensity: 0.9 });
    const mat3 = new THREE.MeshStandardMaterial({ color: 0xfbbf24, emissive: 0xfbbf24, emissiveIntensity: 0.9 });

    this.epilogueRings = [
      new THREE.Mesh(torusGeo1, mat1),
      new THREE.Mesh(torusGeo2, mat2),
      new THREE.Mesh(torusGeo3, mat3)
    ];
    this.epilogueRings.forEach(ring => group.add(ring));

    // Floating Crystal Core
    this.epilogueCore = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.4, 2),
      new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x38bdf8, emissiveIntensity: 0.5, wireframe: true })
    );
    group.add(this.epilogueCore);

    return group;
  }

  // === STAGE PROGRESSION & POSITIONING ===
  setStage(stageIndex) {
    this.targetStage = Math.max(0, Math.min(5, stageIndex));
    this.stageGroups.forEach((g, idx) => {
      g.visible = (idx === this.targetStage);
    });
    this.currentStage = this.targetStage;
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);

    // Dynamic model offset adjustment
    this.targetModelOffsetX = (this.sidebarCollapsed || window.innerWidth <= 900) ? 0 : 2.6;
  }

  // === MAIN RENDER LOOP ===
  animate() {
    requestAnimationFrame(this.animate);
    this.time += 0.015;

    // Smooth Camera Distance & Model Offset lerp
    this.cameraDistance += (this.targetCameraDistance - this.cameraDistance) * 0.08;
    this.camera.position.z = this.cameraDistance;

    this.modelOffsetX += (this.targetModelOffsetX - this.modelOffsetX) * 0.08;

    // Sync all stage positions
    this.stageGroups.forEach(g => {
      g.position.x = this.modelOffsetX;
    });

    // Inertial Damping for mouse drag
    if (!this.mouse.isDragging) {
      this.mouse.velX *= 0.92;
      this.mouse.velY *= 0.92;
      const rot = this.rotations[this.currentStage];
      if (rot) {
        rot.y += this.mouse.velX;
        rot.x += this.mouse.velY;
      }
    }

    // Auto-rotation when enabled
    if (this.autoRotate) {
      const rot = this.rotations[this.currentStage];
      if (rot) rot.y += 0.005;
    }

    // Cosmic Dust rotation
    if (this.cosmicDust) {
      this.cosmicDust.rotation.y = this.time * 0.012;
    }

    // Active Stage Rotation
    const currentRot = this.rotations[this.currentStage];

    // --- STAGE 0: Droplet ---
    if (this.stageGroups[0].visible) {
      this.stageGroups[0].rotation.x = currentRot.x;
      this.stageGroups[0].rotation.y = currentRot.y;
      this.dropletMesh.rotation.y = this.time * 0.2;
      this.dropletWire.rotation.y = -this.time * 0.15;
      this.moleculesGroup.rotation.z = this.time * 0.1;
    }

    // --- STAGE 1: Dalton Particles ---
    if (this.stageGroups[1].visible) {
      this.stageGroups[1].rotation.x = currentRot.x;
      this.stageGroups[1].rotation.y = currentRot.y;

      const b = this.daltonBoxSize;
      this.daltonParticles.forEach(p => {
        p.mesh.position.add(p.vel);
        if (Math.abs(p.mesh.position.x) > b * 0.9) { p.vel.x *= -1; p.mesh.position.x = Math.sign(p.mesh.position.x) * b * 0.9; }
        if (Math.abs(p.mesh.position.y) > b * 0.9) { p.vel.y *= -1; p.mesh.position.y = Math.sign(p.mesh.position.y) * b * 0.9; }
        if (Math.abs(p.mesh.position.z) > b * 0.7) { p.vel.z *= -1; p.mesh.position.z = Math.sign(p.mesh.position.z) * b * 0.7; }
      });
    }

    // --- STAGE 2: Rutherford Atom ---
    if (this.stageGroups[2].visible) {
      this.stageGroups[2].rotation.x = currentRot.x;
      this.stageGroups[2].rotation.y = currentRot.y;
      this.nucleusGroup.rotation.x = this.time * 0.3;
      this.nucleusGroup.rotation.y = this.time * 0.5;

      this.alphaParticles.forEach(p => {
        p.position.x += p.userData.vx;
        p.position.y += p.userData.vy;
        p.position.z += p.userData.vz;

        const distSq = p.position.x * p.position.x + p.position.y * p.position.y + p.position.z * p.position.z;
        if (distSq < 14.0 && !p.userData.deflected) {
          const dist = Math.sqrt(distSq);
          const force = 0.22 / (dist * dist + 0.1);
          p.userData.vy += (p.position.y / dist) * force * 3.8;
          p.userData.vx += (p.position.x / dist) * force * 1.8;
          p.userData.deflected = true;
        }

        if (p.position.x > 18 || Math.abs(p.position.y) > 14) {
          this.resetAlphaParticle(p);
        }
      });
    }

    // --- STAGE 3: Bohr Atom ---
    if (this.stageGroups[3].visible) {
      this.stageGroups[3].rotation.x = currentRot.x;
      this.stageGroups[3].rotation.y = currentRot.y;

      const state = this.bohrElectronState;
      const targetR = this.bohrRadii[state.targetLevel];
      state.currentRadius += (targetR - state.currentRadius) * 0.08;

      state.angle += state.speed;
      const angle = state.angle;
      const tilt = Math.PI / 2.2;

      this.bohrElectron.position.set(
        Math.cos(angle) * state.currentRadius,
        Math.sin(angle) * state.currentRadius * Math.cos(tilt),
        Math.sin(angle) * state.currentRadius * Math.sin(tilt)
      );

      // Photons expanding wave packets
      for (let i = this.photons.length - 1; i >= 0; i--) {
        const ph = this.photons[i];
        ph.position.add(ph.userData.dir);
        ph.scale.addScalar(ph.userData.scaleGrowth);
        ph.userData.life++;
        ph.material.opacity = 1 - (ph.userData.life / ph.userData.maxLife);
        if (ph.userData.life >= ph.userData.maxLife) {
          this.groupBohr.remove(ph);
          this.photons.splice(i, 1);
        }
      }
    }

    // --- STAGE 4: Quantum Orbitals ---
    if (this.stageGroups[4].visible) {
      this.stageGroups[4].rotation.x = currentRot.x;
      this.stageGroups[4].rotation.y = currentRot.y;
      this.orbitalMat.size = 0.13 + Math.sin(this.time * 2.5) * 0.015;
    }

    // --- STAGE 5: Epilogue Superposition ---
    if (this.stageGroups[5].visible) {
      this.stageGroups[5].rotation.x = currentRot.x;
      this.stageGroups[5].rotation.y = currentRot.y;
      this.epilogueRings[0].rotation.x = this.time * 0.4;
      this.epilogueRings[0].rotation.y = this.time * 0.25;
      this.epilogueRings[1].rotation.y = -this.time * 0.35;
      this.epilogueRings[1].rotation.z = this.time * 0.2;
      this.epilogueRings[2].rotation.z = this.time * 0.5;
      this.epilogueCore.rotation.x = this.time * 0.6;
      this.epilogueCore.rotation.y = this.time * 0.4;
    }

    this.renderer.render(this.scene, this.camera);
  }
}
