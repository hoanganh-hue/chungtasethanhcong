"""
Environment Management System.

This module provides environment management for different execution contexts,
including local, Docker, and cloud environments.
"""

import asyncio
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from ..utils.exceptions import EnvironmentError, ResourceError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EnvironmentType(str, Enum):
    """Environment types."""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"
    SANDBOX = "sandbox"


class EnvironmentStatus(str, Enum):
    """Environment status."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    CLEANUP = "cleanup"


class ResourceLimits(BaseModel):
    """Resource limits for environment."""
    cpu_cores: Optional[int] = Field(None, description="CPU cores limit")
    memory_mb: Optional[int] = Field(None, description="Memory limit in MB")
    disk_gb: Optional[int] = Field(None, description="Disk limit in GB")
    network_access: bool = Field(default=True, description="Allow network access")
    file_system_access: bool = Field(default=True, description="Allow file system access")
    timeout_seconds: int = Field(default=300, description="Execution timeout")


class EnvironmentConfig(BaseModel):
    """Environment configuration."""
    environment_type: EnvironmentType = Field(..., description="Environment type")
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits, description="Resource limits")
    working_directory: Optional[str] = Field(None, description="Working directory")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    python_path: Optional[str] = Field(None, description="Python executable path")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    sandbox: bool = Field(default=True, description="Enable sandboxing")
    isolation: bool = Field(default=True, description="Enable isolation")


class BaseEnvironment(ABC):
    """Base class for all environments."""
    
    def __init__(self, config: EnvironmentConfig):
        """
        Initialize environment.
        
        Args:
            config: Environment configuration
        """
        self.config = config
        self.status = EnvironmentStatus.IDLE
        self.created_at = datetime.now()
        self.last_used = None
        self.usage_count = 0
        self.error_count = 0
        
        logger.debug(f"Initialized {config.environment_type} environment")
    
    @abstractmethod
    async def setup(self) -> None:
        """Setup environment."""
        pass
    
    @abstractmethod
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute command in environment."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup environment."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "type": self.config.environment_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "error_count": self.error_count,
            "config": self.config.model_dump()
        }


class LocalEnvironment(BaseEnvironment):
    """Local environment implementation."""
    
    def __init__(self, config: EnvironmentConfig):
        """Initialize local environment."""
        super().__init__(config)
        self.working_dir = None
        self.temp_dir = None
    
    async def setup(self) -> None:
        """Setup local environment."""
        try:
            self.status = EnvironmentStatus.INITIALIZING
            
            # Create working directory
            if self.config.working_directory:
                self.working_dir = Path(self.config.working_directory)
                self.working_dir.mkdir(parents=True, exist_ok=True)
            else:
                self.temp_dir = tempfile.mkdtemp()
                self.working_dir = Path(self.temp_dir)
            
            # Set environment variables
            for key, value in self.config.environment_variables.items():
                os.environ[key] = value
            
            # Install dependencies if specified
            if self.config.dependencies:
                await self._install_dependencies()
            
            self.status = EnvironmentStatus.READY
            logger.info(f"Local environment setup completed: {self.working_dir}")
            
        except Exception as e:
            self.status = EnvironmentStatus.ERROR
            logger.error(f"Failed to setup local environment: {e}")
            raise EnvironmentError(f"Local environment setup failed: {e}") from e
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute command in local environment."""
        try:
            self.status = EnvironmentStatus.RUNNING
            self.last_used = datetime.now()
            
            # Prepare command
            if self.working_dir:
                command = f"cd {self.working_dir} && {command}"
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir
            )
            
            # Wait for completion with timeout
            timeout = self.config.resource_limits.timeout_seconds
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            result = {
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
                "success": process.returncode == 0
            }
            
            self.usage_count += 1
            self.status = EnvironmentStatus.READY
            
            logger.debug(f"Command executed: {command[:100]}...")
            return result
            
        except asyncio.TimeoutError:
            self.error_count += 1
            self.status = EnvironmentStatus.ERROR
            raise EnvironmentError(f"Command timeout after {timeout} seconds")
        
        except Exception as e:
            self.error_count += 1
            self.status = EnvironmentStatus.ERROR
            logger.error(f"Command execution failed: {e}")
            raise EnvironmentError(f"Command execution failed: {e}") from e
    
    async def cleanup(self) -> None:
        """Cleanup local environment."""
        try:
            self.status = EnvironmentStatus.CLEANUP
            
            # Cleanup temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            
            self.status = EnvironmentStatus.IDLE
            logger.info("Local environment cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup local environment: {e}")
            raise EnvironmentError(f"Local environment cleanup failed: {e}") from e
    
    async def _install_dependencies(self) -> None:
        """Install Python dependencies."""
        if not self.config.dependencies:
            return
        
        # Create requirements file
        requirements_file = self.working_dir / "requirements.txt"
        with open(requirements_file, 'w') as f:
            for dep in self.config.dependencies:
                f.write(f"{dep}\n")
        
        # Install dependencies
        install_command = f"pip install -r {requirements_file}"
        result = await self.execute(install_command)
        
        if not result["success"]:
            raise EnvironmentError(f"Failed to install dependencies: {result['stderr']}")


class DockerEnvironment(BaseEnvironment):
    """Docker environment implementation."""
    
    def __init__(self, config: EnvironmentConfig):
        """Initialize Docker environment."""
        super().__init__(config)
        self.container_id = None
        self.image_name = "python:3.12-slim"
    
    async def setup(self) -> None:
        """Setup Docker environment."""
        try:
            self.status = EnvironmentStatus.INITIALIZING
            
            # Import docker here to avoid import errors if not available
            import docker
            
            self.docker_client = docker.from_env()
            
            # Create container
            container_config = {
                "image": self.image_name,
                "working_dir": "/workspace",
                "environment": self.config.environment_variables,
                "mem_limit": f"{self.config.resource_limits.memory_mb}m" if self.config.resource_limits.memory_mb else None,
                "cpu_count": self.config.resource_limits.cpu_cores,
                "network_disabled": not self.config.resource_limits.network_access,
                "read_only": not self.config.resource_limits.file_system_access,
                "detach": True,
                "tty": True
            }
            
            self.container = self.docker_client.containers.run(**container_config)
            self.container_id = self.container.id
            
            # Install dependencies
            if self.config.dependencies:
                await self._install_dependencies()
            
            self.status = EnvironmentStatus.READY
            logger.info(f"Docker environment setup completed: {self.container_id}")
            
        except ImportError:
            raise EnvironmentError("Docker package not available. Install with: pip install docker")
        except Exception as e:
            self.status = EnvironmentStatus.ERROR
            logger.error(f"Failed to setup Docker environment: {e}")
            raise EnvironmentError(f"Docker environment setup failed: {e}") from e
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute command in Docker container."""
        try:
            self.status = EnvironmentStatus.RUNNING
            self.last_used = datetime.now()
            
            # Execute command in container
            result = self.container.exec_run(
                command,
                workdir="/workspace",
                timeout=self.config.resource_limits.timeout_seconds
            )
            
            output = {
                "return_code": result.exit_code,
                "stdout": result.output.decode('utf-8'),
                "stderr": "",
                "success": result.exit_code == 0
            }
            
            self.usage_count += 1
            self.status = EnvironmentStatus.READY
            
            logger.debug(f"Docker command executed: {command[:100]}...")
            return output
            
        except Exception as e:
            self.error_count += 1
            self.status = EnvironmentStatus.ERROR
            logger.error(f"Docker command execution failed: {e}")
            raise EnvironmentError(f"Docker command execution failed: {e}") from e
    
    async def cleanup(self) -> None:
        """Cleanup Docker environment."""
        try:
            self.status = EnvironmentStatus.CLEANUP
            
            if self.container:
                self.container.stop()
                self.container.remove()
                self.container = None
                self.container_id = None
            
            self.status = EnvironmentStatus.IDLE
            logger.info("Docker environment cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup Docker environment: {e}")
            raise EnvironmentError(f"Docker environment cleanup failed: {e}") from e
    
    async def _install_dependencies(self) -> None:
        """Install Python dependencies in Docker container."""
        if not self.config.dependencies:
            return
        
        # Create requirements file
        requirements_content = "\n".join(self.config.dependencies)
        self.container.exec_run(
            f"echo '{requirements_content}' > /workspace/requirements.txt"
        )
        
        # Install dependencies
        result = self.container.exec_run("pip install -r /workspace/requirements.txt")
        
        if result.exit_code != 0:
            raise EnvironmentError(f"Failed to install dependencies: {result.output.decode()}")


class EnvironmentManager:
    """Manages multiple environments."""
    
    def __init__(self):
        """Initialize environment manager."""
        self.environments: Dict[str, BaseEnvironment] = {}
        self.default_environment: Optional[str] = None
        
        logger.info("Environment manager initialized")
    
    def create_environment(
        self,
        name: str,
        config: EnvironmentConfig,
        set_as_default: bool = False
    ) -> BaseEnvironment:
        """
        Create a new environment.
        
        Args:
            name: Environment name
            config: Environment configuration
            set_as_default: Whether to set as default environment
            
        Returns:
            Created environment
        """
        if name in self.environments:
            raise EnvironmentError(f"Environment {name} already exists")
        
        # Create environment based on type
        if config.environment_type == EnvironmentType.LOCAL:
            environment = LocalEnvironment(config)
        elif config.environment_type == EnvironmentType.DOCKER:
            environment = DockerEnvironment(config)
        else:
            raise EnvironmentError(f"Unsupported environment type: {config.environment_type}")
        
        self.environments[name] = environment
        
        if set_as_default or not self.default_environment:
            self.default_environment = name
        
        logger.info(f"Created environment: {name} ({config.environment_type})")
        return environment
    
    def get_environment(self, name: Optional[str] = None) -> Optional[BaseEnvironment]:
        """
        Get environment by name.
        
        Args:
            name: Environment name (uses default if None)
            
        Returns:
            Environment instance or None if not found
        """
        if name is None:
            name = self.default_environment
        
        if name is None:
            return None
        
        return self.environments.get(name)
    
    def list_environments(self) -> List[str]:
        """List all environment names."""
        return list(self.environments.keys())
    
    def remove_environment(self, name: str) -> bool:
        """
        Remove environment.
        
        Args:
            name: Environment name
            
        Returns:
            True if removed, False if not found
        """
        if name not in self.environments:
            return False
        
        environment = self.environments[name]
        
        # Cleanup environment
        try:
            asyncio.create_task(environment.cleanup())
        except Exception as e:
            logger.warning(f"Failed to cleanup environment {name}: {e}")
        
        # Remove from manager
        del self.environments[name]
        
        # Update default if necessary
        if self.default_environment == name:
            self.default_environment = self.list_environments()[0] if self.environments else None
        
        logger.info(f"Removed environment: {name}")
        return True
    
    async def setup_all(self) -> None:
        """Setup all environments."""
        for name, environment in self.environments.items():
            try:
                await environment.setup()
                logger.info(f"Environment {name} setup completed")
            except Exception as e:
                logger.error(f"Failed to setup environment {name}: {e}")
    
    async def cleanup_all(self) -> None:
        """Cleanup all environments."""
        for name, environment in self.environments.items():
            try:
                await environment.cleanup()
                logger.info(f"Environment {name} cleanup completed")
            except Exception as e:
                logger.error(f"Failed to cleanup environment {name}: {e}")
    
    def get_manager_info(self) -> Dict[str, Any]:
        """Get environment manager information."""
        return {
            "total_environments": len(self.environments),
            "default_environment": self.default_environment,
            "environments": {
                name: env.get_info() 
                for name, env in self.environments.items()
            }
        }
    
    def __len__(self) -> int:
        """Return number of environments."""
        return len(self.environments)
    
    def __contains__(self, name: str) -> bool:
        """Check if environment exists."""
        return name in self.environments
    
    def __str__(self) -> str:
        """String representation of manager."""
        return f"EnvironmentManager(environments={len(self.environments)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of manager."""
        return f"EnvironmentManager(environments={len(self.environments)}, default={self.default_environment})"