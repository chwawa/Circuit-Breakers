import sounddevice as sd
import soundfile as sf
import numpy as np
import requests
import json
from audio_stt import audio_stt as stt

SAMPLE_RATE = 16000
RECORD_SECONDS = 6
AUDIO_FILE = "recorded.wav"
BACKEND_URL = "http://localhost:8000"  # Your backend server


def record_audio():
    print("🎤 Speak now...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("🛑 Recording finished")

    sf.write(AUDIO_FILE, audio, SAMPLE_RATE)


def send_to_backend(text: str):
    """Send transcribed text to backend for processing"""
    print(f"\n📤 Sending to backend: {text}")
    
    try:
        # Send text to backend endpoint
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"prompt": text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Backend response:")
            print(json.dumps(data, indent=2))
            
            # Extract and print the clean text and commands
            if "results" in data:
                for result in data["results"]:
                    print(f"\n🤖 Response: {result.get('clean_text', '')}")
                    if result.get('commands'):
                        print(f"📌 Commands: {result['commands']}")
            
            return data
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error sending to backend: {e}")
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
