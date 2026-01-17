import re
from typing import Optional, Tuple, Dict, Any

CMD_RE = re.compile(r"\[\[([A-Z_][A-Z0-9_]*)\]\]")

class StreamParser:
    def __init__(self):
        self.buffer = ""
        self.clean_text = ""   # full history
        self.commands = []     # list of commands (strings)

    def parse_chunk(self, chunk: str) -> Tuple[str, Optional[str]]:
        """
        Add streamed chunk, and return:
          - newly confirmed clean text
          - at most ONE completed command (or None)
        """
        self.buffer += chunk
        new_clean = ""

        # If there is at least one full command in the buffer, emit ONLY the first one.
        m = CMD_RE.search(self.buffer)
        if m:
            start, end = m.span()
            cmd = m.group(1)

            # everything before [[COMMAND]] is now confirmed clean
            text_segment = self.buffer[:start]
            new_clean += text_segment
            self.clean_text += text_segment

            # record + emit exactly one command
            self.commands.append(cmd)

            # remove through the end of this command, keep the rest for later
            self.buffer = self.buffer[end:]

            return new_clean, cmd

        # If no full command exists, we can safely flush text that
        # cannot be part of a future command start.
        # Keep at most 1 '[' in case a command marker '[[' starts across chunk boundary.
        last_bracket = self.buffer.rfind("[")
        if last_bracket == -1:
            # no possible command start
            new_clean += self.buffer
            self.clean_text += self.buffer
            self.buffer = ""
        else:
            # flush everything before the last '['
            flush = self.buffer[:last_bracket]
            new_clean += flush
            self.clean_text += flush
            self.buffer = self.buffer[last_bracket:]

        return new_clean, None

    def finalize(self) -> Dict[str, Any]:
        """
        Flush remaining buffer as clean text.
        (If buffer contains an unmatched '[[' it will be treated as literal text.)
        """
        if self.buffer:
            self.clean_text += self.buffer
            self.buffer = ""

        return {
            "clean_text": self.clean_text,
            "commands": self.commands,
            "is_end": True,
        }
