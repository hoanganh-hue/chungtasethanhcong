"""
Base Tool Implementation.

This module provides the base tool classes and interfaces that all
tools in the unified framework must implement.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from ..utils.exceptions import ToolError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolCategory(Enum):
    """Tool categories for organization and filtering."""
    AUTOMATION = "automation"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    DATA = "data"
    FILE = "file"
    NETWORK = "network"
    RESEARCH = "research"
    SYSTEM = "system"
    UTILITY = "utility"
    WEB = "web"


@dataclass
class ToolMetadata:
    """Metadata for a tool."""
    name: str
    description: str
    category: ToolCategory
    version: str
    author: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    requirements: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.requirements is None:
            self.requirements = {}


@dataclass
class ToolParameter:
    """Parameter definition for a tool."""
    name: str
    type: Type
    description: str
    required: bool = True
    default: Any = None
    choices: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


@dataclass
class ToolDefinition:
    """Complete tool definition."""
    metadata: ToolMetadata
    parameters: Dict[str, ToolParameter]
    return_type: Type
    examples: Optional[List[Dict[str, Any]]] = None
    error_codes: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.error_codes is None:
            self.error_codes = {}


class BaseTool(ABC):
    """
    Base class for all tools in the unified framework.
    
    This class provides the common interface and functionality that all
    tools must implement, including parameter validation, error handling,
    and execution tracking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base tool.
        
        Args:
            config: Tool configuration
        """
        self.config = config or {}
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        self.last_executed = None
        
        # Validate tool implementation
        self._validate_implementation()
        
        logger.info(f"Tool '{self._get_metadata().name}' initialized")
    
    def _validate_implementation(self) -> None:
        """Validate that the tool is properly implemented."""
        try:
            # Check required methods
            if not hasattr(self, '_get_metadata') or not callable(getattr(self, '_get_metadata')):
                raise ToolError("Tool must implement _get_metadata() method")
            
            if not hasattr(self, '_get_definition') or not callable(getattr(self, '_get_definition')):
                raise ToolError("Tool must implement _get_definition() method")
            
            if not hasattr(self, 'execute') or not callable(getattr(self, 'execute')):
                raise ToolError("Tool must implement execute() method")
            
            # Validate metadata
            metadata = self._get_metadata()
            if not isinstance(metadata, ToolMetadata):
                raise ToolError("_get_metadata() must return ToolMetadata instance")
            
            # Validate definition
            definition = self._get_definition()
            if not isinstance(definition, ToolDefinition):
                raise ToolError("_get_definition() must return ToolDefinition instance")
            
        except Exception as e:
            logger.error(f"Tool validation failed: {e}")
            raise ToolError(f"Tool validation failed: {e}") from e
    
    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _get_definition(self) -> ToolDefinition:
        """Get tool definition. Must be implemented by subclasses."""
        pass
    
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        start_time = datetime.now()
        self.execution_count += 1
        
        try:
            logger.info(f"Executing tool '{self._get_metadata().name}'")
            
            # Validate parameters
            self._validate_parameters(kwargs)
            
            # Execute the tool
            result = await self._execute(**kwargs)
            
            # Update execution tracking
            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_execution_time += execution_time
            self.last_executed = datetime.now()
            
            logger.info(f"Tool '{self._get_metadata().name}' executed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"Tool '{self._get_metadata().name}' execution failed: {e}")
            raise ToolError(f"Tool execution failed: {e}") from e
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """Execute the tool implementation. Must be implemented by subclasses."""
        pass
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate tool parameters.
        
        Args:
            parameters: Parameters to validate
            
        Raises:
            ToolError: If validation fails
        """
        try:
            definition = self._get_definition()
            
            # Check required parameters
            for param_name, param_def in definition.parameters.items():
                if param_def.required and param_name not in parameters:
                    raise ToolError(f"Required parameter '{param_name}' is missing")
            
            # Validate parameter types and values
            for param_name, param_value in parameters.items():
                if param_name not in definition.parameters:
                    logger.warning(f"Unknown parameter '{param_name}' for tool '{self._get_metadata().name}'")
                    continue
                
                param_def = definition.parameters[param_name]
                self._validate_parameter(param_name, param_value, param_def)
            
        except Exception as e:
            logger.error(f"Parameter validation failed: {e}")
            raise ToolError(f"Parameter validation failed: {e}") from e
    
    def _validate_parameter(self, name: str, value: Any, param_def: ToolParameter) -> None:
        """
        Validate a single parameter.
        
        Args:
            name: Parameter name
            value: Parameter value
            param_def: Parameter definition
            
        Raises:
            ToolError: If validation fails
        """
        try:
            # Type validation
            if not isinstance(value, param_def.type):
                raise ToolError(f"Parameter '{name}' must be of type {param_def.type.__name__}")
            
            # Value validation
            if param_def.choices and value not in param_def.choices:
                raise ToolError(f"Parameter '{name}' must be one of {param_def.choices}")
            
            # Numeric range validation
            if isinstance(value, (int, float)):
                if param_def.min_value is not None and value < param_def.min_value:
                    raise ToolError(f"Parameter '{name}' must be >= {param_def.min_value}")
                if param_def.max_value is not None and value > param_def.max_value:
                    raise ToolError(f"Parameter '{name}' must be <= {param_def.max_value}")
            
            # String length validation
            if isinstance(value, str):
                if param_def.min_length is not None and len(value) < param_def.min_length:
                    raise ToolError(f"Parameter '{name}' must be at least {param_def.min_length} characters")
                if param_def.max_length is not None and len(value) > param_def.max_length:
                    raise ToolError(f"Parameter '{name}' must be at most {param_def.max_length} characters")
                
                # Pattern validation
                if param_def.pattern:
                    import re
                    if not re.match(param_def.pattern, value):
                        raise ToolError(f"Parameter '{name}' does not match required pattern")
            
        except Exception as e:
            logger.error(f"Parameter '{name}' validation failed: {e}")
            raise ToolError(f"Parameter '{name}' validation failed: {e}") from e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        avg_execution_time = (
            self.total_execution_time / self.execution_count
            if self.execution_count > 0 else 0
        )
        
        return {
            "name": self._get_metadata().name,
            "category": self._get_metadata().category.value,
            "version": self._get_metadata().version,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_execution_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.execution_count if self.execution_count > 0 else 0,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get complete tool information."""
        metadata = self._get_metadata()
        definition = self._get_definition()
        stats = self.get_stats()
        
        return {
            "metadata": {
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category.value,
                "version": metadata.version,
                "author": metadata.author,
                "created_at": metadata.created_at.isoformat(),
                "updated_at": metadata.updated_at.isoformat(),
                "tags": metadata.tags,
                "dependencies": metadata.dependencies,
                "requirements": metadata.requirements
            },
            "definition": {
                "parameters": {
                    name: {
                        "type": param.type.__name__,
                        "description": param.description,
                        "required": param.required,
                        "default": param.default,
                        "choices": param.choices,
                        "min_value": param.min_value,
                        "max_value": param.max_value,
                        "pattern": param.pattern,
                        "min_length": param.min_length,
                        "max_length": param.max_length
                    }
                    for name, param in definition.parameters.items()
                },
                "return_type": definition.return_type.__name__,
                "examples": definition.examples,
                "error_codes": definition.error_codes
            },
            "statistics": stats
        }
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"Tool(name='{self._get_metadata().name}', category='{self._get_metadata().category.value}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return (
            f"Tool(name='{self._get_metadata().name}', "
            f"category='{self._get_metadata().category.value}', "
            f"version='{self._get_metadata().version}', "
            f"executions={self.execution_count})"
        )


class ToolRegistry:
    """
    Registry for managing tools in the unified framework.
    
    This class provides functionality to register, discover, and manage
    tools across the framework.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[ToolCategory, List[str]] = {category: [] for category in ToolCategory}
        
        logger.info("Tool registry initialized")
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool: Tool to register
            
        Raises:
            ToolError: If registration fails
        """
        try:
            metadata = tool._get_metadata()
            tool_name = metadata.name
            
            if tool_name in self._tools:
                logger.warning(f"Tool '{tool_name}' is already registered, replacing...")
            
            self._tools[tool_name] = tool
            
            # Update category index
            category = metadata.category
            if tool_name not in self._categories[category]:
                self._categories[category].append(tool_name)
            
            logger.info(f"Tool '{tool_name}' registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register tool: {e}")
            raise ToolError(f"Tool registration failed: {e}") from e
    
    def unregister_tool(self, tool_name: str) -> None:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: Name of the tool to unregister
        """
        try:
            if tool_name not in self._tools:
                logger.warning(f"Tool '{tool_name}' is not registered")
                return
            
            tool = self._tools[tool_name]
            metadata = tool._get_metadata()
            category = metadata.category
            
            # Remove from tools
            del self._tools[tool_name]
            
            # Remove from category index
            if tool_name in self._categories[category]:
                self._categories[category].remove(tool_name)
            
            logger.info(f"Tool '{tool_name}' unregistered successfully")
            
        except Exception as e:
            logger.error(f"Failed to unregister tool '{tool_name}': {e}")
            raise ToolError(f"Tool unregistration failed: {e}") from e
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tools in the category
        """
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all registered tools.
        
        Returns:
            List of all tools
        """
        return list(self._tools.values())
    
    def search_tools(self, query: str) -> List[BaseTool]:
        """
        Search for tools by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self._tools.values():
            metadata = tool._get_metadata()
            
            # Search in name, description, and tags
            if (query_lower in metadata.name.lower() or
                query_lower in metadata.description.lower() or
                any(query_lower in tag.lower() for tag in metadata.tags)):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information or None if not found
        """
        tool = self.get_tool(tool_name)
        return tool.get_info() if tool else None
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_tools = len(self._tools)
        category_counts = {
            category.value: len(tools) 
            for category, tools in self._categories.items()
        }
        
        return {
            "total_tools": total_tools,
            "category_counts": category_counts,
            "tools": list(self._tools.keys())
        }
    
    def __len__(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    def __iter__(self):
        """Iterate over registered tools."""
        return iter(self._tools.values())