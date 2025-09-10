"""
API Models for OpenManus-Youtu Integrated Framework

This module defines Pydantic models for API request/response validation.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    """Agent type enumeration."""
    SIMPLE = "simple"
    BROWSER = "browser"
    ORCHESTRA = "orchestra"
    META = "meta"


class ToolCategory(str, Enum):
    """Tool category enumeration."""
    WEB = "web"
    SEARCH = "search"
    ANALYSIS = "analysis"
    DATA = "data"
    FILE = "file"
    AUTOMATION = "automation"
    COMMUNICATION = "communication"
    SYSTEM = "system"


class ParameterType(str, Enum):
    """Parameter type enumeration."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FILE = "file"


class ParameterDefinition(BaseModel):
    """Parameter definition model."""
    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=False, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    examples: Optional[List[Any]] = Field(default=None, description="Example values")


class ToolMetadata(BaseModel):
    """Tool metadata model."""
    name: str = Field(..., description="Tool name")
    category: ToolCategory = Field(..., description="Tool category")
    description: str = Field(..., description="Tool description")
    parameters: List[ParameterDefinition] = Field(..., description="Tool parameters")
    examples: Optional[List[Dict[str, Any]]] = Field(default=None, description="Usage examples")


class AgentRequest(BaseModel):
    """Agent creation/execution request model."""
    agent_type: AgentType = Field(..., description="Type of agent to create")
    name: Optional[str] = Field(default=None, description="Custom agent name")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Agent configuration")
    task: Optional[str] = Field(default=None, description="Task to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Task parameters")


class AgentResponse(BaseModel):
    """Agent response model."""
    success: bool = Field(..., description="Whether operation was successful")
    agent_id: Optional[str] = Field(default=None, description="Created agent ID")
    result: Optional[Any] = Field(default=None, description="Execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ToolRequest(BaseModel):
    """Tool execution request model."""
    tool_name: str = Field(..., description="Name of tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    timeout: Optional[int] = Field(default=300, description="Execution timeout in seconds")


class ToolResponse(BaseModel):
    """Tool response model."""
    success: bool = Field(..., description="Whether execution was successful")
    result: Optional[Any] = Field(default=None, description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class WorkflowStep(BaseModel):
    """Workflow step model."""
    step_id: str = Field(..., description="Unique step identifier")
    agent_type: Optional[AgentType] = Field(default=None, description="Agent type for this step")
    tool_name: Optional[str] = Field(default=None, description="Tool name for this step")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    depends_on: Optional[List[str]] = Field(default=None, description="Dependent step IDs")


class WorkflowRequest(BaseModel):
    """Workflow execution request model."""
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(default=None, description="Workflow description")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    parallel: bool = Field(default=False, description="Whether to run steps in parallel")
    timeout: Optional[int] = Field(default=3600, description="Total workflow timeout in seconds")


class WorkflowResponse(BaseModel):
    """Workflow response model."""
    success: bool = Field(..., description="Whether workflow was successful")
    workflow_id: Optional[str] = Field(default=None, description="Workflow execution ID")
    results: Optional[Dict[str, Any]] = Field(default=None, description="Step results")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Total execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Framework version")
    uptime: float = Field(..., description="Service uptime in seconds")
    components: Dict[str, str] = Field(..., description="Component status")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="Performance metrics")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    code: Optional[str] = Field(default=None, description="Error code")
    timestamp: str = Field(..., description="Error timestamp")


class ListResponse(BaseModel):
    """List response model."""
    items: List[Any] = Field(..., description="List items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=10, description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")