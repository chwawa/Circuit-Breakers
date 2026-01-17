# Install: pip install backboard-sdk
import asyncio
import json
from backboard import BackboardClient

async def main():
    # Initialize the Backboard client
    client = BackboardClient(api_key="YOUR_API_KEY")

    # Define a tool (function) for the assistant to call
    tools = [{
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }]

    # Create an assistant with the tool
    assistant = await client.create_assistant(
        name="Weather Assistant",
        system_prompt="You are a helpful weather assistant",
        tools=tools
    )

    # Create a thread
    thread = await client.create_thread(assistant.assistant_id)

    # Send a message and stream the response
    async for chunk in await client.add_message(
        thread_id=thread.thread_id,
        content="What's the weather in San Francisco?",
        stream=True
    ):
        # Stream content chunks
        if chunk['type'] == 'content_streaming':
            print(chunk['content'], end='', flush=True)
        
        # Handle tool call requirement
        elif chunk['type'] == 'tool_submit_required':
            run_id = chunk['run_id']
            tool_calls = chunk['tool_calls']
            
            # Process each tool call
            tool_outputs = []
            for tc in tool_calls:
                function_name = tc['function']['name']
                function_args = json.loads(tc['function']['arguments'])
                
                if function_name == 'get_current_weather':
                    # Execute your function
                    location = function_args['location']
                    weather_data = {
                        "temperature": "68°F",
                        "condition": "Sunny",
                        "location": location
                    }
                    
                    tool_outputs.append({
                        "tool_call_id": tc['id'],
                        "output": json.dumps(weather_data)
                    })
            
            # Submit tool outputs and stream the final response
            async for tool_chunk in await client.submit_tool_outputs(
                thread_id=thread.thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs,
                stream=True
            ):
                if tool_chunk['type'] == 'content_streaming':
                    print(tool_chunk['content'], end='', flush=True)
                elif tool_chunk['type'] == 'message_complete':
                    break
            break

if __name__ == "__main__":
    asyncio.run(main())