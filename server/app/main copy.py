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

        # 1. Create Meshy image-to-3D task
        image_url = req.image_url
        print("Received image url:", image_url)
        payload = {
            "image_url": image_url
        }
 
        create_task = await client.post(
            "https://api.meshy.ai/openapi/v1/image-to-3d",
            headers={
                **MESHY_HEADERS,
                "Content-Type": "application/json"
            },
            json=payload
        )

        task_data = create_task.json()
        print("Meshy create task response:", task_data)

        if "result" not in task_data:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Meshy API error",
                    "meshy_response": task_data
                }
            )

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
            