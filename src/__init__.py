"""
OpenManus-Youtu Integrated Framework

A fully integrated AI Agent platform that combines the power of OpenManus and Youtu-Agent.
"""

__version__ = "0.1.0"
__author__ = "OpenManus-Youtu Integration Team"
__email__ = "team@openmanus-youtu.dev"
__license__ = "MIT"

# Core imports
from .core.unified_agent import UnifiedAgent
from .core.config import UnifiedConfig
from .core.tool_registry import ToolRegistry
from .core.environment import EnvironmentManager
from .core.memory import UnifiedMemory
from .core.state import AgentState

# Agent types
from .agents.simple_agent import SimpleAgent
from .agents.orchestra_agent import OrchestraAgent
from .agents.browser_agent import BrowserAgent
from .agents.meta_agent import MetaAgent

# Tool categories
from .tools.web_tools import WebTools
from .tools.data_tools import DataTools
from .tools.analysis_tools import AnalysisTools

# Configuration
# from .config.loader import ConfigLoader  # Config loader not implemented yet
# from .config.validator import ConfigValidator  # Config validator not implemented yet

# Utilities
from .utils.logger import setup_logging
from .utils.exceptions import (
    UnifiedFrameworkError,
    AgentError,
    ToolError,
    ConfigError,
    EnvironmentError,
)

# Integration modules
from .integrations.openmanus import OpenManusIntegration
from .integrations.youtu import YoutuIntegration

__all__ = [
    # Core
    "UnifiedAgent",
    "UnifiedConfig", 
    "ToolRegistry",
    "EnvironmentManager",
    "UnifiedMemory",
    "AgentState",
    
    # Agents
    "SimpleAgent",
    "OrchestraAgent", 
    "BrowserAgent",
    "MetaAgent",
    
    # Tools
    "WebTools",
    "DataTools",
    "AnalysisTools",
    
    # Configuration
    "ConfigLoader",
    "ConfigValidator",
    
    # Utilities
    "setup_logging",
    
    # Exceptions
    "UnifiedFrameworkError",
    "AgentError",
    "ToolError", 
    "ConfigError",
    "EnvironmentError",
    
    # Integrations
    "OpenManusIntegration",
    "YoutuIntegration",
]