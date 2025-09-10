"""
Logging utilities for the unified framework.

This module provides centralized logging configuration and utilities
for consistent logging across the entire framework.
"""

import logging
import logging.config
import sys
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime

import colorlog
from rich.console import Console
from rich.logging import RichHandler


class ColoredFormatter(colorlog.ColoredFormatter):
    """Custom colored formatter for console output."""
    
    def __init__(self):
        super().__init__(
            fmt='%(log_color)s%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )


class FrameworkLogger:
    """Framework-specific logger with enhanced features."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """
        Initialize framework logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup log handlers."""
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # Rich handler for better formatting
        rich_handler = RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_path=False,
            markup=True
        )
        rich_handler.setFormatter(logging.Formatter(
            fmt='%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(rich_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context."""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {context}"
        return message


# Global logger registry
_loggers: Dict[str, FrameworkLogger] = {}


def get_logger(name: str, level: str = "INFO") -> FrameworkLogger:
    """
    Get or create a framework logger.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Framework logger instance
    """
    if name not in _loggers:
        _loggers[name] = FrameworkLogger(name, level)
    return _loggers[name]


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    config_file: Optional[str] = None
) -> None:
    """
    Setup global logging configuration.
    
    Args:
        level: Global logging level
        log_file: Optional log file path
        log_format: Optional custom log format
        config_file: Optional logging config file
    """
    if config_file and Path(config_file).exists():
        # Load from config file
        logging.config.fileConfig(config_file)
        return
    
    # Default configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'colored': {
                '()': ColoredFormatter,
            },
            'detailed': {
                'format': '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'colored',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console'],
                'level': level,
                'propagate': False
            }
        }
    }
    
    # Add file handler if specified
    if log_file:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level,
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        config['loggers']['']['handlers'].append('file')
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Set framework loggers
    for logger_name in _loggers:
        _loggers[logger_name].level = level


def set_log_level(level: str) -> None:
    """
    Set global log level.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger().setLevel(getattr(logging, level.upper()))
    
    # Update framework loggers
    for logger in _loggers.values():
        logger.level = level


def add_file_handler(
    log_file: str,
    level: str = "INFO",
    max_bytes: int = 10485760,
    backup_count: int = 5
) -> None:
    """
    Add file handler to all loggers.
    
    Args:
        log_file: Log file path
        level: Logging level
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep
    """
    from logging.handlers import RotatingFileHandler
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Add to root logger
    logging.getLogger().addHandler(file_handler)


def log_function_call(func_name: str, args: tuple, kwargs: dict, result: Any = None):
    """
    Log function call details.
    
    Args:
        func_name: Function name
        args: Function arguments
        kwargs: Function keyword arguments
        result: Function result
    """
    logger = get_logger("function_calls")
    
    # Format arguments
    args_str = ", ".join(str(arg) for arg in args)
    kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    
    if args_str and kwargs_str:
        call_str = f"{func_name}({args_str}, {kwargs_str})"
    elif args_str:
        call_str = f"{func_name}({args_str})"
    elif kwargs_str:
        call_str = f"{func_name}({kwargs_str})"
    else:
        call_str = f"{func_name}()"
    
    logger.debug(f"Call: {call_str}")
    
    if result is not None:
        logger.debug(f"Result: {result}")


def log_performance(operation: str, duration: float, **kwargs):
    """
    Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional metrics
    """
    logger = get_logger("performance")
    
    metrics = {
        "operation": operation,
        "duration": f"{duration:.3f}s",
        **kwargs
    }
    
    logger.info(f"Performance: {operation} took {duration:.3f}s", **metrics)


def log_error_with_context(
    error: Exception,
    context: Dict[str, Any],
    logger_name: str = "error_context"
):
    """
    Log error with additional context.
    
    Args:
        error: Exception instance
        context: Additional context
        logger_name: Logger name
    """
    logger = get_logger(logger_name)
    
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **context
    }
    
    logger.error(f"Error occurred: {error}", **error_info)


class LogContext:
    """Context manager for adding context to log messages."""
    
    def __init__(self, **context):
        """
        Initialize log context.
        
        Args:
            **context: Context variables
        """
        self.context = context
        self.old_context = {}
    
    def __enter__(self):
        """Enter context."""
        # Store old context
        for key in self.context:
            if hasattr(logging, key):
                self.old_context[key] = getattr(logging, key)
        
        # Set new context
        for key, value in self.context.items():
            setattr(logging, key, value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        # Restore old context
        for key, value in self.old_context.items():
            setattr(logging, key, value)


def create_logger_config(
    level: str = "INFO",
    log_file: Optional[str] = None,
    include_rich: bool = True
) -> Dict[str, Any]:
    """
    Create logging configuration dictionary.
    
    Args:
        level: Logging level
        log_file: Optional log file path
        include_rich: Whether to include Rich handler
        
    Returns:
        Logging configuration dictionary
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'colored': {
                '()': ColoredFormatter,
            },
            'detailed': {
                'format': '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'colored',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': level,
                'propagate': False
            }
        }
    }
    
    # Add Rich handler if requested
    if include_rich:
        config['handlers']['rich'] = {
            'class': 'rich.logging.RichHandler',
            'level': level,
            'formatter': 'standard',
            'console': 'rich.console.Console(stderr=True)',
            'show_time': True,
            'show_path': False,
            'markup': True
        }
        config['loggers']['']['handlers'].append('rich')
    
    # Add file handler if specified
    if log_file:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level,
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,
            'backupCount': 5
        }
        config['loggers']['']['handlers'].append('file')
    
    return config