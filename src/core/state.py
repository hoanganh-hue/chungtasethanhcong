"""
Agent State Management.

This module provides state management for agents, including state definitions,
transitions, and validation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AgentState(str, Enum):
    """Agent execution states."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class StateTransition(BaseModel):
    """Represents a state transition."""
    from_state: AgentState = Field(..., description="Source state")
    to_state: AgentState = Field(..., description="Target state")
    timestamp: datetime = Field(default_factory=datetime.now, description="Transition timestamp")
    reason: Optional[str] = Field(None, description="Reason for transition")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StateManager:
    """Manages agent state transitions and validation."""
    
    # Valid state transitions
    VALID_TRANSITIONS: Dict[AgentState, List[AgentState]] = {
        AgentState.IDLE: [
            AgentState.INITIALIZING,
            AgentState.ERROR
        ],
        AgentState.INITIALIZING: [
            AgentState.READY,
            AgentState.ERROR
        ],
        AgentState.READY: [
            AgentState.RUNNING,
            AgentState.ERROR
        ],
        AgentState.RUNNING: [
            AgentState.PAUSED,
            AgentState.COMPLETED,
            AgentState.ERROR,
            AgentState.CANCELLED
        ],
        AgentState.PAUSED: [
            AgentState.RUNNING,
            AgentState.CANCELLED,
            AgentState.ERROR
        ],
        AgentState.COMPLETED: [
            AgentState.IDLE,
            AgentState.ERROR
        ],
        AgentState.ERROR: [
            AgentState.IDLE,
            AgentState.READY
        ],
        AgentState.CANCELLED: [
            AgentState.IDLE,
            AgentState.ERROR
        ]
    }
    
    def __init__(self, initial_state: AgentState = AgentState.IDLE):
        """Initialize state manager."""
        self.current_state = initial_state
        self.transition_history: List[StateTransition] = []
        self.state_metadata: Dict[AgentState, Dict[str, Any]] = {}
        
        logger.debug(f"StateManager initialized with state: {initial_state}")
    
    def can_transition_to(self, target_state: AgentState) -> bool:
        """Check if transition to target state is valid."""
        valid_targets = self.VALID_TRANSITIONS.get(self.current_state, [])
        return target_state in valid_targets
    
    def transition_to(
        self, 
        target_state: AgentState, 
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Transition to target state.
        
        Args:
            target_state: Target state
            reason: Reason for transition
            metadata: Additional metadata
            
        Returns:
            True if transition was successful, False otherwise
        """
        if not self.can_transition_to(target_state):
            logger.warning(
                f"Invalid state transition from {self.current_state} to {target_state}"
            )
            return False
        
        # Create transition record
        transition = StateTransition(
            from_state=self.current_state,
            to_state=target_state,
            reason=reason,
            metadata=metadata or {}
        )
        
        # Update state
        previous_state = self.current_state
        self.current_state = target_state
        
        # Record transition
        self.transition_history.append(transition)
        
        # Store metadata
        if metadata:
            self.state_metadata[target_state] = metadata
        
        logger.info(
            f"State transition: {previous_state} -> {target_state} "
            f"(reason: {reason or 'N/A'})"
        )
        
        return True
    
    def force_transition_to(
        self, 
        target_state: AgentState, 
        reason: str = "Force transition",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Force transition to target state (bypasses validation).
        
        Args:
            target_state: Target state
            reason: Reason for forced transition
            metadata: Additional metadata
        """
        transition = StateTransition(
            from_state=self.current_state,
            to_state=target_state,
            reason=f"FORCED: {reason}",
            metadata=metadata or {}
        )
        
        previous_state = self.current_state
        self.current_state = target_state
        self.transition_history.append(transition)
        
        if metadata:
            self.state_metadata[target_state] = metadata
        
        logger.warning(
            f"FORCED state transition: {previous_state} -> {target_state} "
            f"(reason: {reason})"
        )
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information."""
        return {
            "current_state": self.current_state,
            "transition_count": len(self.transition_history),
            "last_transition": self.transition_history[-1] if self.transition_history else None,
            "state_metadata": self.state_metadata.get(self.current_state, {}),
            "valid_transitions": self.VALID_TRANSITIONS.get(self.current_state, [])
        }
    
    def get_transition_history(self) -> List[StateTransition]:
        """Get complete transition history."""
        return self.transition_history.copy()
    
    def reset(self, initial_state: AgentState = AgentState.IDLE) -> None:
        """Reset state manager to initial state."""
        self.current_state = initial_state
        self.transition_history.clear()
        self.state_metadata.clear()
        
        logger.info(f"StateManager reset to: {initial_state}")
    
    def is_running(self) -> bool:
        """Check if agent is in running state."""
        return self.current_state == AgentState.RUNNING
    
    def is_ready(self) -> bool:
        """Check if agent is ready for execution."""
        return self.current_state == AgentState.READY
    
    def is_error(self) -> bool:
        """Check if agent is in error state."""
        return self.current_state == AgentState.ERROR
    
    def is_completed(self) -> bool:
        """Check if agent execution is completed."""
        return self.current_state == AgentState.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if agent execution is cancelled."""
        return self.current_state == AgentState.CANCELLED
    
    def can_execute(self) -> bool:
        """Check if agent can execute (is ready)."""
        return self.current_state == AgentState.READY
    
    def can_pause(self) -> bool:
        """Check if agent can be paused."""
        return self.current_state == AgentState.RUNNING
    
    def can_resume(self) -> bool:
        """Check if agent can be resumed."""
        return self.current_state == AgentState.PAUSED
    
    def can_cancel(self) -> bool:
        """Check if agent can be cancelled."""
        return self.current_state in [AgentState.RUNNING, AgentState.PAUSED]
    
    def get_state_duration(self) -> Optional[float]:
        """Get duration in current state (in seconds)."""
        if not self.transition_history:
            return None
        
        last_transition = self.transition_history[-1]
        duration = (datetime.now() - last_transition.timestamp).total_seconds()
        return duration
    
    def get_total_execution_time(self) -> Optional[float]:
        """Get total execution time across all running states."""
        if not self.transition_history:
            return None
        
        total_time = 0.0
        running_start = None
        
        for transition in self.transition_history:
            if transition.to_state == AgentState.RUNNING:
                running_start = transition.timestamp
            elif running_start and transition.from_state == AgentState.RUNNING:
                total_time += (transition.timestamp - running_start).total_seconds()
                running_start = None
        
        # If currently running, add current duration
        if running_start and self.current_state == AgentState.RUNNING:
            total_time += (datetime.now() - running_start).total_seconds()
        
        return total_time
    
    def __str__(self) -> str:
        """String representation of state manager."""
        return f"StateManager(state={self.current_state}, transitions={len(self.transition_history)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of state manager."""
        return (
            f"StateManager(state={self.current_state}, "
            f"transitions={len(self.transition_history)}, "
            f"duration={self.get_state_duration():.2f}s)"
        )