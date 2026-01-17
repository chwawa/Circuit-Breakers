# Install: pip install backboard-sdk
import asyncio
import os
from dotenv import load_dotenv
from backboard import BackboardClient

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

async def main():
    # Initialize the Backboard client
    client = BackboardClient(api_key=os.getenv("BACKBOARD_API_KEY"))

    # Create an assistant
    assistant = await client.create_assistant(
        name="Snoopy",
        description="You are Snoopy, the beloved beagle from the Peanuts cartoons, films, and television series."
    )

    # Create a thread
    thread = await client.create_thread(assistant.assistant_id)

    # Send a message and stream the response
    async for chunk in await client.add_message(
        thread_id=thread.thread_id,
        content="Who's your best friend?",
        llm_provider="google",
        model_name="gemini-2.5-flash-lite",
        stream=True
    ):
        # Print each chunk of content as it arrives
        if chunk.get('type') == 'content_streaming':
            print(chunk.get('content', ''), end='', flush=True)
        elif chunk.get('type') == 'message_complete':
            break

if __name__ == "__main__":
    asyncio.run(main())