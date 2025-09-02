"""
Stream integration utilities combining SSE parsing with message processing.

This module provides high-level utilities that combine SSE parsing and message
processing for easy end-to-end stream handling.
"""

from typing import Dict, Optional, Union, Iterator

from .UIMessage import UIMessage
from .UIMessageChunk import UIMessageChunk
from .sse_parser import SSEParser, parse_sse_to_chunks, SSEParseError
from .stream_processor import UIMessageStreamProcessor


class SSEStreamProcessor:
    """
    Combined SSE parser and UIMessage processor for real-time streaming.
    
    Processes SSE data incrementally and maintains message state.
    """
    
    def __init__(self, message_id: Optional[str] = None, chunk_factory: Optional[Dict[str, type]] = None):
        """
        Initialize combined processor.
        
        Args:
            message_id: Optional default message ID
            chunk_factory: Optional custom chunk type mappings
        """
        self.sse_parser = SSEParser(chunk_factory)
        self.message_processor = UIMessageStreamProcessor(message_id)
        
    def process_sse_line(self, line: str) -> Optional[UIMessage]:
        """
        Process a single SSE line and update message state.
        
        Args:
            line: Raw SSE line
            
        Returns:
            Complete UIMessage if stream ended, None if still processing
        """
        event = self.sse_parser.parse_sse_line(line)
        if event and event.data:
            # Check for completion
            if event.data.strip() == '[DONE]':
                return self.message_processor.build_message()
                
            try:
                chunk = self.sse_parser.parse_chunk_json(event.data)
                if chunk:
                    self.message_processor.process_chunk(chunk)
            except SSEParseError:
                pass  # Skip malformed chunks
                
        return None
    
    def build_message(self) -> UIMessage:
        """Get current message state."""
        return self.message_processor.build_message()
    
    def reset(self):
        """Reset both parsers for a new message."""
        self.message_processor.reset()


def sse_stream_to_message(
    sse_stream: Union[Iterator[str], str],
    message_id: Optional[str] = None,
    chunk_factory: Optional[Dict[str, type]] = None
) -> UIMessage:
    """
    Convert an SSE stream directly to a complete UIMessage.
    
    Args:
        sse_stream: SSE data as string or iterator of lines
        message_id: Optional message ID
        chunk_factory: Optional custom chunk type mappings
        
    Returns:
        Complete UIMessage built from SSE stream
        
    Example:
        >>> sse_data = '''data: {"type": "text-start", "id": "msg-1"}
        ... data: {"type": "text-delta", "delta": "Hello world"}
        ... data: {"type": "text-end"}
        ... data: [DONE]'''
        >>> message = sse_stream_to_message(sse_data)
        >>> message.parts[0].text  # "Hello world"
    """
    chunks = parse_sse_to_chunks(sse_stream, chunk_factory)
    processor = UIMessageStreamProcessor(message_id)
    return processor.process_stream(chunks), processor