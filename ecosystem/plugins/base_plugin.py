"""
Base Plugin System for OpenManus-Youtu Integrated Framework
Extensible plugin architecture for third-party integrations
"""

import asyncio
import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Plugin type enumeration."""
    AGENT = "agent"
    TOOL = "tool"
    INTEGRATION = "integration"
    MIDDLEWARE = "middleware"
    WORKFLOW = "workflow"
    CUSTOM = "custom"


class PluginStatus(Enum):
    """Plugin status enumeration."""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    LOADING = "loading"


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    requirements: List[str]
    entry_point: str
    config_schema: Dict[str, Any]
    status: PluginStatus = PluginStatus.INSTALLED


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, metadata: PluginMetadata, config: Dict[str, Any] = None):
        self.metadata = metadata
        self.config = config or {}
        self.status = PluginStatus.INSTALLED
        self.logger = logging.getLogger(f"plugin.{metadata.name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """Cleanup the plugin."""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality."""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
    
    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        if not self.metadata.config_schema:
            return True
        
        # Basic validation - in production, use JSON Schema
        for key, schema in self.metadata.config_schema.items():
            if schema.get("required", False) and key not in self.config:
                self.logger.error(f"Required config key missing: {key}")
                return False
        
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "type": self.metadata.plugin_type.value,
            "status": self.status.value,
            "config": self.config
        }


class PluginManager:
    """Plugin management system."""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    async def load_plugin(self, plugin_path: str, config: Dict[str, Any] = None) -> bool:
        """Load a plugin from path."""
        try:
            self.logger.info(f"Loading plugin from: {plugin_path}")
            
            # Import plugin module
            module = importlib.import_module(plugin_path)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                self.logger.error(f"No plugin class found in {plugin_path}")
                return False
            
            # Create plugin instance
            plugin = plugin_class(config or {})
            
            # Validate configuration
            if not plugin.validate_config():
                self.logger.error(f"Plugin configuration validation failed: {plugin.metadata.name}")
                return False
            
            # Initialize plugin
            if not await plugin.initialize():
                self.logger.error(f"Plugin initialization failed: {plugin.metadata.name}")
                return False
            
            # Register plugin
            self.plugins[plugin.metadata.name] = plugin
            self.plugin_metadata[plugin.metadata.name] = plugin.metadata
            plugin.status = PluginStatus.ENABLED
            
            self.logger.info(f"Plugin loaded successfully: {plugin.metadata.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            
            # Cleanup plugin
            await plugin.cleanup()
            
            # Remove from registry
            del self.plugins[plugin_name]
            del self.plugin_metadata[plugin_name]
            
            self.logger.info(f"Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            
            if plugin.status == PluginStatus.ENABLED:
                return True
            
            # Initialize if needed
            if plugin.status == PluginStatus.INSTALLED:
                if not await plugin.initialize():
                    plugin.status = PluginStatus.ERROR
                    return False
            
            plugin.status = PluginStatus.ENABLED
            self.logger.info(f"Plugin enabled: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable plugin {plugin_name}: {e}")
            return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.status = PluginStatus.DISABLED
            
            self.logger.info(f"Plugin disabled: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disable plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins."""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Get plugins by type."""
        return [
            plugin for plugin in self.plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]
    
    async def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Execute a plugin."""
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        if plugin.status != PluginStatus.ENABLED:
            raise ValueError(f"Plugin not enabled: {plugin_name}")
        
        try:
            return await plugin.execute(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Plugin execution failed {plugin_name}: {e}")
            raise
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
        self.logger.debug(f"Registered hook: {hook_name}")
    
    def unregister_hook(self, hook_name: str, callback: Callable):
        """Unregister a hook callback."""
        if hook_name in self.hooks:
            try:
                self.hooks[hook_name].remove(callback)
            except ValueError:
                pass
    
    async def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger a hook."""
        results = []
        
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        result = await callback(*args, **kwargs)
                    else:
                        result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Hook execution failed {hook_name}: {e}")
        
        return results
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """Register an event handler."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Registered event handler: {event_name}")
    
    async def emit_event(self, event_name: str, *args, **kwargs):
        """Emit an event."""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(*args, **kwargs)
                    else:
                        handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Event handler failed {event_name}: {e}")
    
    async def cleanup_all(self):
        """Cleanup all plugins."""
        for plugin_name in list(self.plugins.keys()):
            await self.unload_plugin(plugin_name)


# Global plugin manager
plugin_manager = PluginManager()