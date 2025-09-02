"""
Streaming tools for processing UIMessageChunk streams and generating UIMessage objects.

This module provides utilities for accumulating streaming message chunks and building
complete UIMessage objects from the accumulated data. It also includes SSE (Server-Sent Events)
parsing capabilities to transform raw streaming data into UIMessageChunk objects.

This is the main module that re-exports all streaming functionality for backward compatibility.
The actual implementation has been split into specialized modules:
- stream_processor: Core message processing and accumulation
- sse_parser: SSE stream parsing functionality  
- stream_integration: Combined SSE + message processing
"""

# Re-export all functionality from specialized modules for backward compatibility

# Core stream processing
from .stream_processor import (
    StreamState,
    UIMessageStreamProcessor, 
    StreamBuffer,
    process_chunk_stream,
    create_streaming_processor
)

# SSE parsing
from .sse_parser import (
    SSEParseError,
    SSEEvent, 
    SSEParser,
    parse_sse_to_chunks
)

# Integrated functionality
from .stream_integration import (
    SSEStreamProcessor,
    sse_stream_to_message
)

# Make all classes and functions available at module level
__all__ = [
    # Stream processing
    'StreamState',
    'UIMessageStreamProcessor',
    'StreamBuffer', 
    'process_chunk_stream',
    'create_streaming_processor',
    
    # SSE parsing
    'SSEParseError',
    'SSEEvent',
    'SSEParser',
    'parse_sse_to_chunks',
    
    # Integration
    'SSEStreamProcessor', 
    'sse_stream_to_message'
]