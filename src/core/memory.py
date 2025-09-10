"""
Unified Memory System.

This module provides a unified memory system for agents, combining
conversation memory, context management, and knowledge storage.
"""

import json
import tiktoken
from typing import Any, Dict, List, Optional, Union, Iterator
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, validator

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    FUNCTION = "function"


class MessageType(str, Enum):
    """Message types for different content formats."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    DATA = "data"
    CODE = "code"
    JSON = "json"
    XML = "xml"


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role.value,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            message_type=MessageType(data.get("message_type", "text")),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            tool_calls=data.get("tool_calls"),
            tool_call_id=data.get("tool_call_id")
        )


class MemoryChunk(BaseModel):
    """Represents a chunk of memory with metadata."""
    id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk content")
    chunk_type: str = Field(default="conversation", description="Type of chunk")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")
    timestamp: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return self.model_dump()


class UnifiedMemory(BaseModel):
    """
    Unified memory system for agents.
    
    This class provides a comprehensive memory system that combines
    conversation memory, context management, and knowledge storage.
    """
    
    # Core memory storage
    messages: List[Message] = Field(default_factory=list, description="Conversation messages")
    chunks: List[MemoryChunk] = Field(default_factory=list, description="Memory chunks")
    
    # Configuration
    max_messages: int = Field(default=1000, description="Maximum number of messages")
    max_chunks: int = Field(default=10000, description="Maximum number of chunks")
    max_context_tokens: int = Field(default=4000, description="Maximum context tokens")
    
    # Token counting
    token_encoder: Optional[tiktoken.Encoding] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize unified memory."""
        super().__init__(**data)
        
        # Initialize token encoder
        try:
            self.token_encoder = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Failed to initialize token encoder: {e}")
            self.token_encoder = None
    
    def add_message(
        self,
        role: Union[MessageRole, str],
        content: str,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None
    ) -> None:
        """
        Add a message to the conversation.
        
        Args:
            role: Message role
            content: Message content
            message_type: Type of message content
            metadata: Additional metadata
            tool_calls: Tool calls associated with message
            tool_call_id: Tool call ID for tool responses
        """
        # Convert string role to enum
        if isinstance(role, str):
            role = MessageRole(role)
        
        message = Message(
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
            tool_calls=tool_calls,
            tool_call_id=tool_call_id
        )
        
        self.messages.append(message)
        
        # Trim messages if necessary
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        logger.debug(f"Added {role.value} message: {content[:100]}...")
    
    def add_chunk(
        self,
        content: str,
        chunk_type: str = "conversation",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Add a memory chunk.
        
        Args:
            content: Chunk content
            chunk_type: Type of chunk
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            tags: Tags for categorization
            
        Returns:
            Chunk ID
        """
        chunk_id = f"chunk_{len(self.chunks)}_{datetime.now().timestamp()}"
        
        chunk = MemoryChunk(
            id=chunk_id,
            content=content,
            chunk_type=chunk_type,
            importance=importance,
            metadata=metadata or {},
            tags=tags or []
        )
        
        self.chunks.append(chunk)
        
        # Trim chunks if necessary
        if len(self.chunks) > self.max_chunks:
            # Remove least important chunks
            self.chunks.sort(key=lambda x: x.importance, reverse=True)
            self.chunks = self.chunks[:self.max_chunks]
        
        logger.debug(f"Added memory chunk: {chunk_id}")
        return chunk_id
    
    def get_messages(
        self,
        role: Optional[Union[MessageRole, str]] = None,
        limit: Optional[int] = None,
        include_metadata: bool = False
    ) -> List[Union[Message, Dict[str, Any]]]:
        """
        Get messages from memory.
        
        Args:
            role: Filter by role
            limit: Maximum number of messages
            include_metadata: Whether to include metadata
            
        Returns:
            List of messages
        """
        messages = self.messages
        
        # Filter by role
        if role:
            if isinstance(role, str):
                role = MessageRole(role)
            messages = [msg for msg in messages if msg.role == role]
        
        # Apply limit
        if limit:
            messages = messages[-limit:]
        
        # Convert to dict if metadata not needed
        if not include_metadata:
            return [msg.to_dict() for msg in messages]
        
        return messages
    
    def get_context(
        self,
        max_tokens: Optional[int] = None,
        include_system: bool = True,
        include_tools: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get context for LLM with token limit.
        
        Args:
            max_tokens: Maximum tokens (uses max_context_tokens if None)
            include_system: Whether to include system messages
            include_tools: Whether to include tool messages
            
        Returns:
            List of messages for context
        """
        if max_tokens is None:
            max_tokens = self.max_context_tokens
        
        context = []
        current_tokens = 0
        
        # Start from most recent messages
        for message in reversed(self.messages):
            # Skip system messages if not requested
            if not include_system and message.role == MessageRole.SYSTEM:
                continue
            
            # Skip tool messages if not requested
            if not include_tools and message.role == MessageRole.TOOL:
                continue
            
            # Count tokens
            message_tokens = self._count_tokens(message.content)
            
            # Check if adding this message would exceed limit
            if current_tokens + message_tokens > max_tokens:
                break
            
            context.insert(0, message.to_dict())
            current_tokens += message_tokens
        
        logger.debug(f"Generated context with {len(context)} messages, {current_tokens} tokens")
        return context
    
    def search_chunks(
        self,
        query: str,
        chunk_type: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 10
    ) -> List[MemoryChunk]:
        """
        Search memory chunks.
        
        Args:
            query: Search query
            chunk_type: Filter by chunk type
            min_importance: Minimum importance score
            limit: Maximum number of results
            
        Returns:
            List of matching chunks
        """
        results = []
        
        for chunk in self.chunks:
            # Filter by type
            if chunk_type and chunk.chunk_type != chunk_type:
                continue
            
            # Filter by importance
            if chunk.importance < min_importance:
                continue
            
            # Simple text search (could be enhanced with embeddings)
            if query.lower() in chunk.content.lower():
                results.append(chunk)
        
        # Sort by importance and timestamp
        results.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        
        return results[:limit]
    
    def get_chunks_by_tags(self, tags: List[str], limit: int = 10) -> List[MemoryChunk]:
        """
        Get chunks by tags.
        
        Args:
            tags: List of tags to match
            limit: Maximum number of results
            
        Returns:
            List of matching chunks
        """
        results = []
        
        for chunk in self.chunks:
            if any(tag in chunk.tags for tag in tags):
                results.append(chunk)
        
        # Sort by importance and timestamp
        results.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        
        return results[:limit]
    
    def update_chunk_importance(self, chunk_id: str, importance: float) -> bool:
        """
        Update chunk importance.
        
        Args:
            chunk_id: Chunk ID
            importance: New importance score
            
        Returns:
            True if updated, False if chunk not found
        """
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                chunk.importance = max(0.0, min(1.0, importance))
                logger.debug(f"Updated chunk {chunk_id} importance to {importance}")
                return True
        
        logger.warning(f"Chunk {chunk_id} not found for importance update")
        return False
    
    def remove_chunk(self, chunk_id: str) -> bool:
        """
        Remove a chunk.
        
        Args:
            chunk_id: Chunk ID to remove
            
        Returns:
            True if removed, False if chunk not found
        """
        for i, chunk in enumerate(self.chunks):
            if chunk.id == chunk_id:
                del self.chunks[i]
                logger.debug(f"Removed chunk {chunk_id}")
                return True
        
        logger.warning(f"Chunk {chunk_id} not found for removal")
        return False
    
    def clear(self) -> None:
        """Clear all memory."""
        self.messages.clear()
        self.chunks.clear()
        logger.info("Memory cleared")
    
    def clear_messages(self) -> None:
        """Clear conversation messages."""
        self.messages.clear()
        logger.info("Messages cleared")
    
    def clear_chunks(self) -> None:
        """Clear memory chunks."""
        self.chunks.clear()
        logger.info("Chunks cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        total_tokens = sum(self._count_tokens(msg.content) for msg in self.messages)
        
        return {
            "message_count": len(self.messages),
            "chunk_count": len(self.chunks),
            "total_tokens": total_tokens,
            "max_messages": self.max_messages,
            "max_chunks": self.max_chunks,
            "max_context_tokens": self.max_context_tokens,
            "memory_usage": {
                "messages": len(self.messages) / self.max_messages,
                "chunks": len(self.chunks) / self.max_chunks,
                "tokens": total_tokens / self.max_context_tokens
            }
        }
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not self.token_encoder:
            # Fallback: rough estimation
            return len(text.split()) * 1.3
        
        try:
            return len(self.token_encoder.encode(text))
        except Exception:
            # Fallback: rough estimation
            return len(text.split()) * 1.3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "config": {
                "max_messages": self.max_messages,
                "max_chunks": self.max_chunks,
                "max_context_tokens": self.max_context_tokens
            }
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save memory to file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Memory saved to {file_path}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "UnifiedMemory":
        """Load memory from file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        memory = cls()
        
        # Load messages
        for msg_data in data.get("messages", []):
            message = Message.from_dict(msg_data)
            memory.messages.append(message)
        
        # Load chunks
        for chunk_data in data.get("chunks", []):
            chunk = MemoryChunk(**chunk_data)
            memory.chunks.append(chunk)
        
        # Load config
        config = data.get("config", {})
        memory.max_messages = config.get("max_messages", 1000)
        memory.max_chunks = config.get("max_chunks", 10000)
        memory.max_context_tokens = config.get("max_context_tokens", 4000)
        
        logger.info(f"Memory loaded from {file_path}")
        return memory
    
    def __len__(self) -> int:
        """Return total number of items in memory."""
        return len(self.messages) + len(self.chunks)
    
    def __str__(self) -> str:
        """String representation of memory."""
        return f"UnifiedMemory(messages={len(self.messages)}, chunks={len(self.chunks)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of memory."""
        stats = self.get_stats()
        return (
            f"UnifiedMemory(messages={stats['message_count']}, "
            f"chunks={stats['chunk_count']}, "
            f"tokens={stats['total_tokens']})"
        )