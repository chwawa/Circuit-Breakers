import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def llm_command_streamer():
    # Simulated chunks coming from an LLM
    chunks = ["Hi!! [[JU", "MP]] You ", "said: How ", "are you? [[W", "AVE]]"]
    for chunk in chunks:
        yield chunk
        await asyncio.sleep(0.5)

@app.get("/stream")
async def stream():
    return StreamingResponse(llm_command_streamer(), media_type="text/plain")