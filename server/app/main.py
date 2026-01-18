"""
Backend - API Server
Connection point between frontend and backend services
"""
from dotenv import load_dotenv
load_dotenv()
import sys
import requests
import time
import os
import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from llm_parser import StreamParser
import httpx
from pydantic import BaseModel
import base64
from backboard import BackboardClient
from server.app.dump.snoopy_assistant import backboard_stream_generator
from image_chatbot import create_chatbot_assistant, interactive_chat
import audio_tts as tts


MESHY_API_KEY = os.getenv("MESHY_API_KEY")
# bb_client = BackboardClient(api_key=os.getenv("BACKBOARD_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start Audio TTS worker
if eleven_api_key := os.getenv("ELEVENLABS_API_KEY"):
    print("ElevenLabs API Key loaded")
else:
    print("ElevenLabs API Key not found in .env")
    exit()

tts_audio_worker = tts.audio_tts(
    api_key=eleven_api_key,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2"
)

class ImageRequest(BaseModel):
    image_url: str

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    print("ERROR:", exc)
    return PlainTextResponse(str(exc), status_code=400)

""" Placeholder function to call an LLM API """
@app.get("/chat-stream")
async def call_llm():
    chatbot_name = None
    image_path = "D:\\Personal Projects\\Circuit-Breakers\\server\\app\\graces_airpods.jpg"
    assistant_info = await create_chatbot_assistant(image_path, chatbot_name)
    results = []
    
    try:
        async for response in interactive_chat(assistant_info):
            # results.append(response)
            clean_text = response['clean_text']
            lines = clean_text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Strip leading/trailing spaces from each line
                stripped = line.strip()
                # Only add non-empty lines
                if stripped:
                    cleaned_lines.append(stripped)
            cleaned_text = ' '.join(cleaned_lines)
            response['clean_text'] = cleaned_text
            
            print(f"\n[YIELDED] Clean text: {response['clean_text']}")
            print(f"[YIELDED] Commands: {response['commands']}")
            print(f"[YIELDED] Is end: {response['is_end']}")
            
            # Send to TTS worker
            if response['clean_text']:
                tts_audio_worker.TTS(response)
                
                # Don't wait for audio - let it play in background
                # (Optional: you can check for audio without blocking)
                try:
                    audio, command = tts_audio_worker.audio_queue.get(timeout=0.1)
                    if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
                        audio_bytes = b''.join(audio)
                    else:
                        audio_bytes = audio
                    print(f"[AUDIO] Generated {len(audio_bytes)} bytes, Command: {command}")
                except:
                    pass  # Audio still processing, move on
    finally:
        # Stop TTS worker thread when done
        tts_audio_worker.stop()
        print("TTS worker stopped.")

    return JSONResponse(content={"results": results})


# Meshy.ai endpoints
MESHY_HEADERS = {
    "Authorization": f"Bearer {MESHY_API_KEY}"
}


@app.post("/generate-3d")
async def generate_3d(req: ImageRequest):
    async with httpx.AsyncClient(timeout=60) as client:

        # 1. Generate a preview model and get the task ID
        image_url = req.image_url
        print("Received image url:", image_url[0:10])
        payload = {
            "image_url": image_url,
            # "model_type": "lowpoly",
            "should_texture": False
        }

        generate_preview_response = requests.post(
            "https://api.meshy.ai/openapi/v1/image-to-3d",
            headers=MESHY_HEADERS,
            json=payload,
        )

        generate_preview_response.raise_for_status()

        preview_task_id = generate_preview_response.json()["result"]

        print("Preview task created. Task ID:", preview_task_id)

        # 2. Poll the preview task status until it's finished
        preview_task = None
        while True:
            time.sleep(0.2)
            preview_task_response = requests.get(
                f"https://api.meshy.ai/openapi/v1/image-to-3d/{preview_task_id}",
                headers=MESHY_HEADERS,
            )

            preview_task_response.raise_for_status()

            preview_task = preview_task_response.json()
            
            if preview_task["model_urls"]["glb"]:
                print(preview_task)
                return preview_task["model_urls"]["glb"]

        # 3. Download the preview model in glb format

        # preview_model_url = preview_task["model_urls"]["glb"]

        # preview_model_response = requests.get(preview_model_url)
        # preview_model_response.raise_for_status()

        # with open("preview_model.glb", "wb") as f:
        #     f.write(preview_model_response.content)
        # print("Preview model downloaded.")



# @app.websocket("/ws/audio")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             chunk, command = await tts_audio_worker.get_audio_chunk()
#             await websocket.send_bytes(chunk) # Send raw bytes
#             await websocket.send_json({"command": command}) # Send associated command

#     except Exception as e:
#         print(f"Error: {e}")


# @app.post("/stt")
# async def speech_to_text(file: UploadFile = File(...)):
#     if not file.content_type.startswith("audio/"):
#         raise HTTPException(status_code=400, detail="Invalid audio file")

#     file_id = uuid.uuid4().hex
#     file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

#     # Save uploaded audio to disk
#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     # Send file to worker
#     stt_worker.transcribe(str(file_path))

#     # Blocking wait for result (simple + correct)
#     text = stt_worker.get_result()

#     return {
#         "text": text,
#         "file": file_path.name,
#     }



if __name__ == "__main__":
    asyncio.run(call_llm())

            