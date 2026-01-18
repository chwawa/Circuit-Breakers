import sounddevice as sd
import soundfile as sf
import numpy as np
import requests
import json
import logging
from audio_stt import audio_stt as stt

# Setup logging to see HTTP requests
# logging.basicConfig(level=logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

SAMPLE_RATE = 16000
RECORD_SECONDS = 6
AUDIO_FILE = "recorded.wav"
BACKEND_URL = "http://localhost:8000"  # Your backend server


def record_audio():
    """Record audio from microphone until user presses Enter"""
    # print("🎤 Speak now... (Press Enter to stop recording)")
    
    CHUNK_SIZE = int(SAMPLE_RATE * 0.5)  # 0.5 second chunks
    audio_chunks = []
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"⚠️  Audio warning: {status}")
        audio_chunks.append(indata.copy())
    
    print("💬 Recording... (Press Enter when done)")
    
    try:
        stream = sd.InputStream(
            channels=1,
            samplerate=SAMPLE_RATE,
            callback=audio_callback,
            blocksize=CHUNK_SIZE
        )
        
        with stream:
            input()  # Wait for user to press Enter
        
        print("🛑 Recording finished")
        
        # Combine all chunks
        if audio_chunks:
            audio = np.concatenate(audio_chunks, axis=0)
            duration = len(audio) / SAMPLE_RATE
            print(f"✅ Recorded {duration:.1f} seconds")
            sf.write(AUDIO_FILE, audio, SAMPLE_RATE)
        else:
            print("❌ No audio recorded")
    
    except Exception as e:
        print(f"❌ Recording error: {e}")
        import traceback
        traceback.print_exc()


def send_to_backend(text: str):
    """Send transcribed text to backend for processing"""
    print(f"\n📤 Sending to backend: {text}")
    
    try:
        # Send text to backend endpoint with timeout
        print(f"🔗 URL: {BACKEND_URL}/chat")
        print(f"📦 Payload: {json.dumps({'prompt': text})}")
        print("⏳ Waiting for backend response...")
        
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"prompt": text},
            headers={"Content-Type": "application/json"},
            timeout=30,  # 30 second timeout
            verify=False  # Disable SSL verification if needed
        )
        print(f"✅ Got response with status {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Backend response:")
            print(json.dumps(data, indent=2))
            
            # Extract and print the clean text and commands
            if "results" in data:
                print(f"📊 Received {len(data['results'])} results")
                for i, result in enumerate(data["results"]):
                    print(f"\n  Result #{i+1}:")
                    print(f"    Clean text: {result.get('clean_text', '')}")
                    if result.get('commands'):
                        print(f"    Commands: {result['commands']}")
            
            return data
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(f"📄 Response body: {response.text[:500]}")
            return None
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds - backend may be stuck!")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure backend is running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error sending to backend: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    record_audio()

    stt_audio_worker = stt(
        model_name="base",
        language="en",
    )

    stt_audio_worker.STT(AUDIO_FILE)

    print("🧠 Transcribing...")
    text = stt_audio_worker.get_text()

    print("\n📝 Transcription:")
    print(text)
    
    # Send to backend
    response = send_to_backend(text)

    stt_audio_worker.stop()

if __name__ == "__main__":
    main()
