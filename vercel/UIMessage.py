"""
UIMessage implementation for Python based on Vercel AI SDK.

This module provides Python equivalents for the TypeScript UIMessage data structures
from https://github.com/vercel/ai/blob/main/packages/ai/src/ui/ui-messages.ts

The UIMessage structure represents AI conversation messages with rich metadata and
support for various message parts including text, tools, files, and more.
"""

from typing import Any, Dict, List, Literal, Optional, Union, TypeVar, Generic
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Type aliases
UIDataTypes = Dict[str, Any]
UITools = Dict[str, Any]
ProviderMetadata = Dict[str, Any]

# Generic type variables for UIMessage
METADATA = TypeVar('METADATA')
DATA_PARTS = TypeVar('DATA_PARTS', bound=UIDataTypes)
TOOLS = TypeVar('TOOLS', bound=UITools)

# Role type definition
Role = Literal['system', 'user', 'assistant']

# State type for streaming parts
StreamingState = Literal['streaming', 'done']

# Tool state type
ToolState = Literal['input-streaming', 'input-available', 'output-available', 'output-error']


@dataclass
class BaseUIPart(ABC):
    """Base class for all UI message parts."""

    @property
    @abstractmethod
    def type(self) -> str:
        """Return the type identifier for this part."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert the part to a dictionary for JSON serialization."""
        result = asdict(self)
        result['type'] = self.type
        # Remove None/null values
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class TextUIPart(BaseUIPart):
    """Text content part of a UI message."""
    text: str
    state: Optional[StreamingState] = None
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return 'text'


@dataclass
class ReasoningUIPart(BaseUIPart):
    """Reasoning content part showing AI's thought process."""
    text: str
    state: Optional[StreamingState] = None
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return 'reasoning'


@dataclass
class ToolUIPart(BaseUIPart):
    """Tool usage part of a UI message."""
    toolCallId: str
    toolName: str
    state: ToolState
    args: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return f'tool-{self.toolName}'


@dataclass
class DynamicToolUIPart(BaseUIPart):
    """Dynamic tool usage part with runtime-determined behavior."""
    toolCallId: str
    toolName: str
    state: ToolState
    input: Optional[Any] = None
    output: Optional[Any] = None
    errorText: Optional[str] = None
    callProviderMetadata: Optional[ProviderMetadata] = None
    preliminary: Optional[bool] = None

    @property
    def type(self) -> str:
        return 'dynamic-tool'


@dataclass
class SourceUrlUIPart(BaseUIPart):
    """Source URL reference part."""
    sourceId: str
    url: str
    title: Optional[str] = None
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return 'source-url'


@dataclass
class SourceDocumentUIPart(BaseUIPart):
    """Source document reference part."""
    sourceId: str
    title: Optional[str] = None
    content: Optional[str] = None
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return 'source-document'


@dataclass
class FileUIPart(BaseUIPart):
    """File attachment part."""
    mediaType: str
    filename: Optional[str] = None
    url: str = ""
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return 'file'


@dataclass
class DataUIPart(BaseUIPart):
    """Generic data part for custom data types."""
    data: Any
    providerMetadata: Optional[ProviderMetadata] = None

    @property
    def type(self) -> str:
        return 'data'


@dataclass
class StepStartUIPart(BaseUIPart):
    """Step start marker for multi-step processes."""

    @property
    def type(self) -> str:
        return 'step-start'


# Union type for all possible UI message parts
UIMessagePart = Union[
    TextUIPart,
    ReasoningUIPart,
    ToolUIPart,
    DynamicToolUIPart,
    SourceUrlUIPart,
    SourceDocumentUIPart,
    FileUIPart,
    DataUIPart,
    StepStartUIPart
]


@dataclass
class UIMessage(Generic[METADATA, DATA_PARTS, TOOLS]):
    """
    Represents a UI message in an AI conversation.
    
    This is the main data structure that holds conversation messages with
    rich metadata and support for various content types through parts.
    
    Attributes:
        id: Unique identifier for the message
        role: The role of the message sender ('system', 'user', or 'assistant')
        metadata: Optional metadata associated with the message
        parts: List of message parts that make up the content
    """

    id: str
    role: Role
    parts: List[UIMessagePart]
    metadata: Optional[METADATA] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for JSON serialization."""
        result = {
            'id': self.id,
            'role': self.role,
            'parts': [part.to_dict() for part in self.parts]
        }
        # Only include metadata if it's not None
        if self.metadata is not None:
            result['metadata'] = self.metadata
        return result

    def as_text_content(self) -> str:
        """
        Return the text part of the message.
        :return:
        """
        return ''.join(map(lambda part: part.text if isinstance(part, TextUIPart) else '', self.parts))


# Utility functions for working with UI message parts

def is_tool_ui_part(part: UIMessagePart) -> bool:
    """
    Check if a UI message part is a tool part.
    
    Args:
        part: The UI message part to check
        
    Returns:
        True if the part is a ToolUIPart, False otherwise
    """
    return isinstance(part, ToolUIPart)


def is_dynamic_tool_ui_part(part: UIMessagePart) -> bool:
    """
    Check if a UI message part is a dynamic tool part.
    
    Args:
        part: The UI message part to check
        
    Returns:
        True if the part is a DynamicToolUIPart, False otherwise
    """
    return isinstance(part, DynamicToolUIPart)


def get_tool_name(part: UIMessagePart) -> Optional[str]:
    """
    Extract the tool name from a tool UI part.
    
    Args:
        part: The UI message part to extract the tool name from
        
    Returns:
        The tool name if the part is a ToolUIPart, None otherwise
    """
    if isinstance(part, (ToolUIPart, DynamicToolUIPart)):
        return part.toolName
    return None


def get_tool_or_dynamic_tool_name(part: UIMessagePart) -> Optional[str]:
    """
    Extract the tool name from either a tool or dynamic tool UI part.
    
    Args:
        part: The UI message part to extract the tool name from
        
    Returns:
        The tool name if the part is a ToolUIPart or DynamicToolUIPart, None otherwise
    """
    if isinstance(part, (ToolUIPart, DynamicToolUIPart)):
        return part.toolName
    return None


def create_text_message(
        id: str,
        role: Role,
        text: str,
        metadata: Optional[Any] = None
) -> UIMessage:
    """
    Create a simple text UI message.
    
    Args:
        id: Unique identifier for the message
        role: The role of the message sender
        text: The text content of the message
        metadata: Optional metadata for the message
        
    Returns:
        A UIMessage containing a single TextUIPart
    """
    return UIMessage(
        id=id,
        role=role,
        parts=[TextUIPart(text=text)],
        metadata=metadata
    )


def create_tool_message(
        id: str,
        role: Role,
        tool_name: str,
        args: Dict[str, Any],
        result: Optional[Any] = None,
        metadata: Optional[Any] = None
) -> UIMessage:
    """
    Create a tool usage UI message.
    
    Args:
        id: Unique identifier for the message
        role: The role of the message sender
        tool_name: Name of the tool being used
        args: Arguments passed to the tool
        result: Optional result from the tool execution
        metadata: Optional metadata for the message
        
    Returns:
        A UIMessage containing a single ToolUIPart
    """
    return UIMessage(
        id=id,
        role=role,
        parts=[ToolUIPart(
            toolCallId="default-call-id",
            toolName=tool_name,
            state="output-available",
            args=args,
            result=result
        )],
        metadata=metadata
    )
