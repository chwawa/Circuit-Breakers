import threading
import queue
from faster_whisper import WhisperModel


class audio_stt:
    def __init__(
        self,
        model_name: str = "base",
        device: str | None = None,
        language: str | None = "en",
    ):
        # faster-whisper uses "cpu" or "cuda"
        self.device = device or "cpu"

        # faster-whisper expects language codes like "en", not "English"
        # If you pass "English", it may fail or ignore; so default to "en".
        self.language = language or "en"
        if self.language.lower() == "english":
            self.language = "en"

        # compute_type: int8 is good + fast on CPU
        compute_type = "int8" if self.device == "cpu" else "float16"

        self.model = WhisperModel(
            model_name,
            device=self.device,
            compute_type=compute_type,
        )

        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while True:
            audio_path = self.audio_queue.get()
            if audio_path is None:
                break

            try:
                segments, info = self.model.transcribe(
                    audio_path,
                    language=self.language,
                )
                text = "".join(seg.text for seg in segments).strip()
                self.text_queue.put(text)
            except Exception as e:
                # Return error as text so your server doesn't silently hang
                self.text_queue.put(f"[STT ERROR] {e}")
            finally:
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


# import threading
# import queue
# import torch
# import whisper


# class audio_stt:
#     def __init__(
#         self,
#         model_name: str = "base",
#         device: str | None = None,
#         language: str | None = "English",
#     ):

#         self.device = "cpu" #device or ("cuda" if torch.cuda.is_available() else "cpu")
#         self.language = language

#         self.model = whisper.load_model(model_name, device=self.device)

#         self.audio_queue = queue.Queue()
#         self.text_queue = queue.Queue()

#         self.thread = threading.Thread(target=self._worker, daemon=True)
#         self.thread.start()

#     def _worker(self):
#         while True:
#             audio_path = self.audio_queue.get()
#             if audio_path is None:
#                 break

#             # Transcribe
#             result = self.model.transcribe(
#                 audio_path,
#                 language=self.language,
#             )

#             # Combine all segments into final text
#             text = result["text"]

#             self.text_queue.put(text)
#             self.audio_queue.task_done()

#     def stop(self):
#         self.audio_queue.put(None)
#         self.thread.join()

#     def STT(self, audio_path: str):
#         """Submit an audio file for transcription"""
#         self.audio_queue.put(audio_path)

#     def get_text(self) -> str:
#         """Blocking get of transcription result"""
#         return self.text_queue.get()
