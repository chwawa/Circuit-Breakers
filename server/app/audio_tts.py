import threading
import queue
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import json


class audio_tts:
    def __init__(self, api_key: str, voice_id: str, model_id: str):
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.model_id = model_id
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.thread = threading.Thread(target=self._worker)
        self.thread.start()

    def _worker(self):
        while True:
            data = self.text_queue.get()
            if data is None:
                break
            text = data.get("clean_text", "")
            command = data.get("commands", "")

            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format="mp3_44100_128",
            )
            play(audio)

            self.audio_queue.put((audio, command))

            self.text_queue.task_done()

    def stop(self):
        self.text_queue.put(None)
        self.thread.join()

    def TTS(self, data):
        try:
            payload = json.loads(data)
            text = payload.get("clean_text", "")
            command = payload.get("commands", "")
        except (json.JSONDecodeError, TypeError):
            # Handle dict input directly
            if isinstance(data, dict):
                text = data.get("clean_text", "")
                command = data.get("commands", "")
            else:
                text = data
                command = ""

        self.text_queue.put({"clean_text": text, "commands": command})

    def get_audio_chunk(self):
        return self.audio_queue.get()

