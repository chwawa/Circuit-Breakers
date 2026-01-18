import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

export function createScene(gl, width, height) {
  /* ---------------- Scene ---------------- */
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x202020);

  /* ---------------- Camera ---------------- */
  // Use passed width/height for correct aspect ratio in Expo
  const camera = new THREE.PerspectiveCamera(
    60,
    width / height,
    0.1,
    100
  );
  camera.position.set(0, 1.5, 4);

  /* ---------------- Renderer ---------------- */
  const renderer = new THREE.WebGLRenderer({
    gl,
    antialias: true,
  });
  renderer.setSize(width, height);
  // Important for clear rendering on mobile screens
  renderer.setPixelRatio(window.devicePixelRatio || 1);

  /* ---------------- Lights ---------------- */
  const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1.5);
  hemi.position.set(0, 4, 0);
  scene.add(hemi);

  const dir = new THREE.DirectionalLight(0xffffff, 1);
  dir.position.set(2, 4, 2);
  scene.add(dir);

  /* ---------------- State ---------------- */
  const clock = new THREE.Clock();
  let mixer = null;
  let model = null;
  let shaking = false;

  /* ---------------- Animation Loop ---------------- */
  const animate = () => {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    if (mixer) mixer.update(delta);

    // Idle animation (only when not shaking)
    if (model && !shaking) {
      model.rotation.y += 0.01;
      model.position.y = Math.sin(clock.elapsedTime * 2) * 0.05;
    }

    renderer.render(scene, camera);
    gl.endFrameEXP();
  };
  
  animate();

  /* ---------------- Shake Interaction ---------------- */
  const shakeModel = () => {
    if (!model || shaking) return;

    shaking = true;
    const duration = 300;
    const start = Date.now();

    const originalPos = model.position.clone();
    const originalRot = model.rotation.clone();

    const shake = () => {
      const elapsed = Date.now() - start;

      if (elapsed >= duration) {
        model.position.copy(originalPos);
        model.rotation.copy(originalRot);
        shaking = false;
        return;
      }

      // Apply Random Offsets
      model.position.set(
        originalPos.x + (Math.random() - 0.5) * 0.2,
        originalPos.y + (Math.random() - 0.5) * 0.2,
        originalPos.z + (Math.random() - 0.5) * 0.2
      );

      model.rotation.set(
        originalRot.x + (Math.random() - 0.5) * 0.1,
        originalRot.y + (Math.random() - 0.5) * 0.1,
        originalRot.z + (Math.random() - 0.5) * 0.1
      );

      requestAnimationFrame(shake);
    };

    shake();
  };

  /* ---------------- Model Loader ---------------- */
  // Uses standard Three.js loader.load() as requested
  const loadModel = (url) => {
    const loader = new GLTFLoader();

    loader.load(
      url,
      (gltf) => {
        // Remove previous model if exists
        if (model) scene.remove(model);

        model = gltf.scene;
        model.scale.set(1, 1, 1);
        
        // Center the model to ensure it pivots correctly
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        model.position.sub(center);

        scene.add(model);

        // Handle Animations
        if (gltf.animations && gltf.animations.length) {
          mixer = new THREE.AnimationMixer(model);
          const action = mixer.clipAction(gltf.animations[0]);
          action.play();
        }
      },
      (xhr) => {
        // Optional: Log progress
        // console.log((xhr.loaded / xhr.total * 100) + '% loaded');
      },
      (error) => {
        console.error('An error happened loading the model:', error);
      }
    );
  };

  return {
    scene,
    camera,
    loadModel,
    shakeModel,
  };
}