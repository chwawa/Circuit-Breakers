import * as THREE from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js'

/* ---------- SCENE ---------- */
const scene = new THREE.Scene()
scene.background = new THREE.Color(0xeeeeee)

/* ---------- CAMERA ---------- */
const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  100
)
camera.position.set(0, 1, 3)

/* ---------- RENDERER ---------- */
const renderer = new THREE.WebGLRenderer({ antialias: true })
renderer.setSize(window.innerWidth, window.innerHeight)
document.body.appendChild(renderer.domElement)

/* ---------- LIGHTS ---------- */
scene.add(new THREE.AmbientLight(0xffffff, 0.4))

const light = new THREE.DirectionalLight(0xffffff, 1)
light.position.set(2, 4, 2)
scene.add(light)

/* ---------- MODEL ---------- */
// TODO: GET MODEL FROM SCAN
const loader = new OBJLoader()
let chair = null

loader.load(
  '/wooden_chair_fixed_normals.obj',
  (obj) => {
    chair = obj
    chair.scale.set(1.5, 1.5, 1.5)
    scene.add(chair)
  },
  undefined,
  (err) => console.error(err)
)

/* ---------- ANIMATIONS ---------- */
function rotate_animation(time) {
  requestAnimationFrame(rotate_animation)

  if (chair) {
    chair.position.y = Math.sin(time * 0.002) * 0.05
    chair.rotation.y += 0.002
  }

  renderer.render(scene, camera)
}
rotate_animation()

/* ---------- INTERACTIONS ---------- */
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2()

// On click, scale up the model briefly
// window.addEventListener('click', (e) => {
//   mouse.x = (e.clientX / window.innerWidth) * 2 - 1
//   mouse.y = -(e.clientY / window.innerHeight) * 2 + 1

//   raycaster.setFromCamera(mouse, camera)
//   const hits = raycaster.intersectObjects(scene.children, true)

//   if (hits.length && chair) {
//     chair.scale.set(1.6, 1.6, 1.6)
//     setTimeout(() => chair.scale.set(1.5, 1.5, 1.5), 150)
//   }
// })

// On click, shake the model
window.addEventListener('click', (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const hits = raycaster.intersectObjects(scene.children, true)

  if (hits.length && chair) {
    let shakeTime = 300 // total duration of shake in ms
    let intervalTime = 30 // how often to move the chair
    let elapsed = 0

    const originalPos = chair.position.clone()
    const originalRot = chair.rotation.clone()

    const shakeInterval = setInterval(() => {
      // Random small offsets for position
      chair.position.x = originalPos.x + (Math.random() - 0.5) * 0.2
      chair.position.y = originalPos.y + (Math.random() - 0.5) * 0.2
      chair.position.z = originalPos.z + (Math.random() - 0.5) * 0.2

      // Optional: random rotation shake
      chair.rotation.x = originalRot.x + (Math.random() - 0.5) * 0.1
      chair.rotation.y = originalRot.y + (Math.random() - 0.5) * 0.1
      chair.rotation.z = originalRot.z + (Math.random() - 0.5) * 0.1

      elapsed += intervalTime
      if (elapsed >= shakeTime) {
        clearInterval(shakeInterval)
        chair.position.copy(originalPos)
        chair.rotation.copy(originalRot)
      }
    }, intervalTime)
  }
})
