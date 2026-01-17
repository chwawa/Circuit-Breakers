"""
Backend - API Server
Connection point between frontend and backend services
"""
import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from llm_parser import parse_llm_text
import httpx
from pydantic import BaseModel
import base64
import audio_tts as tts
from dotenv import load_dotenv


MESHY_API_KEY = os.getenv("MESHY_API_KEY")

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

class ChatRequest(BaseModel):
    prompt: str
    track_positions: bool = True

""" Placeholder function to call an LLM API """
async def call_llm(prompt: str) -> str:
    # Testing 
    return f"Hi!! [[JUMP]] You said: {prompt} [[WAVE]]"

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Parse LLM-generated text with embedded commands.
    
    Request JSON:
    {
        "text": "Hi!! [[JUMP]] You said: {prompt} [[WAVE]]",
        "preserve_spacing": false,
        "track_positions": false
    }
    
    Response JSON:
    {
        "clean_text": "Hi!! You said: {prompt}",
        "commands": ["JUMP", "WAVE"],
        "positions": null
    }
    """
    try:
        llm_text = await call_llm(request.prompt)

        parsed = parse_llm_text(llm_text, track_positions=request.track_positions)
        return {
            "clean_text": parsed.clean_text,
            "commands": parsed.commands,
            "positions": parsed.positions
        }

    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Meshy.ai endpoints
MESHY_HEADERS = {
    "Authorization": f"Bearer {MESHY_API_KEY}"
}

@app.post("/generate-3d")
async def generate_3d(image: UploadFile = File(...)):
    async with httpx.AsyncClient(timeout=60) as client:

        # 1. Create Meshy image-to-3D task
        files = {
            "image": (image.filename, await image.read(), image.content_type)
        }

        create_task = await client.post(
            "https://api.meshy.ai/openapi/v1/image-to-3d",
            headers=MESHY_HEADERS,
            files=files
        )

        task_data = create_task.json()
        task_id = task_data["result"]["task_id"]

        # 2. Poll task
        while True:
            await asyncio.sleep(3)

            poll = await client.get(
                f"https://api.meshy.ai/openapi/v1/tasks/{task_id}",
                headers=MESHY_HEADERS
            )

            data = poll.json()
            status = data["result"]["status"]

            if status == "succeeded":
                return {
                    "glbUrl": data["result"]["outputs"]["glb"]
                }

            if status == "failed":
                return {"error": "Meshy generation failed"}
            


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            chunk, command = await tts_audio_worker.get_audio_chunk()
            await websocket.send_bytes(chunk) # Send raw bytes
            await websocket.send_json({"command": command}) # Send associated command

    except Exception as e:
        print(f"Error: {e}")


@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file")

    file_id = uuid.uuid4().hex
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    # Save uploaded audio to disk
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Send file to worker
    stt_worker.transcribe(str(file_path))

    # Blocking wait for result (simple + correct)
    text = stt_worker.get_result()

    return {
        "text": text,
        "file": file_path.name,
    }




            