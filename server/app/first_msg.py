import json
from llm_parser import StreamParser

async def backboard_stream_generator(bb_client, prompt: str, results_container: str, final_results: bool = False):
    """
    Handles the connection to Backboard and yields parsed JSON chunks.
    """
    parser = StreamParser()
    
    # 1. Setup Assistant/Thread
    assistant = await bb_client.create_assistant(
        name="Snoopy", 
        description="You are Snoopy, the beloved beagle from the Peanuts cartoons, films, and television series. Include one-word actions within your messages with [[ACTION]] markers."
    )
    thread = await bb_client.create_thread(assistant.assistant_id)

    # 2. Add message and get stream
    stream = await bb_client.add_message(
        thread_id=thread.thread_id,
        content=prompt,
        llm_provider="google",
        model_name="gemini-2.5-flash-lite",
        stream=True
    )

    # 3. Process the stream
    async for chunk in stream:
        if chunk['type'] == 'content_streaming':
            raw_text = chunk['content']
            
            # Calls llm_parser to parse chunk
            clean_segment, new_cmds = parser.parse_chunk(raw_text)
            
            if clean_segment or new_cmds:
                yield json.dumps({
                    "clean_text": clean_segment,
                    "command": new_cmds, 
                    "is_end": False
                }) + "\n"
        
        elif chunk['type'] == 'message_complete':
            break

        final_data = parser.finalize()
        results_container.update(final_data)
        
        # Send one last packet to signal completion
        yield json.dumps({
            "clean_text": "", 
            "command": "",
            "is_end": True
        }) + "\n"