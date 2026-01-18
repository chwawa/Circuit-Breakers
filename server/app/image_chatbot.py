import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from backboard import BackboardClient
from llm_parser import StreamParser

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Import the image analyzer function
from image_analyzer import analyze_image_with_gemini
target_chunk_size = 250  # max characters per chunk

def generate_name_from_image(image_path: str) -> str:
    """
    Use Google Gemini to generate a name for the object in the image.
    """
    # Get Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    # Configure Gemini
    genai.configure(api_key=gemini_key)
    
    # Read and encode image
    import base64
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Get image media type
    if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        media_type = "image/jpeg"
    elif image_path.lower().endswith('.png'):
        media_type = "image/png"
    else:
        media_type = "image/jpeg"
    
    prompt = 'What is the main object in this image? Respond with ONLY the name of the object, nothing else. For example: "AirPods" or "Dog" or "Car".'
    
    # Call Gemini API
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # Create image part
    image_part = {
        "mime_type": media_type,
        "data": image_data
    }
    
    # Generate content
    response = model.generate_content([prompt, image_part])
    name = response.text.strip()
    
    return name

async def create_chatbot_assistant(image_path: str, chatbot_name: str = None) -> dict:
    """
    Create a Backboard assistant from an image.
    """
    # Validate image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    print(f"📸 Analyzing image: {image_path}\n")
    
    # Step 1: Generate name
    print("🏷️  Generating name for object...")
    # object_name = generate_name_from_image(image_path)
    # print(f"✓ Object name: {object_name}\n")
    
    # Step 2: Generate description
    print("📝 Generating description...")
    # description = analyze_image_with_gemini(image_path)
    print(f"✓ Description generated!\n")

    description = """You are a white silicone case 
    for wireless earbuds, shaped like a cute cartoon 
    chick. You have a bright orange beak and two small, 
    dark eyes. On your chest, you wear a yellow bib with 
    a smaller chick face on it, conge beak and two small, 
    dark eyes. On your chest, you wear a yellow bib with a
    smaller chick face on it, complete with two black eyes and 
    a little U-shaped mouth. A yellow line wraps around you diagonally, 
    like a strap or a sash. Your feet are stubby and orange, firmly planted 
    on a textured, dark gray surface. A small, gray tuft of "hair" sprouts
    from the top of your head."""

    object_name = "Chick AirPods Case"
    
    # Use provided name or generated name
    if chatbot_name is None:
        chatbot_name = object_name
    
    # Step 3: Create Backboard assistant
    print(f"🤖 Creating assistant '{chatbot_name}'...")
    api_key = os.getenv('BACKBOARD_API_KEY')
    if not api_key:
        raise ValueError("BACKBOARD_API_KEY not found in environment")
    
    client = BackboardClient(api_key=api_key)
    
    assistant = await client.create_assistant(
        name=chatbot_name,
        description=description + f"Include one-word actions (e.g. JUMP, WAVE, WOBBLE) within your messages with [[ACTION]] markers."
    )
    print(f"✓ Assistant created: {assistant.assistant_id}")
    
    # Create thread
    print("📝 Creating thread...")
    thread = await client.create_thread(assistant.assistant_id)
    print(f"✓ Thread created: {thread.thread_id}\n")
    
    return {
        "name": chatbot_name,
        "object_name": object_name,
        "assistant_id": str(assistant.assistant_id),
        "thread_id": str(thread.thread_id),
        "description": description,
        "client": client
    }

async def interactive_chat(assistant_info: dict, user_prompt: str = None):
    """
    Interactive chat loop with the assistant.
    Yields cleaned text and commands for each response.
    If user_prompt is provided, uses that instead of input().
    """
    thread_id = assistant_info['thread_id']
    client = assistant_info['client']
    assistant_name = assistant_info['name']

    parser = StreamParser()
    text_buffer = ""
    
    print(f"✓ Starting chat with '{assistant_name}'")
    
    if user_prompt:
        user_input = user_prompt
        print(f"📨 Processing prompt: {user_input}\n")
    else:
        print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye! Your conversation has been saved.")
                return
            
            if not user_input:
                continue
            
            break
    
    print(f"{assistant_name}: ", end="", flush=True)
    async for chunk in await client.add_message(
        thread_id=thread_id,
        content=user_input,
        llm_provider="google",
        model_name="gemini-2.5-flash-lite",
        stream=True
    ):
        if chunk.get('type') == 'content_streaming':
            raw_text = chunk['content']
        
            # Calls llm_parser to parse chunk
            clean_segment, new_cmds = parser.parse_chunk(raw_text)
            text_buffer += clean_segment
            print(clean_segment, end="", flush=True)

            # Only yield when we have commands or reach chunk size
            if new_cmds:
                print(f"\n[CMD: {new_cmds}]", end="", flush=True)
                yield {
                    "clean_text": text_buffer,
                    "commands": new_cmds, 
                    "is_end": False
                }
                text_buffer = ""
            
            elif len(text_buffer) >= target_chunk_size: 
                yield {
                    "clean_text": text_buffer,
                    "commands": [], 
                    "is_end": False
                }
                text_buffer = ""
        
        elif chunk['type'] == 'message_complete':
            # Wait for message_complete, then finalize and yield everything
            print("\n[COMPLETE]", flush=True)
            final_data = parser.finalize()
            
            # Combine any remaining text with finalized data
            remaining_text = text_buffer
            if final_data.get("clean_text") and remaining_text not in final_data.get("clean_text", ""):
                remaining_text = text_buffer + final_data.get("clean_text", "")
            else:
                remaining_text = text_buffer or final_data.get("clean_text", "")
            
            # Always yield the final message
            yield {
                "clean_text": remaining_text.strip(),
                "commands": final_data.get("commands", []),
                "is_end": True
            }
            print()
            break 
            #             "is_end": False
            #         }
            #         text_buffer = ""
                
            #     elif len(text_buffer) >= target_chunk_size: 
            #         yield {
            #             "clean_text": text_buffer,
            #             "commands": [], 
            #             "is_end": False
            #         }
            #         text_buffer = ""
            
            # elif chunk['type'] == 'message_complete':
            #     final_data = parser.finalize()
            #     remaining_text = text_buffer + (final_data.get("clean_text", "") if not clean_segment in final_data.get("clean_text", "") else "")
                
            #     if remaining_text or final_data.get("commands"):
            #         yield {
            #             "clean_text": remaining_text,
            #             "commands": final_data.get("commands", []),
            #             "is_end": True
            #         }
            #     print()
            #     break

# # async def main(image_path: str, chatbot_name: str = None):
# #     """
# #     Main flow: analyze image, create assistant, start chat
# #     """
# #     # Create assistant from image
# #     assistant_info = await create_chatbot_assistant(image_path, chatbot_name)
    
#     # Start interactive chat and process yielded data
#     async for response in interactive_chat(assistant_info):
#         clean_text = response['clean_text']
        
#         # Clean up excessive whitespace while preserving intentional formatting
#         # Remove multiple consecutive newlines, reduce excessive spaces
#         lines = clean_text.split('\n')
#         cleaned_lines = []
        
#         for line in lines:
#             # Strip leading/trailing spaces from each line
#             stripped = line.strip()
#             # Only add non-empty lines
#             if stripped:
#                 cleaned_lines.append(stripped)
        
#         # Join with single space for natural prose
#         cleaned_text = ' '.join(cleaned_lines)
        
#         # Print with debug info but cleaned text
#         print(f"\n[YIELDED] Clean text: {cleaned_text}")
#         print(f"[YIELDED] Commands: {response['commands']}")
#         print(f"[YIELDED] Is end: {response['is_end']}")

# if __name__ == "__main__":
#     # Get image path from command line
#     if len(sys.argv) > 1:
#         image_path = sys.argv[1]
#         chatbot_name = sys.argv[2] if len(sys.argv) > 2 else None
#     else:
#         print("Usage: python image_chatbot.py <image_path> [chatbot_name]")
#         sys.exit(1)
    
#     asyncio.run(main(image_path, chatbot_name))
