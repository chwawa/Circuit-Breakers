import json
from llm_parser import StreamParser

async def backboard_stream_generator(bb_client, prompt: str, results_container: dict):
    """
    Handles the connection to Backboard and yields parsed JSON chunks.
    """
    parser = StreamParser()
    
    # 1. Setup Assistant/Thread
    assistant = await bb_client.create_assistant(
        name="Assistant", 
        system_prompt="Return text with [[COMMAND]] markers."
    )
    thread = await bb_client.create_thread(assistant.assistant_id)

    # 2. Add message and get stream
    stream = await bb_client.add_message(
        thread_id=thread.thread_id,
        content=prompt,
        llm_provider="openrouter",
        model_name="deepseek/deepseek-chat",
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
                    "new_text": clean_segment,
                    "new_commands": new_cmds, 
                    "is_final": False
                }) + "\n"
        
        elif chunk['type'] == 'message_complete':
            break

        final_data = parser.finalize()
        results_container.update(final_data)
        
        # Send one last packet to signal completion
        yield json.dumps({
            "audio_chunk": "", 
            "commands": [],
            "is_final": True
        }) + "\n"