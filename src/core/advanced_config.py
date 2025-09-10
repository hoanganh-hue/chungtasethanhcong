"""
Advanced Configuration Manager for OpenManus-Youtu Integrated Framework
Comprehensive configuration management with validation and environment support
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///./app.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

@dataclass
class RedisConfig:
    """Redis configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True

@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

@dataclass
class CORSConfig:
    """CORS configuration."""
    allow_origins: List[str] = None
    allow_credentials: bool = True
    allow_methods: List[str] = None
    allow_headers: List[str] = None
    max_age: int = 600

    def __post_init__(self):
        if self.allow_origins is None:
            self.allow_origins = ["http://localhost:3000", "http://localhost:8080"]
        if self.allow_methods is None:
            self.allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.allow_headers is None:
            self.allow_headers = ["*"]

@dataclass
class GeminiConfig:
    """Gemini API configuration."""
    api_key: str = ""
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    retry_attempts: int = 3
    enable_function_calling: bool = True
    enable_streaming: bool = True
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"

@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_tracing: bool = False
    tracing_endpoint: Optional[str] = None

@dataclass
class CacheConfig:
    """Cache configuration."""
    enable_cache: bool = True
    cache_ttl: int = 3600
    max_cache_size: int = 1000
    cache_backend: str = "memory"  # memory, redis, memcached

@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    enable_rate_limiting: bool = True
    requests_per_minute: int = 60
    burst_size: int = 10
    window_size: int = 60

@dataclass
class AdvancedConfig:
    """Advanced configuration for the entire system."""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Database
    database: DatabaseConfig = None
    
    # Redis
    redis: RedisConfig = None
    
    # Security
    security: SecurityConfig = None
    
    # CORS
    cors: CORSConfig = None
    
    # Gemini
    gemini: GeminiConfig = None
    
    # Monitoring
    monitoring: MonitoringConfig = None
    
    # Cache
    cache: CacheConfig = None
    
    # Rate Limiting
    rate_limit: RateLimitConfig = None
    
    # Trusted hosts
    trusted_hosts: List[str] = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.redis is None:
            self.redis = RedisConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.cors is None:
            self.cors = CORSConfig()
        if self.gemini is None:
            self.gemini = GeminiConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()
        if self.cache is None:
            self.cache = CacheConfig()
        if self.rate_limit is None:
            self.rate_limit = RateLimitConfig()
        if self.trusted_hosts is None:
            self.trusted_hosts = ["localhost", "127.0.0.1"]

class AdvancedConfigManager:
    """Advanced configuration manager."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config.yaml")
        self.config: Optional[AdvancedConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment."""
        try:
            # Load from file if exists
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Convert to AdvancedConfig
                self.config = self._dict_to_config(config_data)
            else:
                # Create default config
                self.config = AdvancedConfig()
            
            # Override with environment variables
            self._load_from_environment()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = AdvancedConfig()
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AdvancedConfig:
        """Convert dictionary to AdvancedConfig."""
        try:
            # Handle nested configurations
            config_data = {}
            
            for key, value in data.items():
                if key == "environment" and isinstance(value, str):
                    config_data[key] = Environment(value)
                elif key == "log_level" and isinstance(value, str):
                    config_data[key] = LogLevel(value)
                elif key == "database" and isinstance(value, dict):
                    config_data[key] = DatabaseConfig(**value)
                elif key == "redis" and isinstance(value, dict):
                    config_data[key] = RedisConfig(**value)
                elif key == "security" and isinstance(value, dict):
                    config_data[key] = SecurityConfig(**value)
                elif key == "cors" and isinstance(value, dict):
                    config_data[key] = CORSConfig(**value)
                elif key == "gemini" and isinstance(value, dict):
                    config_data[key] = GeminiConfig(**value)
                elif key == "monitoring" and isinstance(value, dict):
                    config_data[key] = MonitoringConfig(**value)
                elif key == "cache" and isinstance(value, dict):
                    config_data[key] = CacheConfig(**value)
                elif key == "rate_limit" and isinstance(value, dict):
                    config_data[key] = RateLimitConfig(**value)
                else:
                    config_data[key] = value
            
            return AdvancedConfig(**config_data)
            
        except Exception as e:
            logger.error(f"Failed to convert config data: {e}")
            return AdvancedConfig()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        if not self.config:
            return
        
        # Environment
        if env := os.getenv("ENVIRONMENT"):
            try:
                self.config.environment = Environment(env.lower())
            except ValueError:
                logger.warning(f"Invalid environment: {env}")
        
        # Debug
        if debug := os.getenv("DEBUG"):
            self.config.debug = debug.lower() in ("true", "1", "yes", "on")
        
        # Log level
        if log_level := os.getenv("LOG_LEVEL"):
            try:
                self.config.log_level = LogLevel(log_level.lower())
            except ValueError:
                logger.warning(f"Invalid log level: {log_level}")
        
        # Server
        if host := os.getenv("HOST"):
            self.config.host = host
        if port := os.getenv("PORT"):
            try:
                self.config.port = int(port)
            except ValueError:
                logger.warning(f"Invalid port: {port}")
        if workers := os.getenv("WORKERS"):
            try:
                self.config.workers = int(workers)
            except ValueError:
                logger.warning(f"Invalid workers: {workers}")
        
        # Database
        if db_url := os.getenv("DATABASE_URL"):
            self.config.database.url = db_url
        
        # Redis
        if redis_host := os.getenv("REDIS_HOST"):
            self.config.redis.host = redis_host
        if redis_port := os.getenv("REDIS_PORT"):
            try:
                self.config.redis.port = int(redis_port)
            except ValueError:
                logger.warning(f"Invalid Redis port: {redis_port}")
        if redis_password := os.getenv("REDIS_PASSWORD"):
            self.config.redis.password = redis_password
        
        # Security
        if secret_key := os.getenv("SECRET_KEY"):
            self.config.security.secret_key = secret_key
        
        # Gemini
        if gemini_api_key := os.getenv("GEMINI_API_KEY"):
            self.config.gemini.api_key = gemini_api_key
        if gemini_model := os.getenv("GEMINI_MODEL"):
            self.config.gemini.model = gemini_model
        if gemini_temperature := os.getenv("GEMINI_TEMPERATURE"):
            try:
                self.config.gemini.temperature = float(gemini_temperature)
            except ValueError:
                logger.warning(f"Invalid Gemini temperature: {gemini_temperature}")
        if gemini_max_tokens := os.getenv("GEMINI_MAX_TOKENS"):
            try:
                self.config.gemini.max_tokens = int(gemini_max_tokens)
            except ValueError:
                logger.warning(f"Invalid Gemini max tokens: {gemini_max_tokens}")
        
        # CORS
        if cors_origins := os.getenv("CORS_ORIGINS"):
            self.config.cors.allow_origins = [origin.strip() for origin in cors_origins.split(",")]
        
        # Trusted hosts
        if trusted_hosts := os.getenv("TRUSTED_HOSTS"):
            self.config.trusted_hosts = [host.strip() for host in trusted_hosts.split(",")]
    
    def get_config(self) -> AdvancedConfig:
        """Get current configuration."""
        return self.config
    
    def save_config(self, config_path: Optional[Path] = None):
        """Save configuration to file."""
        if not self.config:
            logger.error("No configuration to save")
            return
        
        save_path = config_path or self.config_path
        
        try:
            # Convert to dictionary
            config_dict = asdict(self.config)
            
            # Convert enums to strings
            config_dict["environment"] = self.config.environment.value
            config_dict["log_level"] = self.config.log_level.value
            
            # Save to file
            with open(save_path, 'w') as f:
                if save_path.suffix == '.yaml' or save_path.suffix == '.yml':
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        if not self.config:
            issues.append("No configuration loaded")
            return issues
        
        # Validate required fields
        if not self.config.gemini.api_key:
            issues.append("Gemini API key is required")
        
        if self.config.port < 1 or self.config.port > 65535:
            issues.append("Invalid port number")
        
        if self.config.workers < 1:
            issues.append("Invalid number of workers")
        
        # Validate Gemini config
        if self.config.gemini.temperature < 0 or self.config.gemini.temperature > 2:
            issues.append("Gemini temperature must be between 0 and 2")
        
        if self.config.gemini.max_tokens < 1:
            issues.append("Gemini max tokens must be positive")
        
        # Validate security config
        if len(self.config.security.secret_key) < 32:
            issues.append("Secret key should be at least 32 characters")
        
        return issues
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        if not self.config:
            return {}
        
        base_config = asdict(self.config)
        
        # Environment-specific overrides
        if self.config.environment == Environment.PRODUCTION:
            base_config["debug"] = False
            base_config["log_level"] = LogLevel.INFO.value
            base_config["monitoring"]["enable_metrics"] = True
            base_config["cache"]["enable_cache"] = True
            base_config["rate_limit"]["enable_rate_limiting"] = True
        elif self.config.environment == Environment.DEVELOPMENT:
            base_config["debug"] = True
            base_config["log_level"] = LogLevel.DEBUG.value
            base_config["monitoring"]["enable_metrics"] = False
        elif self.config.environment == Environment.TESTING:
            base_config["debug"] = True
            base_config["log_level"] = LogLevel.WARNING.value
            base_config["database"]["url"] = "sqlite:///./test.db"
        
        return base_config

# Global config manager instance
config_manager = AdvancedConfigManager()

def get_config() -> AdvancedConfig:
    """Get global configuration."""
    return config_manager.get_config()

def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration."""
    return config_manager.get_environment_config()