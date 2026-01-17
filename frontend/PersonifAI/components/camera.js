export async function startCamera(video) {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;
}

export function stopCamera(video) {
  const stream = video.srcObject;
  stream?.getTracks().forEach(track => track.stop());
  video.srcObject = null;
}

export async function capturePhoto(video, canvas) {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);
  return new Promise((res) => canvas.toBlob(res, "image/png"));
}
