"""
Unified Configuration System.

This module provides a unified configuration system that supports both
TOML and YAML formats, with automatic validation and type safety.
"""

import os
import yaml
import toml
from typing import Any, Dict, List, Optional, Union, Literal
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, Field, validator, model_validator
from pydantic_settings import BaseSettings

from ..utils.exceptions import ConfigError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelConfig(BaseModel):
    """Model configuration."""
    provider: Literal["openai", "anthropic", "google", "deepseek", "ollama"] = Field(
        default="openai", description="Model provider"
    )
    model_name: str = Field(..., description="Model name")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    api_key: Optional[str] = Field(None, description="API key")
    max_tokens: int = Field(default=4096, description="Maximum tokens")
    temperature: float = Field(default=0.7, description="Temperature")
    top_p: float = Field(default=1.0, description="Top-p sampling")
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, description="Presence penalty")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @validator("top_p")
    def validate_top_p(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Top-p must be between 0.0 and 1.0")
        return v


class ToolConfig(BaseModel):
    """Tool configuration."""
    name: str = Field(..., description="Tool name")
    enabled: bool = Field(default=True, description="Whether tool is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific configuration")
    dependencies: List[str] = Field(default_factory=list, description="Tool dependencies")
    timeout: int = Field(default=30, description="Tool timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")


class EnvironmentConfig(BaseModel):
    """Environment configuration."""
    type: Literal["local", "docker", "kubernetes", "cloud"] = Field(
        default="local", description="Environment type"
    )
    sandbox: bool = Field(default=True, description="Enable sandboxing")
    resource_limits: Dict[str, Any] = Field(default_factory=dict, description="Resource limits")
    network_access: bool = Field(default=True, description="Allow network access")
    file_system_access: bool = Field(default=True, description="Allow file system access")
    timeout: int = Field(default=300, description="Environment timeout in seconds")


class TracingConfig(BaseModel):
    """Tracing configuration."""
    enabled: bool = Field(default=True, description="Enable tracing")
    provider: Literal["local", "jaeger", "zipkin", "datadog"] = Field(
        default="local", description="Tracing provider"
    )
    endpoint: Optional[str] = Field(None, description="Tracing endpoint")
    sampling_rate: float = Field(default=1.0, description="Sampling rate")
    batch_size: int = Field(default=100, description="Batch size for traces")
    flush_interval: int = Field(default=5, description="Flush interval in seconds")


class BenchmarkConfig(BaseModel):
    """Benchmark configuration."""
    enabled: bool = Field(default=False, description="Enable benchmarking")
    datasets: List[str] = Field(default_factory=list, description="Benchmark datasets")
    metrics: List[str] = Field(default_factory=list, description="Metrics to track")
    output_dir: str = Field(default="benchmarks", description="Output directory")
    save_results: bool = Field(default=True, description="Save benchmark results")


class SecurityConfig(BaseModel):
    """Security configuration."""
    authentication: bool = Field(default=False, description="Enable authentication")
    authorization: bool = Field(default=False, description="Enable authorization")
    encryption: bool = Field(default=True, description="Enable encryption")
    audit_logging: bool = Field(default=True, description="Enable audit logging")
    rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    cors_enabled: bool = Field(default=True, description="Enable CORS")


class APIConfig(BaseModel):
    """API configuration."""
    host: str = Field(default="127.0.0.1", description="API host")
    port: int = Field(default=8000, description="API port")
    workers: int = Field(default=1, description="Number of workers")
    reload: bool = Field(default=False, description="Enable auto-reload")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Log level"
    )
    docs_url: str = Field(default="/docs", description="API documentation URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")


class UnifiedConfig(BaseModel):
    """
    Unified configuration for the entire framework.
    
    This configuration class supports both TOML and YAML formats and provides
    comprehensive configuration for all framework components.
    """
    
    # Metadata
    version: str = Field(default="0.1.0", description="Configuration version")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Core configuration
    model: ModelConfig = Field(..., description="Model configuration")
    tools: List[str] = Field(default_factory=list, description="Enabled tools")
    tool_configs: Dict[str, ToolConfig] = Field(default_factory=dict, description="Tool configurations")
    
    # Environment configuration
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig, description="Environment configuration")
    
    # Agent configuration
    agent_name: str = Field(default="unified-agent", description="Agent name")
    agent_description: str = Field(default="A unified AI agent", description="Agent description")
    max_steps: int = Field(default=50, description="Maximum execution steps")
    timeout: int = Field(default=300, description="Execution timeout in seconds")
    
    # Tracing and monitoring
    tracing: TracingConfig = Field(default_factory=TracingConfig, description="Tracing configuration")
    benchmark: BenchmarkConfig = Field(default_factory=BenchmarkConfig, description="Benchmark configuration")
    
    # Security
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    
    # API configuration
    api: APIConfig = Field(default_factory=APIConfig, description="API configuration")
    
    # Additional settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Log level"
    )
    data_dir: str = Field(default="data", description="Data directory")
    cache_dir: str = Field(default="cache", description="Cache directory")
    temp_dir: str = Field(default="temp", description="Temporary directory")
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
    
    @model_validator(mode="after")
    def validate_config(self) -> "UnifiedConfig":
        """Validate configuration after initialization."""
        # Validate tool configurations
        for tool_name in self.tools:
            if tool_name not in self.tool_configs:
                logger.warning(f"Tool {tool_name} is enabled but has no configuration")
        
        # Validate directories
        for dir_name in ["data_dir", "cache_dir", "temp_dir"]:
            dir_path = getattr(self, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
        
        return self
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "UnifiedConfig":
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file (TOML or YAML)
            
        Returns:
            UnifiedConfig instance
            
        Raises:
            ConfigError: If file cannot be loaded or parsed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.toml':
                    data = toml.load(f)
                else:
                    raise ConfigError(f"Unsupported configuration format: {file_path.suffix}")
            
            # Create configuration instance
            config = cls(**data)
            
            logger.info(f"Configuration loaded from {file_path}")
            return config
            
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {file_path}: {e}") from e
    
    def save_to_file(self, file_path: Union[str, Path], format: Literal["yaml", "toml"] = "yaml") -> None:
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save configuration
            format: File format (yaml or toml)
            
        Raises:
            ConfigError: If file cannot be saved
        """
        file_path = Path(file_path)
        
        try:
            # Update timestamp
            self.updated_at = datetime.now()
            
            # Convert to dict
            data = self.model_dump()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif format.lower() == "toml":
                    toml.dump(data, f)
                else:
                    raise ConfigError(f"Unsupported format: {format}")
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            raise ConfigError(f"Failed to save configuration to {file_path}: {e}") from e
    
    def merge(self, other: "UnifiedConfig") -> "UnifiedConfig":
        """
        Merge another configuration into this one.
        
        Args:
            other: Configuration to merge
            
        Returns:
            New merged configuration
        """
        # Convert both to dicts
        self_dict = self.model_dump()
        other_dict = other.model_dump()
        
        # Merge configurations (other takes precedence)
        merged_dict = {**self_dict, **other_dict}
        
        # Create new configuration
        return UnifiedConfig(**merged_dict)
    
    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool."""
        return self.tool_configs.get(tool_name)
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled."""
        return tool_name in self.tools and self.get_tool_config(tool_name)?.enabled != False
    
    def validate_tool_dependencies(self) -> List[str]:
        """Validate tool dependencies and return missing tools."""
        missing_tools = []
        
        for tool_name in self.tools:
            tool_config = self.get_tool_config(tool_name)
            if tool_config:
                for dep in tool_config.dependencies:
                    if dep not in self.tools:
                        missing_tools.append(f"{tool_name} requires {dep}")
        
        return missing_tools
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for the configuration."""
        env_vars = {}
        
        # Model configuration
        if self.model.api_key:
            env_vars["OPENAI_API_KEY"] = self.model.api_key
        if self.model.base_url:
            env_vars["OPENAI_BASE_URL"] = self.model.base_url
        
        # Tool configurations
        for tool_name, tool_config in self.tool_configs.items():
            for key, value in tool_config.config.items():
                if isinstance(value, str):
                    env_vars[f"TOOL_{tool_name.upper()}_{key.upper()}"] = value
        
        return env_vars
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"UnifiedConfig(version={self.version}, agent={self.agent_name}, tools={len(self.tools)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of configuration."""
        return f"UnifiedConfig(version={self.version}, agent={self.agent_name}, model={self.model.model_name}, tools={self.tools})"