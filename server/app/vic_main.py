"""
Backend - API Server (VIC Version)
Connection point between frontend and backend services
Uses vic_image_chatbot for AI assistant functionality
"""
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import sys
import requests
import time
import asyncio
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
import httpx
from pydantic import BaseModel
import base64
from app.image_chatbot import create_chatbot_assistant, interactive_chat
from app.audio_stt import audio_stt
from contextlib import asynccontextmanager
import json
from typing import Dict, List
import tempfile
import os

MODEL_DIR = "../frontend/PersonifAI/public/models"

MESHY_API_KEY = os.getenv("MESHY_API_KEY")

tts_audio_worker = None
assistant_info_cache = None
friends_db: Dict = {}  # {friend_id: {name, personality, assistant_info, model_url, created_at}}

IMAGE_PATH = r"D:\Personal Projects\Circuit-Breakers\server\app\graces_airpods.jpg"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown without deprecated on_event."""
    global tts_audio_worker, assistant_info_cache

    # ---- STARTUP ----
    print("✅ Backend ready (VIC Edition)")

    yield

    # ---- SHUTDOWN ----
    print("🛑 Backend shutdown complete.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request Models ====================

class ImageRequest(BaseModel):
    image_url: str
    image_id: str = "default_image"

class ChatRequest(BaseModel):
    prompt: str

# COMMENTED OUT: Using FormData with UploadFile instead of JSON request model
# class CreateFriendRequest(BaseModel):
#     image_path: str  # Path to image file on device
#     image_id: str
#     name: str
#     personality: str = ""

class SendMessageRequest(BaseModel):
    friend_id: str
    message: str


# ==================== Error Handler ====================

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    print("ERROR:", exc)
    return PlainTextResponse(str(exc), status_code=400)


# ==================== Friend Management Endpoints ====================

@app.post("/create-friend")
async def create_friend(
    image: UploadFile = File(...),
    name: str = Form(...),
    personality: str = Form(default=""),
    image_id: str = Form(...)
):
    """
    Create a new AI friend from an uploaded image file.
    - Receives image as multipart/form-data
    - Saves image to disk
    - Creates chatbot assistant with personality
    - Returns friend data (id, name, model_url, assistant_info)
    """
    global friends_db
    
    friend_id = image_id
    print(f"👨‍👩‍👧 Creating friend '{name}' (ID: {friend_id})...")
    print(f"✅ Endpoint received request")
    
    try:
        # Create models directory if it doesn't exist
        print(f"📁 Creating models directory...")
        models_dir = os.path.join(os.path.dirname(__file__), "..", "public", "models")
        os.makedirs(models_dir, exist_ok=True)
        print(f"✅ Models directory ready")
        
        # Save uploaded image file
        print(f"💾 Saving image file...")
        image_path = os.path.join(models_dir, f"{friend_id}.jpeg")
        with open(image_path, "wb") as f:
            contents = await image.read()
            f.write(contents)
        
        print(f"✅ Image saved to: {image_path}")
        print(f"📊 File size: {os.path.getsize(image_path)} bytes")
        
        # Create assistant from saved image file
        print(f"🤖 Starting chatbot assistant creation...")
        print(f"🎨 Using image: {image_path}, name: {name}, personality: {personality}")
        assistant_info = await create_chatbot_assistant(image_path, name)
        print(f"✅ Assistant created: {assistant_info}")
        
        
        # Store friend data
        friends_db[friend_id] = {
            "id": friend_id,
            "name": name,
            "personality": personality,
            "assistant_info": assistant_info,
            "model_url": "",
            "image_path": image_path,
            "created_at": time.time()
        }
        
        print(f"✅ Friend '{name}' created successfully!")
        
        return JSONResponse(content={
            "success": True,
            "friend": {
                "id": friend_id,
                "name": name,
                "personality": personality,
                "model_url": "",
                "image_path": image_path,
                "assistant_id": assistant_info.get("assistant_id")
            }
        })
    
    except Exception as e:
        print(f"❌ Error creating friend: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "error": str(e)
        }, status_code=400)


@app.post("/send-message")
async def send_message(req: SendMessageRequest):
    """
    Send a message to a friend's assistant and get response.
    Returns streamed response with text and commands.
    """
    global friends_db
    
    friend_id = req.friend_id
    print(f"💬 Sending message to friend '{friend_id}': {req.message}")
    
    # Check if friend exists
    if friend_id not in friends_db:
        return JSONResponse(content={
            "success": False,
            "error": f"Friend '{friend_id}' not found"
        }, status_code=404)
    
    try:
        friend_data = friends_db[friend_id]
        assistant_info = friend_data["assistant_info"]
        results = []
        response_count = 0
        
        # Send message to assistant and stream response
        print(f"🎯 Sending message to assistant...")
        async for response in interactive_chat(assistant_info, user_prompt=req.message):
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
            
            results.append(response)
        
        print(f"📤 Returning {len(results)} results to frontend")
        return JSONResponse(content={
            "success": True,
            "friend_id": friend_id,
            "results": results
        })
    
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "error": str(e)
        }, status_code=400)


@app.post("/send-voice-message")
async def send_voice_message(
    audio: UploadFile = File(...),
    friend_id: str = Form(...)
):
    """
    Receive audio file, convert to text using Whisper, 
    then process as text message through the assistant.
    """
    global friends_db
    
    print(f"🎤 Received voice message for friend '{friend_id}'")
    
    # Check if friend exists
    if friend_id not in friends_db:
        return JSONResponse(content={
            "success": False,
            "error": f"Friend '{friend_id}' not found"
        }, status_code=404)
    
    try:
        # Save audio file temporarily
        audio_content = await audio.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_content)
            audio_path = tmp.name
        
        print(f"💾 Audio saved temporarily to: {audio_path}")
        
        # Convert speech to text using Whisper
        print(f"🎙️ Converting speech to text...")
        stt = audio_stt(model_name="base", device="cpu", language="en")
        stt.audio_queue.put(audio_path)
        
        # Wait for transcription
        import time
        timeout = 60
        start_time = time.time()
        transcribed_text = None
        
        while time.time() - start_time < timeout:
            try:
                transcribed_text = stt.text_queue.get(timeout=1)
                break
            except:
                continue
        
        if not transcribed_text:
            raise Exception("Failed to transcribe audio - timeout")
        
        # Clean up temp file
        os.unlink(audio_path)
        
        print(f"✅ Transcribed text: '{transcribed_text}'")
        
        # Now process the transcribed text as a normal message
        print(f"💬 Processing transcribed message...")
        friend_data = friends_db[friend_id]
        assistant_info = friend_data["assistant_info"]
        results = []
        response_count = 0
        
        # Send message to assistant and stream response
        async for response in interactive_chat(assistant_info, user_prompt=transcribed_text):
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
            
            results.append(response)
        
        print(f"📤 Returning {len(results)} results to frontend")
        return JSONResponse(content={
            "success": True,
            "friend_id": friend_id,
            "transcribed_text": transcribed_text,
            "results": results
        })
        
    except Exception as e:
        print(f"❌ Error processing voice message: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "error": str(e)
        }, status_code=400)
async def get_friends():
    """
    Get all created friends with their metadata.
    """
    global friends_db
    
    friends_list = []
    for friend_id, friend_data in friends_db.items():
        friends_list.append({
            "id": friend_id,
            "name": friend_data.get("name"),
            "personality": friend_data.get("personality"),
            "model_url": friend_data.get("model_url"),
            "created_at": friend_data.get("created_at")
        })
    
    return JSONResponse(content={"friends": friends_list})


@app.get("/friends/{friend_id}")
async def get_friend(friend_id: str):
    """
    Get details of a specific friend.
    """
    global friends_db
    
    if friend_id not in friends_db:
        return JSONResponse(content={
            "success": False,
            "error": f"Friend '{friend_id}' not found"
        }, status_code=404)
    
    friend_data = friends_db[friend_id]
    return JSONResponse(content={
        "success": True,
        "friend": {
            "id": friend_id,
            "name": friend_data.get("name"),
            "personality": friend_data.get("personality"),
            "model_url": friend_data.get("model_url"),
            "created_at": friend_data.get("created_at")
        }
    })


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return JSONResponse(content={"status": "ok", "version": "vic_edition"})
