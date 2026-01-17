import threading
import queue
import torch
import whisper


class audio_stt:
    def __init__(
        self,
        model_name: str = "base",
        device: str | None = None,
        language: str | None = "English",
    ):

        self.device = "cpu" #device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.language = language

        self.model = whisper.load_model(model_name, device=self.device)

        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while True:
            audio_path = self.audio_queue.get()
            if audio_path is None:
                break

            # Transcribe
            result = self.model.transcribe(
                audio_path,
                language=self.language,
            )

            # Combine all segments into final text
            text = result["text"]

            self.text_queue.put(text)
            self.audio_queue.task_done()

    def stop(self):
        self.audio_queue.put(None)
        self.thread.join()

    def STT(self, audio_path: str):
        """Submit an audio file for transcription"""
        self.audio_queue.put(audio_path)

    def get_text(self) -> str:
        """Blocking get of transcription result"""
        return self.text_queue.get()
