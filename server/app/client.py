import httpx
from llm_parser import StreamParser

def run_test():
    parser = StreamParser()
    url = "http://127.0.0.1:8000/stream"

    with httpx.stream("GET", url) as r:
        for chunk in r.iter_text():
            parser.parse_chunk(chunk)
            
            # Show progress in terminal
            print(f"Current Clean Text: {parser.clean_text}")
            print(f"Found Commands: {parser.commands}")
            print("-" * 20)

    final_result = parser.finalize()
    print("\nFINAL JSON RESPONSE:")
    print(final_result)

if __name__ == "__main__":
    run_test()