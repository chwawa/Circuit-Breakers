# Install: pip install backboard-sdk
import asyncio
import os
import json
from dotenv import load_dotenv
from backboard import BackboardClient
import json
from llm_parser import StreamParser

target_chunk_size = 500  # max characters per chunk

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

async def backboard_stream_generator():
    # Initialize the Backboard client
    api_key = os.getenv('BACKBOARD_API_KEY')
    client = BackboardClient(api_key=api_key)

    parser = StreamParser()
    text_buffer = ""

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
            description="You are Snoopy, the beloved beagle from the Peanuts cartoons, films, and television series. Include one-word actions within your messages with [[ACTION]] markers."
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
                raw_text = chunk['content']
            
                # Calls llm_parser to parse chunk
                clean_segment, new_cmds = parser.parse_chunk(raw_text)
                text_buffer += clean_segment

                if new_cmds:
                    yield json.dumps({
                        "clean_text": text_buffer,
                        "commands": new_cmds, 
                        "is_end": False
                    }) + "\n"
                    text_buffer = ""
                
                elif len(text_buffer) >= target_chunk_size: 
                    yield json.dumps({
                        "clean_text": text_buffer,
                        "commands": [], 
                        "is_end": False
                    }) + "\n"
                    text_buffer = ""
            
            elif chunk['type'] == 'message_complete':
                final_data = parser.finalize()
                remaining_text = text_buffer + (final_data.get("clean_text", "") if not clean_segment in final_data.get("clean_text", "") else "")
                
                if remaining_text or final_data.get("commands"):
                    yield json.dumps({
                        "clean_text": remaining_text,
                        "commands": final_data.get("commands", []),
                        "is_end": True
                    }) + "\n"
                break
        
        print("\n")  # New line after response
