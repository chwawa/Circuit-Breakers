"""
Backend - API Server
Connection point between frontend and backend services
"""
import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from llm_parser import StreamParser
import httpx
from pydantic import BaseModel
from first_msg import backboard_stream_generator
from backboard import BackboardClient


MESHY_API_KEY = os.getenv("MESHY_API_KEY")
bb_client = BackboardClient(api_key="YOUR_BACKBOARD_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" Placeholder function to call an LLM API """
@app.get("/chat-stream")
async def call_llm(prompt: str):
    final_results = {"clean_text": "", "commands": []}
    return StreamingResponse(
        backboard_stream_generator(bb_client, prompt, final_results), 
        media_type="application/x-ndjson"
    )

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
            