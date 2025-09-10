"""
Unified Agent Base Class.

This module provides the base UnifiedAgent class that serves as the foundation
for all agent types in the integrated framework.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from datetime import datetime
from pathlib import Path

from .config import UnifiedConfig
from .tool_registry import ToolRegistry, BaseTool
from .environment import EnvironmentManager
from .memory import UnifiedMemory
from .state import AgentState
from ..utils.exceptions import AgentError, ToolError, ConfigError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UnifiedAgent(ABC):
    """
    Base class for all agents in the unified framework.
    
    This class provides the common interface and functionality that all
    agent types must implement, including tool usage, memory management,
    state tracking, and execution control.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: UnifiedConfig,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[UnifiedMemory] = None,
        state: Optional[AgentState] = None
    ):
        """
        Initialize the unified agent.
        
        Args:
            name: Agent name
            description: Agent description
            config: Agent configuration
            tools: List of available tools
            memory: Memory system instance
            state: Agent state instance
        """
        self.name = name
        self.description = description
        self.config = config
        self.tools = tools or []
        self.memory = memory or UnifiedMemory()
        self.state = state or AgentState()
        
        # Initialize components
        self.tool_registry = ToolRegistry()
        self.environment_manager = EnvironmentManager()
        
        # Agent lifecycle
        self.initialized = False
        self.running = False
        self.created_at = datetime.now()
        self.last_executed = None
        
        # Execution tracking
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        
        logger.info(f"UnifiedAgent '{name}' initialized")
    
    async def setup(self) -> None:
        """Setup the agent for execution."""
        try:
            logger.info(f"Setting up agent '{self.name}'...")
            
            # Register tools
            await self._register_tools()
            
            # Setup environment
            await self._setup_environment()
            
            # Initialize memory
            await self.memory.initialize()
            
            # Setup agent-specific components
            await self._setup_agent_specific()
            
            self.initialized = True
            logger.info(f"Agent '{self.name}' setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup agent '{self.name}': {e}")
            raise AgentError(f"Agent setup failed: {e}") from e
    
    async def _register_tools(self) -> None:
        """Register tools with the tool registry."""
        for tool in self.tools:
            self.tool_registry.register_tool(tool)
        
        logger.info(f"Registered {len(self.tools)} tools for agent '{self.name}'")
    
    async def _setup_environment(self) -> None:
        """Setup execution environment."""
        # Create default environment if none exists
        if not self.environment_manager.environments:
            await self.environment_manager.create_default_environment()
        
        logger.info(f"Environment setup completed for agent '{self.name}'")
    
    @abstractmethod
    async def _setup_agent_specific(self) -> None:
        """Setup agent-specific components. Must be implemented by subclasses."""
        pass
    
    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Run the agent with a given task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Execution result
        """
        if not self.initialized:
            raise AgentError("Agent not initialized. Call setup() first.")
        
        start_time = datetime.now()
        self.running = True
        self.execution_count += 1
        
        try:
            logger.info(f"Agent '{self.name}' executing task: {task}")
            
            # Update state
            self.state.update_state("executing", {"task": task, "start_time": start_time})
            
            # Execute the task
            result = await self._execute_task(task, **kwargs)
            
            # Update execution tracking
            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_execution_time += execution_time
            self.last_executed = datetime.now()
            
            # Update state
            self.state.update_state("completed", {
                "task": task,
                "result": result,
                "execution_time": execution_time
            })
            
            # Store in memory
            await self.memory.store_execution(task, result, execution_time)
            
            logger.info(f"Agent '{self.name}' completed task in {execution_time:.2f}s")
            
            return {
                "agent": self.name,
                "task": task,
                "result": result,
                "execution_time": execution_time,
                "timestamp": self.last_executed.isoformat(),
                "success": True
            }
            
        except Exception as e:
            self.error_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update state
            self.state.update_state("error", {
                "task": task,
                "error": str(e),
                "execution_time": execution_time
            })
            
            logger.error(f"Agent '{self.name}' failed to execute task: {e}")
            
            return {
                "agent": self.name,
                "task": task,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
            
        finally:
            self.running = False
    
    @abstractmethod
    async def _execute_task(self, task: str, **kwargs) -> Any:
        """Execute the specific task. Must be implemented by subclasses."""
        pass
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool by name.
        
        Args:
            tool_name: Name of the tool to use
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                raise ToolError(f"Tool '{tool_name}' not found")
            
            logger.info(f"Agent '{self.name}' using tool '{tool_name}'")
            
            # Execute tool
            result = await tool.execute(**kwargs)
            
            # Store tool usage in memory
            await self.memory.store_tool_usage(tool_name, kwargs, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to use tool '{tool_name}': {e}")
            raise ToolError(f"Tool execution failed: {e}") from e
    
    async def get_memory(self, key: Optional[str] = None) -> Any:
        """
        Get memory content.
        
        Args:
            key: Specific memory key to retrieve
            
        Returns:
            Memory content
        """
        return await self.memory.get(key)
    
    async def store_memory(self, key: str, value: Any) -> None:
        """
        Store content in memory.
        
        Args:
            key: Memory key
            value: Value to store
        """
        await self.memory.store(key, value)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return self.state.get_state()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics."""
        avg_execution_time = (
            self.total_execution_time / self.execution_count
            if self.execution_count > 0 else 0
        )
        
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_execution_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.execution_count if self.execution_count > 0 else 0,
            "tools_count": len(self.tools),
            "initialized": self.initialized,
            "running": self.running
        }
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        try:
            logger.info(f"Cleaning up agent '{self.name}'...")
            
            # Cleanup memory
            await self.memory.cleanup()
            
            # Cleanup environment
            await self.environment_manager.cleanup_all()
            
            # Cleanup agent-specific resources
            await self._cleanup_agent_specific()
            
            self.initialized = False
            logger.info(f"Agent '{self.name}' cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup agent '{self.name}': {e}")
            raise AgentError(f"Agent cleanup failed: {e}") from e
    
    @abstractmethod
    async def _cleanup_agent_specific(self) -> None:
        """Cleanup agent-specific resources. Must be implemented by subclasses."""
        pass
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"UnifiedAgent(name='{self.name}', type='{self.__class__.__name__}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"UnifiedAgent(name='{self.name}', type='{self.__class__.__name__}', "
            f"tools={len(self.tools)}, initialized={self.initialized})"
        )