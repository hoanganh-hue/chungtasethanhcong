"""
Agent Memory System for OpenManus-Youtu Integrated Framework
Advanced memory management for agents with persistence and retrieval
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import pickle
import hashlib
from pathlib import Path
import sqlite3
import threading

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Memory types for different information."""
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    EXPERIENCE = "experience"
    CONTEXT = "context"
    PREFERENCE = "preference"
    SKILL = "skill"
    FACT = "fact"
    PROCEDURE = "procedure"

class MemoryPriority(Enum):
    """Memory priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MemoryEntry:
    """Individual memory entry."""
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    memory_type: MemoryType = MemoryType.KNOWLEDGE
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: MemoryPriority = MemoryPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

@dataclass
class MemoryQuery:
    """Memory query for retrieval."""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    query_text: str = ""
    memory_types: List[MemoryType] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    limit: int = 10
    similarity_threshold: float = 0.7
    time_range: Optional[tuple] = None
    priority_filter: Optional[MemoryPriority] = None

class UnifiedMemory:
    """Unified memory system for backward compatibility."""
    
    def __init__(self, agent_id: str, max_memories: int = 10000, persistence_enabled: bool = True):
        self.agent_memory = AgentMemory(agent_id, max_memories, persistence_enabled)
    
    def store_memory(self, memory_type, content, metadata=None, priority=None, tags=None, expires_at=None):
        return self.agent_memory.store_memory(memory_type, content, metadata, priority, tags, expires_at)
    
    def retrieve_memories(self, query):
        return self.agent_memory.retrieve_memories(query)
    
    def search_memories(self, search_text, memory_types=None, limit=10):
        return self.agent_memory.search_memories(search_text, memory_types, limit)
    
    def get_memory_statistics(self):
        return self.agent_memory.get_memory_statistics()

class AgentMemory:
    """Individual agent memory system."""
    
    def __init__(self, agent_id: str, max_memories: int = 10000, persistence_enabled: bool = True):
        self.agent_id = agent_id
        self.max_memories = max_memories
        self.persistence_enabled = persistence_enabled
        self.memories: Dict[str, MemoryEntry] = {}
        self.memory_index: Dict[str, List[str]] = {}  # tag -> memory_ids
        self.type_index: Dict[MemoryType, List[str]] = {}  # type -> memory_ids
        self.lock = threading.RLock()
        
        # Initialize type index
        for memory_type in MemoryType:
            self.type_index[memory_type] = []
        
        # Setup persistence
        if persistence_enabled:
            self.db_path = Path(f"data/memory_{agent_id}.db")
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()
            asyncio.create_task(self._load_from_database())
    
    def _init_database(self) -> None:
        """Initialize SQLite database for memory persistence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        memory_id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        access_count INTEGER NOT NULL,
                        expires_at TEXT,
                        tags TEXT NOT NULL,
                        embedding TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)
                """)
                
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize memory database: {e}")
    
    async def _load_from_database(self) -> None:
        """Load memories from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM memories WHERE agent_id = ?
                """, (self.agent_id,))
                
                for row in cursor.fetchall():
                    memory = MemoryEntry(
                        memory_id=row[0],
                        agent_id=row[1],
                        memory_type=MemoryType(row[2]),
                        content=json.loads(row[3]),
                        metadata=json.loads(row[4]),
                        priority=MemoryPriority(row[5]),
                        created_at=datetime.fromisoformat(row[6]),
                        last_accessed=datetime.fromisoformat(row[7]),
                        access_count=row[8],
                        expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
                        tags=json.loads(row[10]),
                        embedding=json.loads(row[11]) if row[11] else None
                    )
                    
                    with self.lock:
                        self.memories[memory.memory_id] = memory
                        self._update_indexes(memory)
                
                logger.info(f"Loaded {len(self.memories)} memories for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Failed to load memories from database: {e}")
    
    def store_memory(self, memory_type: MemoryType, content: Dict[str, Any], 
                    metadata: Dict[str, Any] = None, priority: MemoryPriority = MemoryPriority.NORMAL,
                    tags: List[str] = None, expires_at: Optional[datetime] = None) -> str:
        """Store a new memory."""
        with self.lock:
            # Check memory limit
            if len(self.memories) >= self.max_memories:
                self._evict_old_memories()
            
            memory = MemoryEntry(
                agent_id=self.agent_id,
                memory_type=memory_type,
                content=content,
                metadata=metadata or {},
                priority=priority,
                tags=tags or [],
                expires_at=expires_at
            )
            
            self.memories[memory.memory_id] = memory
            self._update_indexes(memory)
            
            # Persist to database
            if self.persistence_enabled:
                asyncio.create_task(self._persist_memory(memory))
            
            logger.debug(f"Stored memory: {memory.memory_id}")
            return memory.memory_id
    
    def retrieve_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve memories based on query."""
        with self.lock:
            candidates = []
            
            # Filter by memory types
            if query.memory_types:
                for memory_type in query.memory_types:
                    candidates.extend(self.type_index.get(memory_type, []))
            else:
                candidates = list(self.memories.keys())
            
            # Filter by tags
            if query.tags:
                tag_filtered = []
                for memory_id in candidates:
                    memory = self.memories.get(memory_id)
                    if memory and any(tag in memory.tags for tag in query.tags):
                        tag_filtered.append(memory_id)
                candidates = tag_filtered
            
            # Filter by time range
            if query.time_range:
                time_filtered = []
                start_time, end_time = query.time_range
                for memory_id in candidates:
                    memory = self.memories.get(memory_id)
                    if memory and start_time <= memory.created_at <= end_time:
                        time_filtered.append(memory_id)
                candidates = time_filtered
            
            # Filter by priority
            if query.priority_filter:
                priority_filtered = []
                for memory_id in candidates:
                    memory = self.memories.get(memory_id)
                    if memory and memory.priority.value >= query.priority_filter.value:
                        priority_filtered.append(memory_id)
                candidates = priority_filtered
            
            # Get memory entries and sort by relevance
            memories = [self.memories[memory_id] for memory_id in candidates if memory_id in self.memories]
            
            # Sort by access count and recency
            memories.sort(key=lambda m: (m.access_count, m.last_accessed), reverse=True)
            
            # Update access information
            for memory in memories[:query.limit]:
                memory.last_accessed = datetime.now()
                memory.access_count += 1
            
            return memories[:query.limit]
    
    def search_memories(self, search_text: str, memory_types: List[MemoryType] = None,
                       limit: int = 10) -> List[MemoryEntry]:
        """Search memories by text content."""
        query = MemoryQuery(
            agent_id=self.agent_id,
            query_text=search_text,
            memory_types=memory_types or [],
            limit=limit
        )
        
        memories = self.retrieve_memories(query)
        
        # Simple text matching (can be enhanced with embeddings)
        search_lower = search_text.lower()
        scored_memories = []
        
        for memory in memories:
            score = 0
            content_str = json.dumps(memory.content).lower()
            
            # Count keyword matches
            for word in search_lower.split():
                if word in content_str:
                    score += 1
            
            # Check tags
            for tag in memory.tags:
                if search_lower in tag.lower():
                    score += 2
            
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return [memory for score, memory in scored_memories[:limit]]
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory."""
        with self.lock:
            if memory_id not in self.memories:
                return False
            
            memory = self.memories[memory_id]
            memory.content.update(updates)
            memory.last_accessed = datetime.now()
            
            # Persist changes
            if self.persistence_enabled:
                asyncio.create_task(self._persist_memory(memory))
            
            return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        with self.lock:
            if memory_id not in self.memories:
                return False
            
            memory = self.memories[memory_id]
            
            # Remove from indexes
            self._remove_from_indexes(memory)
            del self.memories[memory_id]
            
            # Remove from database
            if self.persistence_enabled:
                asyncio.create_task(self._delete_from_database(memory_id))
            
            logger.debug(f"Deleted memory: {memory_id}")
            return True
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with self.lock:
            return {
                "total_memories": len(self.memories),
                "memory_types": {
                    memory_type.value: len(memory_ids)
                    for memory_type, memory_ids in self.type_index.items()
                },
                "total_tags": len(self.memory_index),
                "most_accessed": sorted(
                    self.memories.values(),
                    key=lambda m: m.access_count,
                    reverse=True
                )[:5],
                "recent_memories": sorted(
                    self.memories.values(),
                    key=lambda m: m.created_at,
                    reverse=True
                )[:5]
            }
    
    def _update_indexes(self, memory: MemoryEntry) -> None:
        """Update memory indexes."""
        # Update type index
        if memory.memory_id not in self.type_index[memory.memory_type]:
            self.type_index[memory.memory_type].append(memory.memory_id)
        
        # Update tag index
        for tag in memory.tags:
            if tag not in self.memory_index:
                self.memory_index[tag] = []
            if memory.memory_id not in self.memory_index[tag]:
                self.memory_index[tag].append(memory.memory_id)
    
    def _remove_from_indexes(self, memory: MemoryEntry) -> None:
        """Remove memory from indexes."""
        # Remove from type index
        if memory.memory_id in self.type_index[memory.memory_type]:
            self.type_index[memory.memory_type].remove(memory.memory_id)
        
        # Remove from tag index
        for tag in memory.tags:
            if tag in self.memory_index and memory.memory_id in self.memory_index[tag]:
                self.memory_index[tag].remove(memory.memory_id)
    
    def _evict_old_memories(self) -> None:
        """Evict old, less important memories."""
        # Sort by priority, access count, and recency
        memories_to_evict = sorted(
            self.memories.values(),
            key=lambda m: (m.priority.value, m.access_count, m.last_accessed)
        )
        
        # Remove 10% of memories
        evict_count = max(1, len(self.memories) // 10)
        
        for memory in memories_to_evict[:evict_count]:
            self.delete_memory(memory.memory_id)
    
    async def _persist_memory(self, memory: MemoryEntry) -> None:
        """Persist memory to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.memory_id,
                    memory.agent_id,
                    memory.memory_type.value,
                    json.dumps(memory.content),
                    json.dumps(memory.metadata),
                    memory.priority.value,
                    memory.created_at.isoformat(),
                    memory.last_accessed.isoformat(),
                    memory.access_count,
                    memory.expires_at.isoformat() if memory.expires_at else None,
                    json.dumps(memory.tags),
                    json.dumps(memory.embedding) if memory.embedding else None
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist memory: {e}")
    
    async def _delete_from_database(self, memory_id: str) -> None:
        """Delete memory from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to delete memory from database: {e}")

class MemoryManager:
    """Global memory manager for all agents."""
    
    def __init__(self):
        self.agent_memories: Dict[str, AgentMemory] = {}
        self.shared_memories: Dict[str, MemoryEntry] = {}
        self.lock = threading.RLock()
    
    def get_agent_memory(self, agent_id: str) -> AgentMemory:
        """Get or create memory for an agent."""
        with self.lock:
            if agent_id not in self.agent_memories:
                self.agent_memories[agent_id] = AgentMemory(agent_id)
            return self.agent_memories[agent_id]
    
    def store_shared_memory(self, content: Dict[str, Any], memory_type: MemoryType = MemoryType.KNOWLEDGE,
                           tags: List[str] = None) -> str:
        """Store shared memory accessible by all agents."""
        with self.lock:
            memory = MemoryEntry(
                memory_type=memory_type,
                content=content,
                tags=tags or [],
                priority=MemoryPriority.HIGH
            )
            self.shared_memories[memory.memory_id] = memory
            return memory.memory_id
    
    def get_shared_memories(self, tags: List[str] = None, limit: int = 10) -> List[MemoryEntry]:
        """Get shared memories."""
        with self.lock:
            memories = list(self.shared_memories.values())
            
            if tags:
                memories = [m for m in memories if any(tag in m.tags for tag in tags)]
            
            return memories[:limit]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get global memory statistics."""
        with self.lock:
            return {
                "total_agents": len(self.agent_memories),
                "total_shared_memories": len(self.shared_memories),
                "agent_memory_stats": {
                    agent_id: memory.get_memory_statistics()
                    for agent_id, memory in self.agent_memories.items()
                }
            }

# Global memory manager
memory_manager = MemoryManager()

# Convenience functions
def get_agent_memory(agent_id: str) -> AgentMemory:
    """Get agent memory."""
    return memory_manager.get_agent_memory(agent_id)

def store_agent_memory(agent_id: str, memory_type: MemoryType, content: Dict[str, Any],
                      metadata: Dict[str, Any] = None, tags: List[str] = None) -> str:
    """Store memory for an agent."""
    memory = get_agent_memory(agent_id)
    return memory.store_memory(memory_type, content, metadata, tags=tags)

def retrieve_agent_memories(agent_id: str, query: MemoryQuery) -> List[MemoryEntry]:
    """Retrieve memories for an agent."""
    memory = get_agent_memory(agent_id)
    return memory.retrieve_memories(query)

def search_agent_memories(agent_id: str, search_text: str, memory_types: List[MemoryType] = None,
                         limit: int = 10) -> List[MemoryEntry]:
    """Search memories for an agent."""
    memory = get_agent_memory(agent_id)
    return memory.search_memories(search_text, memory_types, limit)