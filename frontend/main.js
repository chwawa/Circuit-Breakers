import { startCamera, stopCamera, capturePhoto } from "./camera.js";
import { createScene } from "./threeScene.js";

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const openBtn = document.getElementById("openCamera");
const captureBtn = document.getElementById("capture");

const { loadModel } = createScene();

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      resolve(reader.result);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

openBtn.onclick = () => startCamera(video);
  // loadModel('/public/models/preview_model.glb');

captureBtn.onclick = async () => {
  const imageBlob = await capturePhoto(video, canvas);
  stopCamera(video);
  canvas.hidden = true;

  const imageBase64 = await blobToBase64(imageBlob);

  const response = await fetch("http://127.0.0.1:8000/generate-3d", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ image_url: imageBase64 }),
    
  });
//   console.log(await response.text());

  const glbUrl = await response.json();
  console.log("glbUrl :", glbUrl)
  loadModel(glbUrl);
//   loadModel('/public/models/Meshy_AI_Animation_Walking_withSkin.glb');
};
