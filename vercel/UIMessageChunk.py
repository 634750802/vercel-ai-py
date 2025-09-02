"""
UIMessageChunk implementation for Python based on Vercel AI SDK.

This module provides Python equivalents for the TypeScript UIMessageChunk data structures
from https://github.com/vercel/ai/blob/main/packages/ai/src/ui-message-stream/ui-message-chunks.ts

UIMessageChunk represents streaming updates for AI conversation messages, allowing
granular updates to different parts of a message as it's being generated.
"""

from typing import Any, Dict, Literal, Optional, Union, TypeVar, Generic
from dataclasses import dataclass


# Type aliases
UIDataTypes = Dict[str, Any]
ProviderMetadata = Dict[str, Any]

# Generic type variables
METADATA = TypeVar('METADATA')
DATA_TYPES = TypeVar('DATA_TYPES', bound=UIDataTypes)


@dataclass
class TextStartChunk:
    """Chunk indicating the start of text generation."""
    type: Literal['text-start'] = 'text-start'
    id: str = ""
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class TextDeltaChunk:
    """Chunk containing incremental text content."""
    type: Literal['text-delta'] = 'text-delta'
    delta: str = ""
    id: str = ""
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class TextEndChunk:
    """Chunk indicating the end of text generation."""
    type: Literal['text-end'] = 'text-end'
    id: str = ""
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class ErrorChunk:
    """Chunk representing an error condition."""
    type: Literal['error'] = 'error'
    errorText: str = ""


@dataclass
class ToolInputStartChunk:
    """Chunk indicating tool input generation started."""
    type: Literal['tool-input-start'] = 'tool-input-start'
    toolCallId: str = ""
    toolName: str = ""
    providerMetadata: Optional[ProviderMetadata] = None
    dynamic: Optional[bool] = None


@dataclass
class ToolInputDeltaChunk:
    """Chunk containing incremental tool input text."""
    type: Literal['tool-input-delta'] = 'tool-input-delta'
    toolCallId: str = ""
    inputTextDelta: str = ""


@dataclass
class ToolInputAvailableChunk:
    """Chunk indicating tool input is available."""
    type: Literal['tool-input-available'] = 'tool-input-available'
    toolCallId: str = ""
    toolName: str = ""
    input: Any = None
    providerExecuted: Optional[bool] = None
    providerMetadata: Optional[ProviderMetadata] = None
    dynamic: Optional[bool] = None


@dataclass
class ToolInputErrorChunk:
    """Chunk indicating tool input generation error."""
    type: Literal['tool-input-error'] = 'tool-input-error'
    toolCallId: str = ""
    toolName: str = ""
    input: Any = None
    errorText: str = ""
    providerExecuted: Optional[bool] = None
    providerMetadata: Optional[ProviderMetadata] = None
    dynamic: Optional[bool] = None


@dataclass
class ToolOutputAvailableChunk:
    """Chunk indicating tool output is available."""
    type: Literal['tool-output-available'] = 'tool-output-available'
    toolCallId: str = ""
    output: Any = None
    providerExecuted: Optional[bool] = None
    dynamic: Optional[bool] = None
    preliminary: Optional[bool] = None


@dataclass
class ToolOutputErrorChunk:
    """Chunk indicating tool output error."""
    type: Literal['tool-output-error'] = 'tool-output-error'
    toolCallId: str = ""
    errorText: str = ""
    providerExecuted: Optional[bool] = None
    dynamic: Optional[bool] = None
    preliminary: Optional[bool] = None




@dataclass
class ReasoningStartChunk:
    """Chunk indicating start of reasoning generation."""
    type: Literal['reasoning-start'] = 'reasoning-start'
    id: str = ""
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class ReasoningDeltaChunk:
    """Chunk containing incremental reasoning content."""
    type: Literal['reasoning-delta'] = 'reasoning-delta'
    delta: str = ""
    id: str = ""
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class ReasoningEndChunk:
    """Chunk indicating end of reasoning generation."""
    type: Literal['reasoning-end'] = 'reasoning-end'
    id: str = ""
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class SourceUrlChunk:
    """Chunk containing source URL information."""
    type: Literal['source-url'] = 'source-url'
    url: str = ""
    title: Optional[str] = None
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class SourceDocumentChunk:
    """Chunk containing source document information."""
    type: Literal['source-document'] = 'source-document'
    documentId: str = ""
    title: Optional[str] = None
    content: Optional[str] = None
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class FileChunk:
    """Chunk containing file attachment information."""
    type: Literal['file'] = 'file'
    filename: str = ""
    contentType: str = ""
    data: bytes = b""
    size: Optional[int] = None
    providerMetadata: Optional[ProviderMetadata] = None


@dataclass
class StepStartChunk:
    """Chunk indicating start of a process step."""
    type: Literal['start-step'] = 'start-step'


@dataclass
class StepFinishChunk:
    """Chunk indicating finish of a process step."""
    type: Literal['finish-step'] = 'finish-step'


@dataclass
class MessageMetadataChunk(Generic[METADATA]):
    """Chunk containing message metadata."""
    type: Literal['message-metadata'] = 'message-metadata'
    metadata: METADATA = None


@dataclass
class DataChunk(Generic[DATA_TYPES]):
    """Chunk containing custom data."""
    type: str  # Will be 'data-{type}' format
    data: DATA_TYPES = None
    transient: Optional[bool] = None
    providerMetadata: Optional[ProviderMetadata] = None

    def __post_init__(self):
        if not self.type.startswith('data-'):
            self.type = f'data-{self.type}'


# Add missing control chunks
@dataclass
class StartChunk:
    """Chunk indicating start of message generation."""
    type: Literal['start'] = 'start'
    messageId: Optional[str] = None
    messageMetadata: Optional[Any] = None


@dataclass
class FinishChunk:
    """Chunk indicating finish of message generation."""
    type: Literal['finish'] = 'finish'
    messageMetadata: Optional[Any] = None


@dataclass
class AbortChunk:
    """Chunk indicating message generation was aborted."""
    type: Literal['abort'] = 'abort'
    providerMetadata: Optional[ProviderMetadata] = None


# Union type for all possible UI message chunks
UIMessageChunk = Union[
    TextStartChunk,
    TextDeltaChunk,
    TextEndChunk,
    ErrorChunk,
    ToolInputStartChunk,
    ToolInputDeltaChunk,
    ToolInputAvailableChunk,
    ToolInputErrorChunk,
    ToolOutputAvailableChunk,
    ToolOutputErrorChunk,
    ReasoningStartChunk,
    ReasoningDeltaChunk,
    ReasoningEndChunk,
    SourceUrlChunk,
    SourceDocumentChunk,
    FileChunk,
    StepStartChunk,
    StepFinishChunk,
    MessageMetadataChunk,
    DataChunk,
    StartChunk,
    FinishChunk,
    AbortChunk
]


# Utility functions for working with UI message chunks

def is_text_chunk(chunk: UIMessageChunk) -> bool:
    """
    Check if a chunk is related to text content.
    
    Args:
        chunk: The UI message chunk to check
        
    Returns:
        True if the chunk is text-related, False otherwise
    """
    return chunk.type in ['text-start', 'text-delta', 'text-end']


def is_tool_chunk(chunk: UIMessageChunk) -> bool:
    """
    Check if a chunk is related to tool usage.
    
    Args:
        chunk: The UI message chunk to check
        
    Returns:
        True if the chunk is tool-related, False otherwise
    """
    return chunk.type in [
        'tool-input-start', 'tool-input-delta', 'tool-input-available', 
        'tool-input-error', 'tool-output-available', 'tool-output-error'
    ]


def is_reasoning_chunk(chunk: UIMessageChunk) -> bool:
    """
    Check if a chunk is related to reasoning content.
    
    Args:
        chunk: The UI message chunk to check
        
    Returns:
        True if the chunk is reasoning-related, False otherwise
    """
    return chunk.type in ['reasoning-start', 'reasoning-delta', 'reasoning-end']


def is_data_chunk(chunk: UIMessageChunk) -> bool:
    """
    Check if a chunk is a data chunk.
    
    Args:
        chunk: The UI message chunk to check
        
    Returns:
        True if the chunk is a data chunk, False otherwise
    """
    return hasattr(chunk, 'type') and chunk.type.startswith('data-')


def is_step_chunk(chunk: UIMessageChunk) -> bool:
    """
    Check if a chunk is related to process steps.
    
    Args:
        chunk: The UI message chunk to check
        
    Returns:
        True if the chunk is step-related, False otherwise
    """
    return chunk.type in ['start-step', 'finish-step']


def is_source_chunk(chunk: UIMessageChunk) -> bool:
    """
    Check if a chunk is related to source information.
    
    Args:
        chunk: The UI message chunk to check
        
    Returns:
        True if the chunk is source-related, False otherwise
    """
    return chunk.type in ['source-url', 'source-document']


def get_chunk_id(chunk: UIMessageChunk) -> Optional[str]:
    """
    Extract the ID from a chunk if it has one.
    
    Args:
        chunk: The UI message chunk to extract ID from
        
    Returns:
        The chunk ID if available, None otherwise
    """
    return getattr(chunk, 'id', None)


def get_provider_metadata(chunk: UIMessageChunk) -> Optional[ProviderMetadata]:
    """
    Extract provider metadata from a chunk if it has any.
    
    Args:
        chunk: The UI message chunk to extract metadata from
        
    Returns:
        The provider metadata if available, None otherwise
    """
    return getattr(chunk, 'providerMetadata', None)


# Factory functions for creating common chunk types

def create_text_delta_chunk(
    delta: str,
    chunk_id: str = "",
    provider_metadata: Optional[ProviderMetadata] = None
) -> TextDeltaChunk:
    """
    Create a text delta chunk.
    
    Args:
        delta: The incremental text content
        chunk_id: Optional chunk ID
        provider_metadata: Optional provider metadata
        
    Returns:
        A TextDeltaChunk instance
    """
    return TextDeltaChunk(
        delta=delta,
        id=chunk_id,
        providerMetadata=provider_metadata
    )


def create_tool_input_chunk(
    tool_call_id: str,
    tool_name: str,
    input_data: Any,
    provider_executed: Optional[bool] = None,
    provider_metadata: Optional[ProviderMetadata] = None,
    dynamic: Optional[bool] = None
) -> ToolInputAvailableChunk:
    """
    Create a tool input available chunk.
    
    Args:
        tool_call_id: The tool call identifier
        tool_name: Name of the tool
        input_data: Input data for the tool
        provider_executed: Whether the provider executed the tool
        provider_metadata: Optional provider metadata
        dynamic: Whether this is a dynamic tool
        
    Returns:
        A ToolInputAvailableChunk instance
    """
    return ToolInputAvailableChunk(
        toolCallId=tool_call_id,
        toolName=tool_name,
        input=input_data,
        providerExecuted=provider_executed,
        providerMetadata=provider_metadata,
        dynamic=dynamic
    )


def create_error_chunk(error_text: str) -> ErrorChunk:
    """
    Create an error chunk.
    
    Args:
        error_text: The error message
        
    Returns:
        An ErrorChunk instance
    """
    return ErrorChunk(errorText=error_text)


def create_data_chunk(
    data_type: str,
    data: Any,
    provider_metadata: Optional[ProviderMetadata] = None
) -> DataChunk:
    """
    Create a data chunk.
    
    Args:
        data_type: The type of data (will be prefixed with 'data-')
        data: The data content
        provider_metadata: Optional provider metadata
        
    Returns:
        A DataChunk instance
    """
    return DataChunk(
        type=data_type,  # __post_init__ will add 'data-' prefix
        data=data,
        providerMetadata=provider_metadata
    )