import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

let renderer, scene, camera, currentModel, mixer, clock;

export function createScene() {
  // Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x202020);

  // Camera
  camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    100
  );
  camera.position.set(0, 1.5, 4);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);

  // Clock for animations
  clock = new THREE.Clock();

  // Lights
  const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1.5);
  light.position.set(2, 4, 2);
  scene.add(light);

  // Animations
  let animate = () => {
    requestAnimationFrame(animate);

    if (mixer) mixer.update(clock.getDelta());

    if (currentModel) {
      currentModel.rotation.y += 0.01;
      currentModel.position.y = Math.sin(clock.elapsedTime * 2) * 0.05;
    }

    renderer.render(scene, camera);
  };
  animate();

  // Interactions
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  // On click, shake the model
  window.addEventListener('click', (e) => {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(scene.children, true);

    if (hits.length && currentModel) {
      let shakeTime = 300; // total duration of shake in ms
      let intervalTime = 30; // how often to move the currentModel
      let elapsed = 0;

      const originalPos = currentModel.position.clone();
      const originalRot = currentModel.rotation.clone();

      const shakeInterval = setInterval(() => {
        // Random small offsets for position
        currentModel.position.x = originalPos.x + (Math.random() - 0.5) * 0.2;
        currentModel.position.y = originalPos.y + (Math.random() - 0.5) * 0.2;
        currentModel.position.z = originalPos.z + (Math.random() - 0.5) * 0.2;

        // Random rotation shake
        currentModel.rotation.x = originalRot.x + (Math.random() - 0.5) * 0.1;
        currentModel.rotation.y = originalRot.y + (Math.random() - 0.5) * 0.1;
        currentModel.rotation.z = originalRot.z + (Math.random() - 0.5) * 0.1;

        elapsed += intervalTime;
        if (elapsed >= shakeTime) {
          clearInterval(shakeInterval);
          currentModel.position.copy(originalPos);
          currentModel.rotation.copy(originalRot);
        }
      }, intervalTime);
    }
  });

  // Handle window resize
  const onWindowResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  };

  window.addEventListener('resize', onWindowResize);

  return {
    getRenderer: () => renderer,
    getScene: () => scene,
    loadModel(url) {
      const loader = new GLTFLoader();
      loader.load(url, (gltf) => {
        gltf.scene.scale.set(1, 1, 1);
        scene.add(gltf.scene);
        currentModel = gltf.scene;

        if (gltf.animations.length) {
          mixer = new THREE.AnimationMixer(currentModel);
          const action = mixer.clipAction(gltf.animations[0]);
          action.reset();
          action.setLoop(THREE.LoopRepeat);
          action.play();
        }
      });
    },
    cleanup: () => {
      window.removeEventListener('resize', onWindowResize);
      renderer.dispose();
    },
  };
}