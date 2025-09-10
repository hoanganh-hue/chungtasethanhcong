"""
Custom exceptions for the unified framework.

This module defines all custom exceptions used throughout the framework,
providing clear error handling and debugging information.
"""

from typing import Any, Dict, Optional


class UnifiedFrameworkError(Exception):
    """Base exception for all framework errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize framework error.
        
        Args:
            message: Error message
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """String representation of error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class AgentError(UnifiedFrameworkError):
    """Exception raised for agent-related errors."""
    
    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent error.
        
        Args:
            message: Error message
            agent_name: Name of the agent that caused the error
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.agent_name = agent_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["agent_name"] = self.agent_name
        return result


class ToolError(UnifiedFrameworkError):
    """Exception raised for tool-related errors."""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize tool error.
        
        Args:
            message: Error message
            tool_name: Name of the tool that caused the error
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.tool_name = tool_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["tool_name"] = self.tool_name
        return result


class ConfigError(UnifiedFrameworkError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_file: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize config error.
        
        Args:
            message: Error message
            config_file: Path to the configuration file
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.config_file = config_file
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["config_file"] = self.config_file
        return result


class EnvironmentError(UnifiedFrameworkError):
    """Exception raised for environment-related errors."""
    
    def __init__(
        self,
        message: str,
        environment_type: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize environment error.
        
        Args:
            message: Error message
            environment_type: Type of environment that caused the error
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.environment_type = environment_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["environment_type"] = self.environment_type
        return result


class MemoryError(UnifiedFrameworkError):
    """Exception raised for memory-related errors."""
    
    def __init__(
        self,
        message: str,
        memory_type: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize memory error.
        
        Args:
            message: Error message
            memory_type: Type of memory that caused the error
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.memory_type = memory_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["memory_type"] = self.memory_type
        return result


class StateError(UnifiedFrameworkError):
    """Exception raised for state-related errors."""
    
    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize state error.
        
        Args:
            message: Error message
            current_state: Current state when error occurred
            target_state: Target state that caused the error
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.current_state = current_state
        self.target_state = target_state
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["current_state"] = self.current_state
        result["target_state"] = self.target_state
        return result


class ValidationError(UnifiedFrameworkError):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.field_name = field_name
        self.field_value = field_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["field_name"] = self.field_name
        result["field_value"] = self.field_value
        return result


class TimeoutError(UnifiedFrameworkError):
    """Exception raised for timeout errors."""
    
    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        operation: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_duration: Duration of the timeout
            operation: Operation that timed out
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.timeout_duration = timeout_duration
        self.operation = operation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["timeout_duration"] = self.timeout_duration
        result["operation"] = self.operation
        return result


class ResourceError(UnifiedFrameworkError):
    """Exception raised for resource-related errors."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize resource error.
        
        Args:
            message: Error message
            resource_type: Type of resource that caused the error
            resource_name: Name of the resource
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.resource_type = resource_type
        self.resource_name = resource_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["resource_type"] = self.resource_type
        result["resource_name"] = self.resource_name
        return result


class NetworkError(UnifiedFrameworkError):
    """Exception raised for network-related errors."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize network error.
        
        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.url = url
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["url"] = self.url
        result["status_code"] = self.status_code
        return result


class AuthenticationError(UnifiedFrameworkError):
    """Exception raised for authentication errors."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            service: Service that failed authentication
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.service = service
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["service"] = self.service
        return result


class AuthorizationError(UnifiedFrameworkError):
    """Exception raised for authorization errors."""
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize authorization error.
        
        Args:
            message: Error message
            resource: Resource that was not authorized
            action: Action that was not authorized
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message, error_code, details)
        self.resource = resource
        self.action = action
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result = super().to_dict()
        result["resource"] = self.resource
        result["action"] = self.action
        return result