"""
Backend - API Server
Connection point between frontend and backend services
"""
from dotenv import load_dotenv
load_dotenv()

import requests
import time
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from .llm_parser import parse_llm_text
import httpx
from pydantic import BaseModel

MESHY_API_KEY = os.getenv("MESHY_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    track_positions: bool = True

class ImageRequest(BaseModel):
    image_url: str

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    print("ERROR:", exc)
    return PlainTextResponse(str(exc), status_code=400)

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
