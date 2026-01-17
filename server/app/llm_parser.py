"""
Parser for LLM-generated text with embedded command markers.

Parses text containing commands in [[COMMAND]] format and extracts:
- Clean text with commands removed
- List of commands in order of appearance
"""

import re

class StreamParser:
    def __init__(self):
        self.buffer = ""
        self.clean_text = "" # stores full history
        self.commands = []   # stores all found commands

    def parse_chunk(self, chunk: str):
        """
        Processes a chunk and returns any newly confirmed clean text 
        and any newly completed commands.
        """
        self.buffer += chunk
        new_clean_text = ""
        new_command = ""
        
        while "[[" in self.buffer and "]]" in self.buffer:
            start = self.buffer.find("[[")
            end = self.buffer.find("]]")
            
            if start < end:
                # Text before the command is now confirmed "clean"
                text_segment = self.buffer[:start]
                new_clean_text += text_segment
                self.clean_text += text_segment
                
                # Extract the command
                command = self.buffer[start+2 : end]
                new_command += command
                self.commands += command
                
                # Advance buffer
                self.buffer = self.buffer[end+2:]
            else:
                # If ]] appears before [[, it's malformed; clear it
                self.buffer = self.buffer[end+2:]
        
        if "[[" not in self.buffer:
            new_clean_text += self.buffer
            self.clean_text += self.buffer
            self.buffer = ""
            
        return new_clean_text, new_command