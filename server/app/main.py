"""
Backend - API Server
Connection point between frontend and backend services
"""
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
import sys
import requests
import time
import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from app.llm_parser import parse_llm_text
import httpx
from pydantic import BaseModel
import base64
from image_chatbot import create_chatbot_assistant, interactive_chat
import audio_tts as tts
import audio_stt as stt
from fastapi import UploadFile, File, HTTPException
from contextlib import asynccontextmanager

import app.audio_tts as tts

MODEL_DIR = "../frontend/PersonifAI/public/models"

MESHY_API_KEY = os.getenv("MESHY_API_KEY")
# bb_client = BackboardClient(api_key=os.getenv("BACKBOARD_API_KEY"))

tts_audio_worker = None
assistant_info_cache = None

IMAGE_PATH = r"D:\Personal Projects\Circuit-Breakers\server\app\graces_airpods.jpg"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown without deprecated on_event."""
    global tts_audio_worker, assistant_info_cache

    # ---- STARTUP ----
    # Start TTS worker ONCE
    if eleven_api_key := os.getenv("ELEVENLABS_API_KEY"):
        print("ElevenLabs API Key loaded")
    else:
        raise RuntimeError("ElevenLabs API Key not found in .env")

    tts_audio_worker = tts.audio_tts(
        api_key=eleven_api_key,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2"
    )
    print("✅ TTS worker started")

    # Create assistant ONCE (cache)
    chatbot_name = None
    print("🖼️  Creating assistant from image (startup cache)...")
    assistant_info_cache = await create_chatbot_assistant(IMAGE_PATH, chatbot_name)
    print(f"✅ Assistant cached: {assistant_info_cache.get('name')}")

    yield

    # ---- SHUTDOWN ----
    if tts_audio_worker:
        print("🛑 Stopping TTS worker...")
        tts_audio_worker.stop()
        print("🛑 TTS worker stopped.")


app = FastAPI(lifespan=lifespan)

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

class ImageRequest(BaseModel):
    image_url: str
    image_id: str = "default_image"

class ChatRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    prompt: str

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    print("ERROR:", exc)
    return PlainTextResponse(str(exc), status_code=400)


@app.post("/chat")
async def process_prompt(req: ChatRequest):
    """
    Receives prompt from frontend (STT result),
    creates assistant, sends prompt to chatbot,
    returns cleaned text and commands
    """
    global assistant_info_cache, tts_audio_worker

    print(f"📨 Received prompt from frontend: {req.prompt}")
    assistant_info = assistant_info_cache
    if not assistant_info:
        # fallback (shouldn't happen unless startup failed)
        assistant_info = await create_chatbot_assistant(IMAGE_PATH, None)
        assistant_info_cache = assistant_info
        print(f"✅ Assistant created: {assistant_info['name']}")
    
    results = []
    response_count = 0
    
    
    # Pass the prompt directly without asking for input
    print(f"🎯 Sending prompt to interactive_chat...")
    async for response in interactive_chat(assistant_info, user_prompt=req.prompt):
        response_count += 1
        print(f"📊 Response #{response_count} received")
        
        clean_text = response['clean_text']
        lines = clean_text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
        clean_text = ' '.join(cleaned_lines)
        response['clean_text'] = clean_text
        
        print(f"\n[RESPONSE] Clean text: {response['clean_text']}")
        print(f"[RESPONSE] Commands: {response['commands']}")
        
        # Send to TTS worker
        if response["clean_text"]:
            try:
                tts_audio_worker.TTS(response)
            except Exception as e:
                print(f"[TTS enqueue error] {e}")

        results.append(response)
    print(f"📤 Returning {len(results)} results to frontend")
    return JSONResponse(content={"results": results})


# """ Placeholder function to call an LLM API """
# @app.get("/chat-stream")
# async def call_llm():
#     chatbot_name = None
#     image_path = "D:\\Personal Projects\\Circuit-Breakers\\server\\app\\graces_airpods.jpg"
#     assistant_info = await create_chatbot_assistant(image_path, chatbot_name)
#     results = []
    
#     try:
#         async for response in interactive_chat(assistant_info):
#             # results.append(response)
#             clean_text = response['clean_text']
#             lines = clean_text.split('\n')
#             cleaned_lines = []
#             for line in lines:
#                 # Strip leading/trailing spaces from each line
#                 stripped = line.strip()
#                 # Only add non-empty lines
#                 if stripped:
#                     cleaned_lines.append(stripped)
#             cleaned_text = ' '.join(cleaned_lines)
#             response['clean_text'] = cleaned_text
            
#             print(f"\n[YIELDED] Clean text: {response['clean_text']}")
#             print(f"[YIELDED] Commands: {response['commands']}")
#             print(f"[YIELDED] Is end: {response['is_end']}")
            
#             # Send to TTS worker
#             if response['clean_text']:
#                 tts_audio_worker.TTS(response)
                
#                 try:
#                     audio, command = tts_audio_worker.audio_queue.get(timeout=0.1)
#                     if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
#                         audio_bytes = b''.join(audio)
#                     else:
#                         audio_bytes = audio
#                     print(f"[AUDIO] Generated {len(audio_bytes)} bytes, Command: {command}")
#                 except:
#                     pass  # Audio still processing, move on
#     finally:
#         # Stop TTS worker thread when done
#         tts_audio_worker.stop()
#         print("TTS worker stopped.")

#     return JSONResponse(content={"results": results})


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
                break
                # return preview_task["model_urls"]["glb"]

        # 3. Download the preview model in glb format

        preview_model_url = preview_task["model_urls"]["glb"]

        model_resp = await client.get(preview_model_url)
        model_resp.raise_for_status()

        # Save using image_id as the filename
        file_path = os.path.join(MODEL_DIR, f"{req.image_id}.glb")
        
        with open(file_path, "wb") as f:
            f.write(model_resp.content)

        print(f"{req.image_id} Saved to {file_path}")

        return f"http://localhost:8000/models/{req.image_id}"

@app.get("/models/{image_id}")
async def get_model(image_id: str):
    """
    Endpoint that serves the GLB file to the frontend.
    """
    file_path = os.path.join(MODEL_DIR, f"{image_id}.glb")
    
    if not os.path.exists(file_path):
        print("Model not found. Has it been generated yet?")
    
    # Returning FileResponse automatically handles headers and content-type
    return FileResponse(file_path, media_type="model/gltf-binary", filename=f"{image_id}.glb")

# @app.websocket("/ws/audio")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             chunk, command = await tts_audio_worker.get_audio_chunk()
#             await websocket.send_bytes(chunk) # Send raw bytes
#             await websocket.send_json({"command": command}) # Send associated command

    except Exception as e:
        print(f"Error: {e}")


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



# if __name__ == "__main__":
#     asyncio.run(call_llm())
