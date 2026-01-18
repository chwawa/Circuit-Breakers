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
  // Create friend - send image file and metadata to backend
  createFriend: async (imageUri: string, name: string, personality?: string) => {
    const id = Date.now().toString()

    try {
      // Fetch the image blob from URI
      console.log("🎬 Starting friend creation:", { imageUri, name, personality, id });

      console.log("📸 Fetching image from:", imageUri);
      const response = await fetch(imageUri);
      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.statusText}`);
      }
      const blob = await response.blob();
      console.log("✅ Image fetched, size:", blob.size, "bytes");

      // Create FormData with file and metadata
      const formData = new FormData();
      formData.append('image', blob, 'photo.jpg');
      formData.append('name', name);
      formData.append('personality', personality || "");
      formData.append('image_id', id);

      console.log("📤 Sending image file to backend:", { name, personality, id });

      // Send to backend - don't set Content-Type, let fetch set it with boundary
      const createResponse = await fetch("http://localhost:8000/create-friend", {
        method: "POST",
        body: formData
      });

      console.log("📋 Backend response status:", createResponse.status);

      if (!createResponse.ok) {
        const errorText = await createResponse.text();
        console.error("❌ Backend error:", errorText);
        throw new Error(`Failed to create friend: ${createResponse.statusText} - ${errorText}`);
      }

      const data = await createResponse.json();
      console.log('✅ Friend created successfully:', data);

      return { success: data.success, friendId: data.friend?.id || id, modelUrl: data.friend?.model_url || "" };
    } catch (error) {
      console.error('❌ Error creating friend:', error);
      throw error;
    }

    // ========== COMMENTED OUT OLD CODE ==========
    // const formData = new FormData();
    // formData.append('image', {
    //   uri: imageUri,
    //   type: 'image/jpeg',
    //   name: 'photo.jpg',
    // } as any);
    // formData.append('name', name);
    // if (personality) formData.append('personality', personality);
    //
    // // Send to 3D model generation endpoint
    // console.log("Sending image to 3D generation API:", imageUri);
    // const base64Image = await blobUrlToBase64(imageUri);
    // const response = await fetch("http://localhost:8000/generate-3d", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json"
    //   },
    //   body: JSON.stringify({ image_url: base64Image, image_id: id })
    // });
    //
    // const glbUrl = await response.json();
    // console.log("glb path :", glbUrl)
    // loadModel(glbUrl);
    // ========== END COMMENTED OUT CODE ==========
  },

  // Send text message to friend
  sendTextMessage: async (friendId: string, text: string) => {
    console.log('📤 Sending text message to backend:', { friendId, text });

    try {
      const response = await fetch('http://localhost:8000/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ friend_id: friendId, message: text })
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Backend response:', data);
      return data;
    } catch (error) {
      console.error('❌ Error sending message:', error);
      throw error;
    }

    // COMMENTED OUT: Old placeholder code
    // const response = await fetch('YOUR_BACKEND_URL/message', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ friendId, text })
    // });
    // const audioBlob = await response.blob();
    // return audioBlob;
  },

  // Send voice message to friend
  sendVoiceMessage: async (friendId: string, audioUri: string) => {
    try {
      console.log('🎤 Sending voice message:', { friendId, audioUri });

      // Fetch audio file from URI
      const audioResponse = await fetch(audioUri);
      if (!audioResponse.ok) {
        throw new Error(`Failed to fetch audio: ${audioResponse.statusText}`);
      }
      const audioBlob = await audioResponse.blob();
      console.log('✅ Audio fetched, size:', audioBlob.size, 'bytes');

      // Create FormData with audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, 'message.wav');
      formData.append('friend_id', friendId);

      // Send to backend
      const response = await fetch('http://localhost:8000/send-voice-message', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend error:', errorText);
        throw new Error(`Failed to send voice message: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Voice message response:', data);
      return data;
    } catch (error) {
      console.error('❌ Error sending voice message:', error);
      throw error;
    }
  },

  // Get friend status (for polling processing status)
  getFriendStatus: async (friendId: string) => {
    console.log('API: Checking friend status', { friendId });
    return { isProcessing: false };
  }
};
