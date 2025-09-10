"""
Advanced API Endpoints for OpenManus-Youtu Integrated Framework
Enhanced endpoints with monitoring, health checks, and system management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, List, Optional
import asyncio
import json
import time
import psutil
import os
from datetime import datetime, timedelta
from pathlib import Path

# from ..core.advanced_config import get_config, get_environment_config
# from ..utils.logger import get_logger
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# System metrics storage
system_metrics = {
    "start_time": datetime.now(),
    "request_count": 0,
    "error_count": 0,
    "response_times": [],
    "active_connections": 0
}

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        config = get_config()
        
        # Basic system health
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - system_metrics["start_time"]),
            "version": "1.0.0",
            "environment": config.environment.value
        }
        
        # System resources
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status["system"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            health_status["system"] = {"error": "Unable to retrieve system metrics"}
        
        # Application metrics
        health_status["application"] = {
            "request_count": system_metrics["request_count"],
            "error_count": system_metrics["error_count"],
            "active_connections": system_metrics["active_connections"],
            "average_response_time": sum(system_metrics["response_times"]) / len(system_metrics["response_times"]) if system_metrics["response_times"] else 0
        }
        
        # Gemini API health
        try:
            from ..ai.gemini_client import GeminiClient, GeminiConfig, GeminiModel, GeminiMessage
            
            gemini_config = GeminiConfig(
                api_key=config.gemini.api_key,
                model=config.gemini.model,
                temperature=0.1,
                max_tokens=10
            )
            
            client = GeminiClient(gemini_config)
            await client.initialize()
            
            # Quick test message
            test_message = GeminiMessage(
                role="user",
                parts=[{"text": "test"}],
                timestamp=datetime.now()
            )
            
            response_chunks = []
            async for chunk in client.generate_content([test_message], stream=False):
                response_chunks.append(chunk)
            
            await client.close()
            
            health_status["gemini"] = {
                "status": "healthy",
                "model": config.gemini.model,
                "response_time": "< 1s"
            }
            
        except Exception as e:
            health_status["gemini"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Overall health determination
        if health_status["gemini"]["status"] != "healthy":
            health_status["status"] = "degraded"
        
        if health_status["system"].get("cpu_percent", 0) > 90 or health_status["system"].get("memory_percent", 0) > 90:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    try:
        config = get_config()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "used": disk.used,
                    "percent": disk.percent
                }
            },
            "process": {
                "pid": process.pid,
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            },
            "application": {
                "uptime": str(datetime.now() - system_metrics["start_time"]),
                "request_count": system_metrics["request_count"],
                "error_count": system_metrics["error_count"],
                "active_connections": system_metrics["active_connections"],
                "response_times": {
                    "min": min(system_metrics["response_times"]) if system_metrics["response_times"] else 0,
                    "max": max(system_metrics["response_times"]) if system_metrics["response_times"] else 0,
                    "avg": sum(system_metrics["response_times"]) / len(system_metrics["response_times"]) if system_metrics["response_times"] else 0,
                    "count": len(system_metrics["response_times"])
                }
            },
            "configuration": {
                "environment": config.environment.value,
                "debug": config.debug,
                "log_level": config.log_level.value,
                "host": config.host,
                "port": config.port,
                "workers": config.workers
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Get system status."""
    try:
        config = get_config()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "version": "1.0.0",
            "environment": config.environment.value,
            "uptime": str(datetime.now() - system_metrics["start_time"]),
            "features": {
                "gemini_integration": True,
                "function_calling": config.gemini.enable_function_calling,
                "streaming": config.gemini.enable_streaming,
                "monitoring": config.monitoring.enable_metrics,
                "caching": config.cache.enable_cache,
                "rate_limiting": config.rate_limit.enable_rate_limiting
            },
            "endpoints": {
                "api_docs": "/docs",
                "health_check": "/health",
                "metrics": "/metrics",
                "gemini_agents": "/api/v1/agents",
                "system_status": "/status"
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_configuration():
    """Get current configuration (without sensitive data)."""
    try:
        config = get_config()
        
        # Create safe config without sensitive data
        safe_config = {
            "environment": config.environment.value,
            "debug": config.debug,
            "log_level": config.log_level.value,
            "host": config.host,
            "port": config.port,
            "workers": config.workers,
            "gemini": {
                "model": config.gemini.model,
                "temperature": config.gemini.temperature,
                "max_tokens": config.gemini.max_tokens,
                "timeout": config.gemini.timeout,
                "retry_attempts": config.gemini.retry_attempts,
                "enable_function_calling": config.gemini.enable_function_calling,
                "enable_streaming": config.gemini.enable_streaming,
                "base_url": config.gemini.base_url
            },
            "monitoring": {
                "enable_metrics": config.monitoring.enable_metrics,
                "metrics_port": config.monitoring.metrics_port,
                "enable_health_checks": config.monitoring.enable_health_checks,
                "health_check_interval": config.monitoring.health_check_interval
            },
            "cache": {
                "enable_cache": config.cache.enable_cache,
                "cache_ttl": config.cache.cache_ttl,
                "max_cache_size": config.cache.max_cache_size,
                "cache_backend": config.cache.cache_backend
            },
            "rate_limit": {
                "enable_rate_limiting": config.rate_limit.enable_rate_limiting,
                "requests_per_minute": config.rate_limit.requests_per_minute,
                "burst_size": config.rate_limit.burst_size,
                "window_size": config.rate_limit.window_size
            }
        }
        
        return safe_config
        
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(limit: int = 100, level: Optional[str] = None):
    """Get application logs."""
    try:
        # This is a simplified log retrieval
        # In production, you'd want to integrate with proper logging systems
        
        logs = []
        log_file = Path("logs/app.log")
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
                # Filter by level if specified
                if level:
                    lines = [line for line in lines if level.upper() in line]
                
                # Get last N lines
                lines = lines[-limit:] if len(lines) > limit else lines
                
                for line in lines:
                    logs.append({
                        "timestamp": line[:23] if len(line) > 23 else "",
                        "level": line[24:29].strip() if len(line) > 29 else "",
                        "message": line[30:].strip() if len(line) > 30 else line.strip()
                    })
        
        return {
            "logs": logs,
            "count": len(logs),
            "limit": limit,
            "level_filter": level
        }
        
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/restart")
async def restart_system(background_tasks: BackgroundTasks):
    """Restart the system (graceful shutdown)."""
    try:
        config = get_config()
        
        if config.environment.value != "development":
            raise HTTPException(status_code=403, detail="Restart only allowed in development environment")
        
        # Schedule restart
        background_tasks.add_task(restart_application)
        
        return {
            "message": "System restart scheduled",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to restart system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def restart_application():
    """Restart the application."""
    import os
    import signal
    
    logger.info("Restarting application...")
    await asyncio.sleep(2)  # Give time for response
    os.kill(os.getpid(), signal.SIGTERM)

@router.get("/system/info")
async def get_system_info():
    """Get detailed system information."""
    try:
        config = get_config()
        
        # Python info
        import sys
        python_info = {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro
            },
            "executable": sys.executable,
            "platform": sys.platform
        }
        
        # Package info
        try:
            import pkg_resources
            packages = []
            for dist in pkg_resources.working_set:
                packages.append({
                    "name": dist.project_name,
                    "version": dist.version
                })
        except Exception:
            packages = []
        
        # Environment info
        env_info = {
            "PATH": os.environ.get("PATH", "").split(":")[:5],  # First 5 paths
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV", ""),
            "USER": os.environ.get("USER", ""),
            "HOME": os.environ.get("HOME", "")
        }
        
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "python": python_info,
            "packages": packages[:20],  # First 20 packages
            "environment": env_info,
            "configuration": {
                "config_file": str(config_manager.config_path) if hasattr(config_manager, 'config_path') else "default",
                "environment": config.environment.value,
                "debug": config.debug
            }
        }
        
        return system_info
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Middleware to track requests
@router.middleware("http")
async def track_requests(request: Request, call_next):
    """Track request metrics."""
    start_time = time.time()
    
    # Increment request count
    system_metrics["request_count"] += 1
    
    try:
        response = await call_next(request)
        
        # Track response time
        response_time = time.time() - start_time
        system_metrics["response_times"].append(response_time)
        
        # Keep only last 1000 response times
        if len(system_metrics["response_times"]) > 1000:
            system_metrics["response_times"] = system_metrics["response_times"][-1000:]
        
        return response
        
    except Exception as e:
        # Track errors
        system_metrics["error_count"] += 1
        logger.error(f"Request error: {e}")
        raise