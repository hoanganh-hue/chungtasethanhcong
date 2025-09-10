"""
Agent implementations for the unified framework.

This package contains all agent types that can be used in the
OpenManus-Youtu Integrated Framework.
"""

from .simple_agent import SimpleAgent
from .browser_agent import BrowserAgent
from .orchestra_agent import OrchestraAgent, WorkflowStatus, TaskDependency
from .meta_agent import MetaAgent

__all__ = [
    "SimpleAgent",
    "BrowserAgent", 
    "OrchestraAgent",
    "MetaAgent",
    "WorkflowStatus",
    "TaskDependency",
]