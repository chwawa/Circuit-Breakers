import sounddevice as sd
import soundfile as sf
import numpy as np
from audio_stt import audio_stt as stt

SAMPLE_RATE = 16000
RECORD_SECONDS = 6
AUDIO_FILE = "recorded.wav"


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

    stt_audio_worker.stop()

if __name__ == "__main__":
    main()
