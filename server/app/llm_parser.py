"""
Parser for LLM-generated text with embedded command markers.

Parses text containing commands in [[COMMAND]] format and extracts:
- Clean text with commands removed
- List of commands in order of appearance
- Optional: positions of commands in the original text
"""

import re
from typing import NamedTuple, Optional


class ParsedLLMOutput(NamedTuple):
    """Result of parsing LLM output text."""
    clean_text: str
    commands: list[str]
    positions: Optional[list[int]] = None


def parse_llm_text(text: str, track_positions: bool = False) -> ParsedLLMOutput:
    """Parse LLM-generated text with embedded commands."""

    # Pattern to match [[COMMAND]] or [COMMAND] format
    pattern = r'\[{1,2}([A-Za-z_][A-Za-z0-9_]*)\]{1,2}'

    commands = []
    positions = [] if track_positions else None

    # counts the word index in the clean text (for command positions) 
    # note: 0 - base index
    def replace_command(match):
        commands.append(match.group(1))

        if positions is not None:
            before = text[:match.start()]               
            word_index = len(before.strip().split()) 
            positions.append(word_index)

        return ""

    clean_text = re.sub(pattern, replace_command, text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    return ParsedLLMOutput(
        clean_text=clean_text,
        commands=commands,
        positions=positions
    )