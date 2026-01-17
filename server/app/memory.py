# Install: pip install backboard-sdk
import asyncio
from backboard import BackboardClient

async def main():
    # Initialize the Backboard client
    client = BackboardClient(api_key="YOUR_API_KEY")
    
    # Create an assistant
    assistant = await client.create_assistant(
        name="Memory Assistant",
        system_prompt="You are a helpful assistant with persistent memory"
    )
    
    # Create first thread and share information
    thread1 = await client.create_thread(assistant.assistant_id)
    
    # Share information with memory enabled (streaming)
    print("Sharing info...")
    memory_op_id = None
    async for chunk in await client.add_message(
        thread_id=thread1.thread_id,
        content="My name is Sarah and I work as a software engineer at Google.",
        memory="Auto",  # Enable memory - automatically saves relevant info
        stream=True
    ):
        if chunk['type'] == 'content_streaming':
            print(chunk['content'], end='', flush=True)
        elif chunk['type'] == 'memory_retrieved':
            # Shows when memories are being searched
            memories = chunk.get('memories', [])
            if memories:
                print(f"\n[Found {len(memories)} memories]")
        elif chunk['type'] == 'run_ended':
            memory_op_id = chunk.get('memory_operation_id')
    print("\n")
    
    # Optional: Poll for memory operation completion
    # if memory_op_id:
    #     import time
    #     while True:
    #         status_response = requests.get(
    #             f"{base_url}/assistants/memories/operations/{memory_op_id}",
    #             headers={"X-API-Key": api_key}
    #         )
    #         if status_response.status_code == 200:
    #             data = status_response.json()
    #             if data.get("status") in ("COMPLETED", "ERROR"):
    #                 print(f"Memory operation: {data.get('status')}")
    #                 break
    #         time.sleep(1)
    
    # Create a new thread to test memory recall
    thread2 = await client.create_thread(assistant.assistant_id)
    
    # Ask what the assistant remembers (streaming)
    print("Testing memory recall...")
    async for chunk in await client.add_message(
        thread_id=thread2.thread_id,
        content="What do you remember about me?",
        memory="Auto",  # Searches and retrieves saved memories
        stream=True
    ):
        if chunk['type'] == 'content_streaming':
            print(chunk['content'], end='', flush=True)
    print("\n")
    # Should mention: Sarah, Google, software engineer

if __name__ == "__main__":
    asyncio.run(main())