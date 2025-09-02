"""
SSE (Server-Sent Events) parsing functionality for UIMessageChunk streams.

This module provides utilities for parsing raw SSE streams and converting them
to UIMessageChunk objects for further processing.
"""

from typing import Dict, List, Optional, Iterator, Union
from dataclasses import dataclass
import json

from .UIMessageChunk import (
    UIMessageChunk, TextStartChunk, TextDeltaChunk, TextEndChunk,
    ToolInputStartChunk, ToolInputDeltaChunk, ToolInputAvailableChunk, 
    ToolInputErrorChunk, ToolOutputAvailableChunk, ToolOutputErrorChunk,
    ReasoningStartChunk, ReasoningDeltaChunk, ReasoningEndChunk, 
    SourceUrlChunk, SourceDocumentChunk, FileChunk, StepStartChunk, 
    StepFinishChunk, MessageMetadataChunk, DataChunk, ErrorChunk,
    StartChunk, FinishChunk, AbortChunk
)


class SSEParseError(Exception):
    """Exception raised when SSE parsing fails."""
    pass


@dataclass
class SSEEvent:
    """Represents a parsed SSE event."""
    data: Optional[str] = None


class SSEParser:
    """
    Parser for Server-Sent Events (SSE) streams that converts raw SSE data 
    to UIMessageChunk objects.
    
    Supports the standard SSE format with 'data: <JSON>' lines and 'data: [DONE]' markers.
    """
    
    def __init__(self, chunk_factory: Optional[Dict[str, type]] = None):
        """
        Initialize SSE parser.
        
        Args:
            chunk_factory: Optional mapping of chunk type names to classes for custom chunks
        """
        self.chunk_factory = chunk_factory or {}
        self.buffer = ""
        
    def parse_sse_line(self, line: str) -> Optional[SSEEvent]:
        """
        Parse a single SSE line.
        
        Args:
            line: Raw SSE line
            
        Returns:
            SSEEvent if the line represents a complete event, None otherwise
        """
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith(':'):
            return None
            
        # Handle field: value format
        if ':' in line:
            field, value = line.split(':', 1)
            field = field.strip()
            value = value.strip()

            if field == 'data':
                return SSEEvent(data=value)
                    
        return None
    
    def parse_chunk_json(self, json_data: str) -> Optional[UIMessageChunk]:
        """
        Parse JSON data into a UIMessageChunk.
        
        Args:
            json_data: JSON string representing chunk data
            
        Returns:
            UIMessageChunk object or None if parsing fails
            
        Raises:
            SSEParseError: If JSON is malformed or chunk type is unknown
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise SSEParseError(f"Invalid JSON in chunk: {e}")
            
        if not isinstance(data, dict) or 'type' not in data:
            raise SSEParseError("Chunk must be a JSON object with 'type' field")
            
        chunk_type = data['type']
        
        # Map chunk types to their corresponding classes
        chunk_classes = {
            'text-start': TextStartChunk,
            'text-delta': TextDeltaChunk,
            'text-end': TextEndChunk,
            'reasoning-start': ReasoningStartChunk,
            'reasoning-delta': ReasoningDeltaChunk,
            'reasoning-end': ReasoningEndChunk,
            'tool-input-start': ToolInputStartChunk,
            'tool-input-delta': ToolInputDeltaChunk,
            'tool-input-available': ToolInputAvailableChunk,
            'tool-input-error': ToolInputErrorChunk,
            'tool-output-available': ToolOutputAvailableChunk,
            'tool-output-error': ToolOutputErrorChunk,
            'source-url': SourceUrlChunk,
            'source-document': SourceDocumentChunk,
            'file': FileChunk,
            'start-step': StepStartChunk,
            'finish-step': StepFinishChunk,
            'message-metadata': MessageMetadataChunk,
            'error': ErrorChunk,
            'start': StartChunk,
            'finish': FinishChunk,
            'abort': AbortChunk,
        }
        
        # Add custom chunk types
        chunk_classes.update(self.chunk_factory)
        
        # Handle data chunks (data-*)
        if chunk_type.startswith('data-'):
            return DataChunk(
                type=chunk_type,
                data=data.get('data'),
                providerMetadata=data.get('providerMetadata')
            )

        chunk_class = chunk_classes.get(chunk_type)
        if not chunk_class:
            raise SSEParseError(f"Unknown chunk type: {chunk_type}")
        
        try:
            # Use data directly since Python implementation now matches TypeScript field names
            return chunk_class(**data)
        except TypeError as e:
            raise SSEParseError(f"Failed to create {chunk_type} chunk: {e}")
    
    def parse_sse_stream(self, stream_lines: Iterator[str] | Iterator[bytes]) -> Iterator[UIMessageChunk]:
        """
        Parse an SSE stream and yield UIMessageChunk objects.
        
        Args:
            stream_lines: Iterator of raw SSE lines
            
        Yields:
            UIMessageChunk objects parsed from the stream
            
        Raises:
            SSEParseError: If parsing fails
        """
        for line in stream_lines:
            event = self.parse_sse_line(str(line))
            if event and event.data:
                # Check for [DONE] marker
                if event.data.strip() == '[DONE]':
                    break
                    
                chunk = self.parse_chunk_json(event.data)
                if chunk:
                    yield chunk
    
    def parse_sse_string(self, sse_data: str) -> List[UIMessageChunk]:
        """
        Parse SSE data from a string.
        
        Args:
            sse_data: Complete SSE data as string
            
        Returns:
            List of UIMessageChunk objects
        """
        lines = sse_data.split('\n')
        return list(self.parse_sse_stream(iter(lines)))


# Utility functions

def parse_sse_to_chunks(
    sse_stream: Union[Iterator[str], str],
    chunk_factory: Optional[Dict[str, type]] = None
) -> Iterator[UIMessageChunk]:
    """
    Convenience function to parse SSE stream into UIMessageChunk objects.
    
    Args:
        sse_stream: SSE data as string or iterator of lines
        chunk_factory: Optional custom chunk type mappings
        
    Yields:
        UIMessageChunk objects parsed from SSE data
        
    Example:
        >>> sse_data = '''data: {"type": "text-start", "id": "msg-1"}
        ... data: {"type": "text-delta", "delta": "Hello"}
        ... data: {"type": "text-end"}
        ... data: [DONE]'''
        >>> chunks = list(parse_sse_to_chunks(sse_data))
        >>> len(chunks)  # 3
    """
    parser = SSEParser(chunk_factory)
    
    if isinstance(sse_stream, str):
        return parser.parse_sse_stream(iter(sse_stream.split('\n')))
    else:
        return parser.parse_sse_stream(sse_stream)