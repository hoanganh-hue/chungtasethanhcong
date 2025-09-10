"""
Unified Tool Registry System.

This module provides a unified tool registry that manages all tools
from both OpenManus and Youtu-Agent, with a common interface.
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Type, Set
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator

from ..utils.exceptions import ToolError, ValidationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolCategory(str, Enum):
    """Tool categories for organization."""
    WEB = "web"
    DATA = "data"
    ANALYSIS = "analysis"
    FILE = "file"
    SYSTEM = "system"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"
    RESEARCH = "research"
    VISUALIZATION = "visualization"
    CUSTOM = "custom"


class ToolStatus(str, Enum):
    """Tool status states."""
    AVAILABLE = "available"
    LOADING = "loading"
    ERROR = "error"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class ToolMetadata(BaseModel):
    """Metadata for a tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: ToolCategory = Field(..., description="Tool category")
    version: str = Field(default="1.0.0", description="Tool version")
    author: str = Field(default="Unknown", description="Tool author")
    tags: List[str] = Field(default_factory=list, description="Tool tags")
    dependencies: List[str] = Field(default_factory=list, description="Tool dependencies")
    requirements: List[str] = Field(default_factory=list, description="Tool requirements")
    status: ToolStatus = Field(default=ToolStatus.AVAILABLE, description="Tool status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return self.model_dump()


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str = Field(..., description="Parameter name")
    type: Type = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Any = Field(default=None, description="Default value")
    choices: Optional[List[Any]] = Field(None, description="Valid choices")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum value")
    
    def validate(self, value: Any) -> Any:
        """Validate parameter value."""
        if value is None and self.required:
            raise ValidationError(f"Required parameter {self.name} is missing")
        
        if value is None and not self.required:
            return self.default
        
        # Type validation
        if not isinstance(value, self.type):
            try:
                value = self.type(value)
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Invalid type for {self.name}: {e}")
        
        # Choices validation
        if self.choices and value not in self.choices:
            raise ValidationError(f"Invalid choice for {self.name}: {value}")
        
        # Range validation
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Value too small for {self.name}: {value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Value too large for {self.name}: {value}")
        
        return value


class ToolDefinition(BaseModel):
    """Complete tool definition."""
    metadata: ToolMetadata = Field(..., description="Tool metadata")
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict, description="Tool parameters")
    return_type: Type = Field(default=str, description="Return type")
    is_async: bool = Field(default=False, description="Whether tool is async")
    timeout: int = Field(default=30, description="Tool timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert definition to dictionary."""
        return self.model_dump()


class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize tool.
        
        Args:
            config: Tool configuration
        """
        self.config = config or {}
        self.metadata = self._get_metadata()
        self.definition = self._get_definition()
        self.status = ToolStatus.AVAILABLE
        self.last_used = None
        self.usage_count = 0
        self.error_count = 0
        
        logger.debug(f"Initialized tool: {self.metadata.name}")
    
    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _get_definition(self) -> ToolDefinition:
        """Get tool definition. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute tool. Must be implemented by subclasses."""
        pass
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate tool parameters."""
        validated = {}
        
        for param_name, param_def in self.definition.parameters.items():
            if param_name in kwargs:
                validated[param_name] = param_def.validate(kwargs[param_name])
            elif param_def.required:
                raise ValidationError(f"Required parameter {param_name} is missing")
            else:
                validated[param_name] = param_def.default
        
        return validated
    
    async def run(self, **kwargs) -> Any:
        """Run tool with validation and error handling."""
        try:
            # Validate parameters
            validated_kwargs = self.validate_parameters(**kwargs)
            
            # Execute tool
            result = await self.execute(**validated_kwargs)
            
            # Update usage statistics
            self.last_used = datetime.now()
            self.usage_count += 1
            
            logger.debug(f"Tool {self.metadata.name} executed successfully")
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Tool {self.metadata.name} execution failed: {e}")
            raise ToolError(f"Tool execution failed: {e}", tool_name=self.metadata.name) from e
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "metadata": self.metadata.to_dict(),
            "definition": self.definition.to_dict(),
            "status": self.status,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.usage_count, 1)
        }


class ToolRegistry:
    """Unified tool registry for managing all tools."""
    
    def __init__(self):
        """Initialize tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._tool_definitions: Dict[str, ToolDefinition] = {}
        self._tool_instances: Dict[str, BaseTool] = {}
        self._categories: Dict[ToolCategory, Set[str]] = {cat: set() for cat in ToolCategory}
        self._dependencies: Dict[str, Set[str]] = {}
        
        logger.info("Tool registry initialized")
    
    def register_tool(
        self,
        tool_class: Type[BaseTool],
        config: Optional[Dict[str, Any]] = None,
        override: bool = False
    ) -> str:
        """
        Register a tool class.
        
        Args:
            tool_class: Tool class to register
            config: Tool configuration
            override: Whether to override existing tool
            
        Returns:
            Tool name
            
        Raises:
            ToolError: If registration fails
        """
        try:
            # Create temporary instance to get metadata
            temp_instance = tool_class(config)
            tool_name = temp_instance.metadata.name
            
            # Check if tool already exists
            if tool_name in self._tools and not override:
                raise ToolError(f"Tool {tool_name} already registered")
            
            # Register tool
            self._tools[tool_name] = tool_class
            self._tool_definitions[tool_name] = temp_instance.definition
            
            # Add to category
            category = temp_instance.metadata.category
            self._categories[category].add(tool_name)
            
            # Register dependencies
            self._dependencies[tool_name] = set(temp_instance.metadata.dependencies)
            
            logger.info(f"Registered tool: {tool_name} (category: {category})")
            return tool_name
            
        except Exception as e:
            raise ToolError(f"Failed to register tool {tool_class.__name__}: {e}") from e
    
    def register_function(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: ToolCategory = ToolCategory.CUSTOM,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a function as a tool.
        
        Args:
            func: Function to register
            name: Tool name (uses function name if None)
            description: Tool description
            category: Tool category
            config: Tool configuration
            
        Returns:
            Tool name
        """
        tool_name = name or func.__name__
        description = description or func.__doc__ or f"Function {func.__name__}"
        
        # Create tool class dynamically
        class FunctionTool(BaseTool):
            def _get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name=tool_name,
                    description=description,
                    category=category
                )
            
            def _get_definition(self) -> ToolDefinition:
                # Analyze function signature
                sig = inspect.signature(func)
                parameters = {}
                
                for param_name, param in sig.parameters.items():
                    param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
                    required = param.default == inspect.Parameter.empty
                    default = param.default if param.default != inspect.Parameter.empty else None
                    
                    parameters[param_name] = ToolParameter(
                        name=param_name,
                        type=param_type,
                        description=f"Parameter {param_name}",
                        required=required,
                        default=default
                    )
                
                return ToolDefinition(
                    metadata=self._get_metadata(),
                    parameters=parameters,
                    return_type=func.__annotations__.get('return', str),
                    is_async=inspect.iscoroutinefunction(func)
                )
            
            async def execute(self, **kwargs) -> Any:
                if self.definition.is_async:
                    return await func(**kwargs)
                else:
                    return func(**kwargs)
        
        return self.register_tool(FunctionTool, config)
    
    def get_tool(self, name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseTool]:
        """
        Get tool instance.
        
        Args:
            name: Tool name
            config: Tool configuration
            
        Returns:
            Tool instance or None if not found
        """
        if name not in self._tools:
            logger.warning(f"Tool {name} not found in registry")
            return None
        
        # Check if instance already exists
        instance_key = f"{name}_{hash(str(config))}"
        if instance_key in self._tool_instances:
            return self._tool_instances[instance_key]
        
        try:
            # Create new instance
            tool_class = self._tools[name]
            instance = tool_class(config)
            self._tool_instances[instance_key] = instance
            
            logger.debug(f"Created tool instance: {name}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create tool instance {name}: {e}")
            return None
    
    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        status: Optional[ToolStatus] = None
    ) -> List[str]:
        """
        List available tools.
        
        Args:
            category: Filter by category
            status: Filter by status
            
        Returns:
            List of tool names
        """
        tools = list(self._tools.keys())
        
        if category:
            tools = [t for t in tools if t in self._categories[category]]
        
        if status:
            tools = [t for t in tools if self._get_tool_status(t) == status]
        
        return sorted(tools)
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool information."""
        if name not in self._tools:
            return None
        
        # Get definition
        definition = self._tool_definitions.get(name)
        if not definition:
            return None
        
        return {
            "name": name,
            "definition": definition.to_dict(),
            "dependencies": list(self._dependencies.get(name, [])),
            "status": self._get_tool_status(name)
        }
    
    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """Get tools by category."""
        return sorted(list(self._categories[category]))
    
    def get_tool_dependencies(self, name: str) -> Set[str]:
        """Get tool dependencies."""
        return self._dependencies.get(name, set()).copy()
    
    def validate_tool_dependencies(self, tool_names: List[str]) -> List[str]:
        """Validate tool dependencies and return missing tools."""
        missing = []
        all_tools = set(tool_names)
        
        for tool_name in tool_names:
            dependencies = self._dependencies.get(tool_name, set())
            missing_deps = dependencies - all_tools
            missing.extend(missing_deps)
        
        return list(set(missing))
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if unregistered, False if not found
        """
        if name not in self._tools:
            return False
        
        # Remove from registry
        del self._tools[name]
        del self._tool_definitions[name]
        
        # Remove from category
        for category, tools in self._categories.items():
            tools.discard(name)
        
        # Remove dependencies
        self._dependencies.pop(name, None)
        
        # Remove instances
        instances_to_remove = [k for k in self._tool_instances.keys() if k.startswith(f"{name}_")]
        for key in instances_to_remove:
            del self._tool_instances[key]
        
        logger.info(f"Unregistered tool: {name}")
        return True
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_tools = len(self._tools)
        total_instances = len(self._tool_instances)
        
        category_counts = {
            category.value: len(tools) 
            for category, tools in self._categories.items()
        }
        
        return {
            "total_tools": total_tools,
            "total_instances": total_instances,
            "category_counts": category_counts,
            "tools": list(self._tools.keys())
        }
    
    def _get_tool_status(self, name: str) -> ToolStatus:
        """Get tool status."""
        if name not in self._tools:
            return ToolStatus.ERROR
        
        # Check if tool has instances
        has_instances = any(k.startswith(f"{name}_") for k in self._tool_instances.keys())
        
        if has_instances:
            return ToolStatus.AVAILABLE
        else:
            return ToolStatus.LOADING
    
    def clear(self) -> None:
        """Clear all tools from registry."""
        self._tools.clear()
        self._tool_definitions.clear()
        self._tool_instances.clear()
        self._categories = {cat: set() for cat in ToolCategory}
        self._dependencies.clear()
        
        logger.info("Tool registry cleared")
    
    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools
    
    def __iter__(self):
        """Iterate over tool names."""
        return iter(self._tools.keys())
    
    def __str__(self) -> str:
        """String representation of registry."""
        return f"ToolRegistry(tools={len(self._tools)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of registry."""
        stats = self.get_registry_stats()
        return f"ToolRegistry(tools={stats['total_tools']}, instances={stats['total_instances']})"


# Global tool registry instance
tool_registry = ToolRegistry()