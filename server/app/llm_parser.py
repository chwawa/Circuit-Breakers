import re
from typing import Tuple, Dict, Any

# Updated Regex to be more robust for streaming
CMD_RE = re.compile(r"\[\[([A-Z_][A-Z0-9_]*)\]\]")

class StreamParser:
    def __init__(self):
        self.buffer = ""
        self.clean_text = ""   # Cumulative full history
        self.commands = []     # Cumulative list of all commands

    def parse_chunk(self, chunk: str) -> Tuple[str, list]:
        """
        Processes a chunk and returns ONLY confirmed clean text and 
        ONLY the commands found in this specific chunk.
        """
        self.buffer += chunk
        new_clean = ""
        commands_found = []

        while True:
            m = CMD_RE.search(self.buffer)
            if not m:
                break

            start, end = m.span()
            cmd = m.group(1)

            # Confirm text BEFORE the command as clean
            text_segment = self.buffer[:start]
            new_clean += text_segment
            self.clean_text += text_segment

            # Store the command
            self.commands.append(cmd)
            commands_found.append(cmd)

            # Advance buffer past the found command
            self.buffer = self.buffer[end:]

        first_bracket = self.buffer.find("[")
        
        if first_bracket == -1:
            # No brackets at all: the entire buffer is clean text
            new_clean += self.buffer
            self.clean_text += self.buffer
            self.buffer = ""
        elif first_bracket > 0:
            # Text exists before the first '[': that part is definitely clean
            flush = self.buffer[:first_bracket]
            new_clean += flush
            self.clean_text += flush
            self.buffer = self.buffer[first_bracket:]

        return new_clean, commands_found

    def finalize(self) -> Dict[str, Any]:
        """
        Cleans up any remaining text in the buffer when the stream ends.
        """
        remaining = self.buffer
        if remaining:
            self.clean_text += remaining
            self.buffer = ""

        return {
            "clean_text": self.clean_text,
            "new_clean": remaining, # Helpful for the final yield in your assistant
            "commands": self.commands,
            "is_end": True,
        }