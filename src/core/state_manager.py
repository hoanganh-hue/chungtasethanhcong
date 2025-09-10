"""
Agent State Management System for OpenManus-Youtu Integrated Framework
Advanced state management for agents and workflows
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
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class StateType(Enum):
    """State types for different components."""
    AGENT = "agent"
    WORKFLOW = "workflow"
    SESSION = "session"
    TASK = "task"
    CONVERSATION = "conversation"
    MEMORY = "memory"
    CACHE = "cache"

class StateStatus(Enum):
    """State status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class StateSnapshot:
    """State snapshot for persistence."""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str = ""
    entity_type: StateType = StateType.AGENT
    state_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    version: int = 1

@dataclass
class StateTransition:
    """State transition definition."""
    transition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_state: str = ""
    to_state: str = ""
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """Advanced state management system."""
    
    def __init__(self, persistence_enabled: bool = True, max_memory_states: int = 1000):
        self.persistence_enabled = persistence_enabled
        self.max_memory_states = max_memory_states
        self.states: Dict[str, Dict[str, Any]] = {}
        self.state_history: Dict[str, List[StateSnapshot]] = {}
        self.transitions: Dict[str, List[StateTransition]] = {}
        self.state_listeners: Dict[str, List[Callable]] = {}
        self.lock = threading.RLock()
        self.persistence_path = Path("data/state_persistence")
        self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        # Start cleanup task
        if persistence_enabled:
            asyncio.create_task(self._cleanup_expired_states())
    
    def create_state(self, entity_id: str, entity_type: StateType, 
                    initial_data: Dict[str, Any] = None) -> str:
        """Create a new state for an entity."""
        with self.lock:
            state_id = f"{entity_type.value}_{entity_id}"
            
            if state_id in self.states:
                logger.warning(f"State already exists: {state_id}")
                return state_id
            
            state_data = {
                "entity_id": entity_id,
                "entity_type": entity_type.value,
                "status": StateStatus.ACTIVE.value,
                "data": initial_data or {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": 1
                }
            }
            
            self.states[state_id] = state_data
            self.state_history[state_id] = []
            
            # Create initial snapshot
            snapshot = StateSnapshot(
                entity_id=entity_id,
                entity_type=entity_type,
                state_data=state_data["data"].copy(),
                metadata=state_data["metadata"].copy()
            )
            self.state_history[state_id].append(snapshot)
            
            logger.info(f"Created state: {state_id}")
            return state_id
    
    def get_state(self, entity_id: str, entity_type: StateType) -> Optional[Dict[str, Any]]:
        """Get current state of an entity."""
        state_id = f"{entity_type.value}_{entity_id}"
        with self.lock:
            return self.states.get(state_id)
    
    def update_state(self, entity_id: str, entity_type: StateType, 
                    updates: Dict[str, Any], create_if_missing: bool = True) -> bool:
        """Update state of an entity."""
        state_id = f"{entity_type.value}_{entity_id}"
        
        with self.lock:
            if state_id not in self.states:
                if create_if_missing:
                    self.create_state(entity_id, entity_type)
                else:
                    logger.warning(f"State not found: {state_id}")
                    return False
            
            # Update state data
            current_state = self.states[state_id]
            current_state["data"].update(updates)
            current_state["metadata"]["last_updated"] = datetime.now().isoformat()
            current_state["metadata"]["version"] += 1
            
            # Create snapshot
            snapshot = StateSnapshot(
                entity_id=entity_id,
                entity_type=entity_type,
                state_data=current_state["data"].copy(),
                metadata=current_state["metadata"].copy(),
                version=current_state["metadata"]["version"]
            )
            self.state_history[state_id].append(snapshot)
            
            # Notify listeners
            self._notify_state_change(state_id, current_state)
            
            # Persist if enabled
            if self.persistence_enabled:
                asyncio.create_task(self._persist_state(state_id, current_state))
            
            logger.debug(f"Updated state: {state_id}")
            return True
    
    def set_state_status(self, entity_id: str, entity_type: StateType, 
                        status: StateStatus) -> bool:
        """Set status of a state."""
        state_id = f"{entity_type.value}_{entity_id}"
        
        with self.lock:
            if state_id not in self.states:
                logger.warning(f"State not found: {state_id}")
                return False
            
            self.states[state_id]["status"] = status.value
            self.states[state_id]["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Create snapshot
            snapshot = StateSnapshot(
                entity_id=entity_id,
                entity_type=entity_type,
                state_data=self.states[state_id]["data"].copy(),
                metadata=self.states[state_id]["metadata"].copy()
            )
            self.state_history[state_id].append(snapshot)
            
            self._notify_state_change(state_id, self.states[state_id])
            return True
    
    def delete_state(self, entity_id: str, entity_type: StateType) -> bool:
        """Delete a state."""
        state_id = f"{entity_type.value}_{entity_id}"
        
        with self.lock:
            if state_id in self.states:
                del self.states[state_id]
                if state_id in self.state_history:
                    del self.state_history[state_id]
                
                # Remove persistence file
                if self.persistence_enabled:
                    persistence_file = self.persistence_path / f"{state_id}.json"
                    if persistence_file.exists():
                        persistence_file.unlink()
                
                logger.info(f"Deleted state: {state_id}")
                return True
            
            return False
    
    def get_state_history(self, entity_id: str, entity_type: StateType, 
                         limit: int = 100) -> List[StateSnapshot]:
        """Get state history for an entity."""
        state_id = f"{entity_type.value}_{entity_id}"
        with self.lock:
            history = self.state_history.get(state_id, [])
            return history[-limit:] if limit > 0 else history
    
    def restore_state_from_history(self, entity_id: str, entity_type: StateType, 
                                  snapshot_id: str) -> bool:
        """Restore state from a historical snapshot."""
        state_id = f"{entity_type.value}_{entity_id}"
        
        with self.lock:
            if state_id not in self.state_history:
                return False
            
            # Find snapshot
            snapshot = None
            for snap in self.state_history[state_id]:
                if snap.snapshot_id == snapshot_id:
                    snapshot = snap
                    break
            
            if not snapshot:
                return False
            
            # Restore state
            self.states[state_id] = {
                "entity_id": entity_id,
                "entity_type": entity_type.value,
                "status": StateStatus.ACTIVE.value,
                "data": snapshot.state_data.copy(),
                "metadata": snapshot.metadata.copy()
            }
            
            logger.info(f"Restored state from snapshot: {snapshot_id}")
            return True
    
    def add_state_transition(self, entity_type: StateType, transition: StateTransition) -> None:
        """Add state transition rule."""
        type_key = entity_type.value
        if type_key not in self.transitions:
            self.transitions[type_key] = []
        self.transitions[type_key].append(transition)
    
    def add_state_listener(self, entity_id: str, entity_type: StateType, 
                          listener: Callable) -> None:
        """Add state change listener."""
        state_id = f"{entity_type.value}_{entity_id}"
        if state_id not in self.state_listeners:
            self.state_listeners[state_id] = []
        self.state_listeners[state_id].append(listener)
    
    def _notify_state_change(self, state_id: str, state_data: Dict[str, Any]) -> None:
        """Notify state change listeners."""
        if state_id in self.state_listeners:
            for listener in self.state_listeners[state_id]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        asyncio.create_task(listener(state_data))
                    else:
                        listener(state_data)
                except Exception as e:
                    logger.error(f"State listener error: {e}")
    
    async def _persist_state(self, state_id: str, state_data: Dict[str, Any]) -> None:
        """Persist state to disk."""
        try:
            persistence_file = self.persistence_path / f"{state_id}.json"
            with open(persistence_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to persist state {state_id}: {e}")
    
    async def _load_persisted_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Load persisted state from disk."""
        try:
            persistence_file = self.persistence_path / f"{state_id}.json"
            if persistence_file.exists():
                with open(persistence_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load persisted state {state_id}: {e}")
        return None
    
    async def _cleanup_expired_states(self) -> None:
        """Cleanup expired states."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                with self.lock:
                    current_time = datetime.now()
                    expired_states = []
                    
                    for state_id, state_data in self.states.items():
                        # Check if state has expired
                        if "expires_at" in state_data.get("metadata", {}):
                            expires_at = datetime.fromisoformat(state_data["metadata"]["expires_at"])
                            if current_time > expires_at:
                                expired_states.append(state_id)
                    
                    # Remove expired states
                    for state_id in expired_states:
                        del self.states[state_id]
                        if state_id in self.state_history:
                            del self.state_history[state_id]
                        logger.info(f"Cleaned up expired state: {state_id}")
                
            except Exception as e:
                logger.error(f"State cleanup error: {e}")
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Get state management statistics."""
        with self.lock:
            return {
                "total_states": len(self.states),
                "total_history_entries": sum(len(history) for history in self.state_history.values()),
                "state_types": {
                    state_type.value: len([s for s in self.states.values() if s["entity_type"] == state_type.value])
                    for state_type in StateType
                },
                "state_statuses": {
                    status.value: len([s for s in self.states.values() if s["status"] == status.value])
                    for status in StateStatus
                },
                "persistence_enabled": self.persistence_enabled,
                "listeners_count": sum(len(listeners) for listeners in self.state_listeners.values())
            }

# Global state manager
state_manager = StateManager()

# Convenience functions
def create_agent_state(agent_id: str, initial_data: Dict[str, Any] = None) -> str:
    """Create state for an agent."""
    return state_manager.create_state(agent_id, StateType.AGENT, initial_data)

def get_agent_state(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get agent state."""
    return state_manager.get_state(agent_id, StateType.AGENT)

def update_agent_state(agent_id: str, updates: Dict[str, Any]) -> bool:
    """Update agent state."""
    return state_manager.update_state(agent_id, StateType.AGENT, updates)

def set_agent_status(agent_id: str, status: StateStatus) -> bool:
    """Set agent status."""
    return state_manager.set_state_status(agent_id, StateType.AGENT, status)

def create_workflow_state(workflow_id: str, initial_data: Dict[str, Any] = None) -> str:
    """Create state for a workflow."""
    return state_manager.create_state(workflow_id, StateType.WORKFLOW, initial_data)

def get_workflow_state(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get workflow state."""
    return state_manager.get_state(workflow_id, StateType.WORKFLOW)

def update_workflow_state(workflow_id: str, updates: Dict[str, Any]) -> bool:
    """Update workflow state."""
    return state_manager.update_state(workflow_id, StateType.WORKFLOW, updates)