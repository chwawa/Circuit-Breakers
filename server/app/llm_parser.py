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
    """
    Parse LLM-generated text with embedded commands.
    
    Args:
        text: Raw LLM text with commands in [[COMMAND]] format
        track_positions: If True, track character positions of commands in original text
        
    Returns:
        ParsedLLMOutput containing clean_text, commands, and optional positions
        
    Example:
        >>> text = "Hi!! [[JUMP]] I'm excited to meet you [[WAVE]]"
        >>> result = parse_llm_text(text)
        >>> result.clean_text
        "Hi!! I'm excited to meet you"
        >>> result.commands
        ["JUMP", "WAVE"]
    """
    # Pattern to match [[COMMAND]] format
    pattern = r'\[\[([A-Z_][A-Z0-9_]*)\]\]'
    
    commands = []
    positions = [] if track_positions else None
    
    def replace_command(match):
        commands.append(match.group(1))
        if positions is not None:
            positions.append(match.start())
        return ""
    
    # Remove command markers and extract commands
    clean_text = re.sub(pattern, replace_command, text)
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return ParsedLLMOutput(
        clean_text=clean_text,
        commands=commands,
        positions=positions
    )


def parse_llm_text_preserve_spacing(text: str) -> ParsedLLMOutput:
    """
    Parse LLM text while preserving original spacing (only removes command markers).
    
    Useful if you want to maintain exact spacing and only extract commands.
    
    Args:
        text: Raw LLM text with commands in [[COMMAND]] format
        
    Returns:
        ParsedLLMOutput with original spacing preserved around command removal
    """
    pattern = r'\[\[([A-Z_][A-Z0-9_]*)\]\]'
    
    commands = []
    
    def replace_command(match):
        commands.append(match.group(1))
        return ""
    
    clean_text = re.sub(pattern, replace_command, text)
    
    return ParsedLLMOutput(
        clean_text=clean_text.strip(),
        commands=commands,
        positions=None
    )
