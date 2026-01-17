# Install: pip install backboard-sdk
import asyncio
import os
import json
from dotenv import load_dotenv
from backboard import BackboardClient

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Path to store conversation metadata
CONVERSATION_FILE = os.path.join(os.path.dirname(__file__), 'snoopy_conversation.json')

def load_conversation_metadata():
    """Load assistant and thread IDs from file if they exist."""
    if os.path.exists(CONVERSATION_FILE):
        try:
            with open(CONVERSATION_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_conversation_metadata(assistant_id, thread_id):
    """Save assistant and thread IDs to file."""
    metadata = {
        'assistant_id': str(assistant_id),
        'thread_id': str(thread_id)
    }
    with open(CONVERSATION_FILE, 'w') as f:
        json.dump(metadata, f)

async def main():
    # Initialize the Backboard client
    api_key = os.getenv('BACKBOARD_API_KEY')
    client = BackboardClient(api_key=api_key)

    # Check if we have an existing conversation
    existing_conversation = load_conversation_metadata()
    
    if existing_conversation:
        assistant_id = existing_conversation['assistant_id']
        thread_id = existing_conversation['thread_id']
        assistant = await client.get_assistant(assistant_id)
        print(f"\n✓ Loaded existing assistant '{assistant.name}' (ID: {assistant_id})")
        print(f"✓ Loaded existing thread (ID: {thread_id})")
    else:
        # Create a new assistant
        assistant = await client.create_assistant(
            name="Snoopy",
            description="You are Snoopy, the beloved beagle from the Peanuts cartoons, films, and television series."
        )
        
        # Create a new thread
        thread = await client.create_thread(assistant.assistant_id)
        assistant_id = assistant.assistant_id
        thread_id = thread.thread_id
        
        # Save the conversation metadata
        save_conversation_metadata(assistant_id, thread_id)
        
        print(f"\n✓ Assistant '{assistant.name}' created (ID: {assistant_id})")
        print(f"✓ Thread created (ID: {thread_id})")

    print("\nChat started! Type 'exit' or 'quit' to end the conversation.\n")

    # Interactive chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye! Your conversation has been saved.")
            break
        
        # Skip empty inputs
        if not user_input:
            continue
        
        # Send a message and stream the response
        print("Snoopy: ", end="", flush=True)
        async for chunk in await client.add_message(
            thread_id=thread_id,
            content=user_input,
            llm_provider="google",
            model_name="gemini-2.5-flash-lite",
            stream=True
        ):
            # Print each chunk of content as it arrives
            if chunk.get('type') == 'content_streaming':
                print(chunk.get('content', ''), end='', flush=True)
            elif chunk.get('type') == 'message_complete':
                break
        
        print("\n")  # New line after response

if __name__ == "__main__":
    asyncio.run(main())