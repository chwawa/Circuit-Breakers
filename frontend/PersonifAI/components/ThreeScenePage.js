import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

let renderer, scene, camera, currentModel, mixer, clock;
let animationId;
let shakeState = null;

export function createScene() {
  // Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f172a);

  // Camera
  camera = new THREE.PerspectiveCamera(90, 1, 0.5, 5);
  camera.position.set(0, 0, 1.8);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);

  // Clock
  clock = new THREE.Clock();

  // Lights (more depth)
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
  keyLight.position.set(3, 5, 2);
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0xa855f7, 0.6);
  rimLight.position.set(-3, 2, -2);
  scene.add(rimLight);

  // Animation loop
  const animate = () => {
    animationId = requestAnimationFrame(animate);

    const delta = clock.getDelta();
    mixer?.update(delta);

    if (currentModel) {
      // Smooth rotating motion
      // currentModel.rotation.y += delta * 0.6;
      // currentModel.position.y = Math.sin(clock.elapsedTime * 2) * 0.04;

      // Bobbing motion
      const bobSpeed = 2;
      const bobHeight = 0.1;
      currentModel.position.y = Math.sin(clock.elapsedTime * bobSpeed) * bobHeight;

      // Shake animation (if active)
      if (shakeState) {
        shakeState.elapsed += delta * 1000;
        const t = shakeState.elapsed / shakeState.duration;

        if (t >= 1) {
          currentModel.position.copy(shakeState.originalPos);
          currentModel.rotation.copy(shakeState.originalRot);
          shakeState = null;
        } else {
          const strength = (1 - t) * shakeState.strength;
          currentModel.position.x =
            shakeState.originalPos.x + (Math.random() - 0.5) * strength;
          currentModel.position.y =
            shakeState.originalPos.y + (Math.random() - 0.5) * strength;
          currentModel.position.z =
            shakeState.originalPos.z + (Math.random() - 0.5) * strength;

          currentModel.rotation.x =
            shakeState.originalRot.x + (Math.random() - 0.5) * strength * 0.5;
          currentModel.rotation.y =
            shakeState.originalRot.y + (Math.random() - 0.5) * strength * 0.5;
        }
      }
    }

    renderer.render(scene, camera);
  };

  animate();

  // Interaction
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  window.addEventListener("click", (e) => {
    if (!currentModel) return;

    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(scene.children, true);

    if (hits.length) {
      shakeState = {
        elapsed: 0,
        duration: 300,
        strength: 0.2,
        originalPos: currentModel.position.clone(),
        originalRot: currentModel.rotation.clone(),
      };
    }
  });

  return {
    getRenderer: () => renderer,
    getScene: () => scene,

    loadModel(url) {
      const loader = new GLTFLoader();
      loader.load(url, (gltf) => {
        currentModel = gltf.scene;
        currentModel.scale.setScalar(1);
        scene.add(currentModel);

        if (gltf.animations.length) {
          mixer = new THREE.AnimationMixer(currentModel);
          mixer.clipAction(gltf.animations[0]).play();
        }
      });
    },

    cleanup() {
      cancelAnimationFrame(animationId);
      renderer.dispose();
      scene.clear();
      currentModel = null;
      mixer = null;
    },
  };
}
