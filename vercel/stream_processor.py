"""
Stream processor for converting UIMessageChunk streams to UIMessage objects.

This module contains the core functionality for processing streaming message chunks
and building complete UIMessage objects from accumulated streaming data.
"""

from typing import Dict, List, Optional, Iterator, Any, Literal, Union
from dataclasses import dataclass, field
import uuid

from .UIMessageChunk import (
    UIMessageChunk, TextStartChunk, TextDeltaChunk, TextEndChunk,
    ToolInputStartChunk, ToolInputDeltaChunk, ToolInputAvailableChunk, 
    ToolInputErrorChunk, ToolOutputAvailableChunk, ToolOutputErrorChunk,
    ReasoningStartChunk, ReasoningDeltaChunk, ReasoningEndChunk, 
    SourceUrlChunk, SourceDocumentChunk, FileChunk, StepStartChunk, 
    StepFinishChunk, MessageMetadataChunk, DataChunk, ErrorChunk,
    StartChunk, FinishChunk, AbortChunk
)
from .UIMessage import (
    UIMessage, TextUIPart, ToolUIPart, DynamicToolUIPart, ReasoningUIPart, 
    SourceUrlUIPart, SourceDocumentUIPart, FileUIPart, StepStartUIPart,
    DataUIPart, Role, ToolState
)


@dataclass
class ToolCall:
    """Internal representation of a tool call during streaming."""
    id: str = ""
    name: str = ""
    args: Optional[Any] = None
    result: Optional[Any] = None
    dynamic: bool = False
    provider_executed: Optional[bool] = None
    preliminary: Optional[bool] = None
    input_text: str = ""
    input_error: Optional[str] = None
    output_error: Optional[str] = None


@dataclass
class StreamState:
    """Internal state for tracking streaming message construction."""
    message_id: str = ""
    role: Role = "assistant"
    metadata: Optional[Any] = None
    
    # Current text part being streamed
    current_text_content: str = ""
    text_active: bool = False
    
    # Current reasoning part being streamed
    current_reasoning_content: str = ""
    reasoning_active: bool = False
    
    # Tool calls tracking
    tool_calls: Dict[str, ToolCall] = field(default_factory=dict)
    
    # All completed parts (text, reasoning, and others)
    completed_parts: List[Any] = field(default_factory=list)
    
    # Error state
    error_text: Optional[str] = None


class UIMessageStreamProcessor:
    """
    Processes UIMessageChunk streams to build complete UIMessage objects.
    
    This class accumulates streaming chunks and maintains state to construct
    the final message once streaming is complete or when requested.
    """
    
    def __init__(self, default_message_id: Optional[str] = None):
        """
        Initialize the stream processor.
        
        Args:
            default_message_id: Optional default message ID to use if not provided in chunks
        """
        self.default_message_id = default_message_id or str(uuid.uuid4())
        self.state = StreamState()
        self.reset()
    
    def reset(self):
        """Reset the processor state for a new message."""
        self.state = StreamState()
        self.state.message_id = self.default_message_id
    
    def _create_tool_ui_part(self, tool_call: ToolCall) -> Union[ToolUIPart, DynamicToolUIPart]:
        """Create appropriate UI part from a completed tool call."""
        if tool_call.dynamic:
            # Determine state and fields based on available data
            if tool_call.output_error:
                tool_state: ToolState = 'output-error'
                error_text = tool_call.output_error
                tool_output = None
            elif tool_call.result is not None:
                tool_state = 'output-available'
                error_text = None
                tool_output = tool_call.result
            else:
                tool_state = 'input-available'
                error_text = None
                tool_output = None
                
            return DynamicToolUIPart(
                toolCallId=tool_call.id or 'unknown',
                toolName=tool_call.name,
                state=tool_state,
                input=tool_call.args,
                output=tool_output,
                errorText=error_text,
                preliminary=tool_call.preliminary
            )
        else:
            result_state: ToolState = 'output-available' if tool_call.result is not None else 'input-available'
            return ToolUIPart(
                toolCallId=tool_call.id or 'unknown',
                toolName=tool_call.name,
                state=result_state,
                args=tool_call.args,
                result=tool_call.result
            )
    
    def process_chunk(self, chunk: UIMessageChunk) -> Optional[UIMessage]:
        """
        Process a single chunk and update internal state.
        
        Args:
            chunk: The UIMessageChunk to process
            
        Returns:
            Complete UIMessage if stream ended, None if still streaming
        """
        if isinstance(chunk, TextStartChunk):
            self._handle_text_start(chunk)
        elif isinstance(chunk, TextDeltaChunk):
            self._handle_text_delta(chunk)
        elif isinstance(chunk, TextEndChunk):
            self._handle_text_end(chunk)
        elif isinstance(chunk, ReasoningStartChunk):
            self._handle_reasoning_start(chunk)
        elif isinstance(chunk, ReasoningDeltaChunk):
            self._handle_reasoning_delta(chunk)
        elif isinstance(chunk, ReasoningEndChunk):
            self._handle_reasoning_end(chunk)
        elif isinstance(chunk, ToolInputStartChunk):
            self._handle_tool_input_start(chunk)
        elif isinstance(chunk, ToolInputDeltaChunk):
            self._handle_tool_input_delta(chunk)
        elif isinstance(chunk, ToolInputAvailableChunk):
            self._handle_tool_input_available(chunk)
        elif isinstance(chunk, ToolInputErrorChunk):
            self._handle_tool_input_error(chunk)
        elif isinstance(chunk, ToolOutputAvailableChunk):
            self._handle_tool_output_available(chunk)
        elif isinstance(chunk, ToolOutputErrorChunk):
            self._handle_tool_output_error(chunk)
        elif isinstance(chunk, SourceUrlChunk):
            self._handle_source_url(chunk)
        elif isinstance(chunk, SourceDocumentChunk):
            self._handle_source_document(chunk)
        elif isinstance(chunk, FileChunk):
            self._handle_file(chunk)
        elif isinstance(chunk, StepStartChunk):
            self._handle_step_start(chunk)
        elif isinstance(chunk, StepFinishChunk):
            self._handle_step_finish(chunk)
        elif isinstance(chunk, MessageMetadataChunk):
            self._handle_message_metadata(chunk)
        elif isinstance(chunk, DataChunk):
            self._handle_data(chunk)
        elif isinstance(chunk, ErrorChunk):
            self._handle_error(chunk)
        elif isinstance(chunk, StartChunk):
            self._handle_start(chunk)
        elif isinstance(chunk, FinishChunk):
            self._handle_finish(chunk)
        elif isinstance(chunk, AbortChunk):
            self._handle_abort(chunk)
        
        return None  # Return None while streaming, use build_message() to get final result
    
    def process_stream(self, chunks: Iterator[UIMessageChunk]) -> UIMessage:
        """
        Process an entire stream of chunks and return the final message.
        
        Args:
            chunks: Iterator of UIMessageChunk objects
            
        Returns:
            Complete UIMessage built from all chunks
        """
        for chunk in chunks:
            self.process_chunk(chunk)
        return self.build_message()
    
    def build_message(self) -> UIMessage:
        """
        Build the final UIMessage from accumulated state.
        
        Returns:
            Complete UIMessage object
        """
        parts = []
        
        # Add any currently active text content
        if self.state.current_text_content and self.state.text_active:
            parts.append(TextUIPart(text=self.state.current_text_content, state='streaming'))
        
        # Add any currently active reasoning content
        if self.state.current_reasoning_content and self.state.reasoning_active:
            parts.append(ReasoningUIPart(text=self.state.current_reasoning_content, state='streaming'))
        
        # Add all completed parts (including completed text/reasoning parts and tools)
        parts.extend(self.state.completed_parts)
        
        # Handle error case
        if self.state.error_text:
            # Add error as text part for now
            parts.append(TextUIPart(text=f"Error: {self.state.error_text}"))
        
        return UIMessage(
            id=self.state.message_id,
            role=self.state.role,
            parts=parts,
            metadata=self.state.metadata
        )
    
    # Internal chunk handlers
    
    def _handle_text_start(self, chunk: TextStartChunk):
        """Handle text start chunk."""
        self.state.text_active = True
        self.state.current_text_content = ""
    
    def _handle_text_delta(self, chunk: TextDeltaChunk):
        """Handle text delta chunk."""
        self.state.current_text_content += chunk.delta
    
    def _handle_text_end(self, chunk: TextEndChunk):
        """Handle text end chunk."""
        self.state.text_active = False
        # Add completed text part if there's content
        if self.state.current_text_content:
            self.state.completed_parts.append(TextUIPart(text=self.state.current_text_content, state='done'))
            self.state.current_text_content = ""
    
    def _handle_reasoning_start(self, chunk: ReasoningStartChunk):
        """Handle reasoning start chunk."""
        self.state.reasoning_active = True
        self.state.current_reasoning_content = ""
    
    def _handle_reasoning_delta(self, chunk: ReasoningDeltaChunk):
        """Handle reasoning delta chunk."""
        self.state.current_reasoning_content += chunk.delta
    
    def _handle_reasoning_end(self, chunk: ReasoningEndChunk):
        """Handle reasoning end chunk."""
        self.state.reasoning_active = False
        # Add completed reasoning part if there's content
        if self.state.current_reasoning_content:
            self.state.completed_parts.append(ReasoningUIPart(text=self.state.current_reasoning_content, state='done'))
            self.state.current_reasoning_content = ""
    
    def _handle_tool_input_start(self, chunk: ToolInputStartChunk):
        """Handle tool input start chunk."""
        self.state.tool_calls[chunk.toolCallId] = ToolCall(
            id=chunk.toolCallId,
            name=chunk.toolName,
            dynamic=chunk.dynamic or False,
            input_text=''
        )
    
    def _handle_tool_input_delta(self, chunk: ToolInputDeltaChunk):
        """Handle tool input delta chunk."""
        if chunk.toolCallId in self.state.tool_calls:
            self.state.tool_calls[chunk.toolCallId].input_text += chunk.inputTextDelta
    
    def _handle_tool_input_available(self, chunk: ToolInputAvailableChunk):
        """Handle tool input available chunk."""
        if chunk.toolCallId not in self.state.tool_calls:
            self.state.tool_calls[chunk.toolCallId] = ToolCall()
        
        tool_call = self.state.tool_calls[chunk.toolCallId]
        tool_call.id = chunk.toolCallId
        tool_call.name = chunk.toolName
        tool_call.args = chunk.input
        tool_call.dynamic = chunk.dynamic or False
        tool_call.provider_executed = chunk.providerExecuted
    
    def _handle_tool_input_error(self, chunk: ToolInputErrorChunk):
        """Handle tool input error chunk."""
        if chunk.toolCallId in self.state.tool_calls:
            tool_call = self.state.tool_calls[chunk.toolCallId]
            tool_call.input_error = chunk.errorText
            # Tool is complete when input error occurs - add to completed parts
            if tool_call.name and tool_call.args is not None:
                self.state.completed_parts.append(self._create_tool_ui_part(tool_call))
    
    def _handle_tool_output_available(self, chunk: ToolOutputAvailableChunk):
        """Handle tool output available chunk."""
        if chunk.toolCallId in self.state.tool_calls:
            tool_call = self.state.tool_calls[chunk.toolCallId]
            tool_call.result = chunk.output
            tool_call.preliminary = chunk.preliminary
            # Tool is complete when output is available - add to completed parts
            if tool_call.name and tool_call.args is not None:
                self.state.completed_parts.append(self._create_tool_ui_part(tool_call))
    
    def _handle_tool_output_error(self, chunk: ToolOutputErrorChunk):
        """Handle tool output error chunk."""
        if chunk.toolCallId in self.state.tool_calls:
            tool_call = self.state.tool_calls[chunk.toolCallId]
            tool_call.output_error = chunk.errorText
            # Tool is complete when output error occurs - add to completed parts
            if tool_call.name and tool_call.args is not None:
                self.state.completed_parts.append(self._create_tool_ui_part(tool_call))
    
    def _handle_source_url(self, chunk: SourceUrlChunk):
        """Handle source URL chunk."""
        self.state.completed_parts.append(SourceUrlUIPart(
            sourceId=f"source-{len(self.state.completed_parts)}",
            url=chunk.url,
            title=chunk.title
        ))
    
    def _handle_source_document(self, chunk: SourceDocumentChunk):
        """Handle source document chunk."""
        self.state.completed_parts.append(SourceDocumentUIPart(
            sourceId=chunk.documentId,
            title=chunk.title,
            content=chunk.content
        ))
    
    def _handle_file(self, chunk: FileChunk):
        """Handle file chunk."""
        self.state.completed_parts.append(FileUIPart(
            mediaType=chunk.contentType,
            filename=chunk.filename,
            url=f"data:{chunk.contentType};base64,{chunk.data.hex()}"
        ))
    
    def _handle_step_start(self, chunk: StepStartChunk):
        """Handle step start chunk."""
        self.state.completed_parts.append(StepStartUIPart())
    
    def _handle_step_finish(self, chunk: StepFinishChunk):
        """Handle step finish chunk - for now just track it."""
        pass  # Could track step completion state if needed
    
    def _handle_message_metadata(self, chunk: MessageMetadataChunk):
        """Handle message metadata chunk."""
        self.state.metadata = chunk.metadata
    
    def _handle_data(self, chunk: DataChunk):
        """Handle data chunk."""
        self.state.completed_parts.append(DataUIPart(data=chunk.data))
    
    def _handle_error(self, chunk: ErrorChunk):
        """Handle error chunk."""
        self.state.error_text = chunk.errorText
    
    def _handle_start(self, chunk: StartChunk):
        """Handle start chunk - marks beginning of generation."""
        if chunk.messageId:
            self.state.message_id = chunk.messageId
        if chunk.messageMetadata:
            self.state.metadata = chunk.messageMetadata
    
    def _handle_finish(self, chunk: FinishChunk):
        """Handle finish chunk - marks completion of generation."""
        pass  # Could be used to finalize message
    
    def _handle_abort(self, chunk: AbortChunk):
        """Handle abort chunk - marks aborted generation."""
        self.state.error_text = "Generation was aborted"


class StreamBuffer:
    """
    Buffer for collecting chunks before processing.
    
    Useful for batching chunks or implementing backpressure.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize buffer.
        
        Args:
            max_size: Maximum number of chunks to buffer
        """
        self.max_size = max_size
        self.chunks: List[UIMessageChunk] = []
    
    def add_chunk(self, chunk: UIMessageChunk) -> bool:
        """
        Add a chunk to the buffer.
        
        Args:
            chunk: Chunk to add
            
        Returns:
            True if added successfully, False if buffer is full
        """
        if len(self.chunks) >= self.max_size:
            return False
        self.chunks.append(chunk)
        return True
    
    def get_chunks(self) -> List[UIMessageChunk]:
        """Get all buffered chunks and clear the buffer."""
        buffered_chunks = self.chunks.copy()
        self.chunks.clear()
        return buffered_chunks
    
    def process_with(self, processor: UIMessageStreamProcessor) -> UIMessage:
        """
        Process all buffered chunks with the given processor.
        
        Args:
            processor: The processor to use
            
        Returns:
            UIMessage built from buffered chunks
        """
        for chunk in self.chunks:
            processor.process_chunk(chunk)
        return processor.build_message()


# Utility functions

def process_chunk_stream(
    chunks: Iterator[UIMessageChunk],
    message_id: Optional[str] = None
) -> UIMessage:
    """
    Convenience function to process a stream of chunks into a UIMessage.
    
    Args:
        chunks: Iterator of UIMessageChunk objects
        message_id: Optional message ID to use
        
    Returns:
        Complete UIMessage built from the chunk stream
        
    Example:
        >>> message_chunks = [
        ...     TextStartChunk(id="msg-1"),
        ...     TextDeltaChunk(delta="Hello "),
        ...     TextDeltaChunk(delta="world!"),
        ...     TextEndChunk()
        ... ]
        >>> message = process_chunk_stream(iter(message_chunks))
        >>> print(message.parts[0].text)  # "Hello world!"
    """
    processor = UIMessageStreamProcessor(message_id)
    return processor.process_stream(chunks)


def create_streaming_processor(message_id: Optional[str] = None) -> UIMessageStreamProcessor:
    """
    Create a new streaming processor instance.
    
    Args:
        message_id: Optional default message ID
        
    Returns:
        New UIMessageStreamProcessor instance
        
    Example:
        >>> processor = create_streaming_processor("msg-123")
        >>> processor.process_chunk(TextStartChunk())
        >>> processor.process_chunk(TextDeltaChunk(delta="Hello"))
        >>> message = processor.build_message()
    """
    return UIMessageStreamProcessor(message_id)