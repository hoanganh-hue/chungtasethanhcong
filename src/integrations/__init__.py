"""
Integration modules for OpenManus and Youtu-Agent frameworks.

This package contains integration adapters and wrappers that allow
seamless integration between the unified framework and the original
OpenManus and Youtu-Agent frameworks.
"""

from .openmanus import OpenManusIntegration
from .youtu import YoutuIntegration

__all__ = [
    "OpenManusIntegration",
    "YoutuIntegration",
]