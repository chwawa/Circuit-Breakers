// import { createScene } from "../components/threeScene.js";
// const { loadModel } = createScene();

export async function blobUrlToBase64(blobUrl: string): Promise<string> {
  const response = await fetch(blobUrl);
  const blob = await response.blob();

  return await new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onerror = () =>
      reject(new Error('Failed to convert blob to base64'));

    reader.onloadend = () => {
      const dataUrl = reader.result as string;
      resolve(dataUrl);
    };

    reader.readAsDataURL(blob);
  });
}

export const apiService = {
  // Create friend - send image and metadata to backend
  createFriend: async (imageUri: string, name: string, personality?: string) => {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'photo.jpg',
    } as any);
    formData.append('name', name);
    if (personality) formData.append('personality', personality);

    const id = Date.now().toString()
    
    // TODO: Replace with your backend URL
    // const response = await fetch('YOUR_BACKEND_URL/create-friend', {
    //   method: 'POST',
    //   body: formData
    // });
    // return response.json();

    // Send to 3D model generation endpoint
    // console.log("Sending image to 3D generation API:", imageUri);
    // const base64Image = await blobUrlToBase64(imageUri);
    // const response = await fetch("http://localhost:8000/generate-3d", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json"
    //   },
    //   body: JSON.stringify({ image_url: base64Image, image_id: id })
    // });

    // const glbUrl = await response.json();
    // console.log("glbUrl :", glbUrl)
    // loadModel(glbUrl);

    
    
    console.log('API: Creating friend', { name, personality , id});
    return { success: true, friendId: id, modelUrl: "glbUrl"  };
  },

  // Send text message to friend
  sendTextMessage: async (friendId: string, text: string) => {
    // TODO: Replace with your backend URL
    // const response = await fetch('YOUR_BACKEND_URL/message', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ friendId, text })
    // });
    // const audioBlob = await response.blob();
    // return audioBlob;
    console.log('API: Sending text message', { friendId, text });
    return null; // Return audio URI in real implementation
  },

  // Send voice message to friend
  sendVoiceMessage: async (friendId: string, audioUri: string) => {
    const formData = new FormData();
    formData.append('audio', {
      uri: audioUri,
      type: 'audio/mp3',
      name: 'message.mp3',
    } as any);
    formData.append('friendId', friendId);
    
    // TODO: Replace with your backend URL
    // const response = await fetch('YOUR_BACKEND_URL/voice-message', {
    //   method: 'POST',
    //   body: formData
    // });
    // const audioResponse = await response.blob();
    // return audioResponse;
    
    console.log('API: Sending voice message', { friendId });
    return null; // Return audio URI in real implementation
  },

  // Get friend status (for polling processing status)
  getFriendStatus: async (friendId: string) => {
    // TODO: Replace with your backend URL
    // const response = await fetch(`YOUR_BACKEND_URL/friend/${friendId}/status`);
    // return response.json();
    
    console.log('API: Checking friend status', { friendId });
    return { isProcessing: false };
  }
};
