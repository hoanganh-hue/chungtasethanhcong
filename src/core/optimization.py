"""
Performance Optimization Module for OpenManus-Youtu Integrated Framework
Advanced optimization techniques and performance enhancements
"""

import asyncio
import time
import psutil
import gc
from typing import Dict, Any, Optional, List
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import weakref
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data class."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    response_time: float
    throughput: float


class PerformanceOptimizer:
    """Advanced performance optimization system."""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_enabled = True
        self.auto_cleanup_interval = 300  # 5 minutes
        self.max_memory_usage = 80  # 80% memory threshold
        self.connection_pool_size = 100
        self.cache_size = 1000
        
    async def optimize_system(self):
        """Optimize system performance."""
        if not self.optimization_enabled:
            return
            
        logger.info("Starting system optimization...")
        
        # Memory optimization
        await self._optimize_memory()
        
        # Connection pool optimization
        await self._optimize_connections()
        
        # Cache optimization
        await self._optimize_cache()
        
        # Garbage collection
        await self._optimize_garbage_collection()
        
        logger.info("System optimization completed")
    
    async def _optimize_memory(self):
        """Optimize memory usage."""
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > self.max_memory_usage:
            logger.warning(f"High memory usage: {memory_percent}%")
            
            # Force garbage collection
            gc.collect()
            
            # Clear unused caches
            await self._clear_unused_caches()
            
            # Optimize object references
            await self._optimize_object_references()
    
    async def _optimize_connections(self):
        """Optimize connection pools."""
        # This would integrate with actual connection pools
        logger.debug("Optimizing connection pools...")
    
    async def _optimize_cache(self):
        """Optimize cache usage."""
        # Clear expired cache entries
        logger.debug("Optimizing cache...")
    
    async def _optimize_garbage_collection(self):
        """Optimize garbage collection."""
        # Force garbage collection for optimization
        collected = gc.collect()
        if collected > 0:
            logger.debug(f"Garbage collection freed {collected} objects")
    
    async def _clear_unused_caches(self):
        """Clear unused caches."""
        # Implementation for clearing unused caches
        pass
    
    async def _optimize_object_references(self):
        """Optimize object references."""
        # Implementation for optimizing object references
        pass


class AsyncOptimizer:
    """Async operation optimizer."""
    
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_with_optimization(self, coro, task_id: str = None):
        """Execute coroutine with optimization."""
        if task_id is None:
            task_id = f"task_{id(coro)}"
        
        async with self.semaphore:
            try:
                self.active_tasks[task_id] = asyncio.create_task(coro)
                result = await self.active_tasks[task_id]
                return result
            finally:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    async def batch_execute(self, coroutines: List, batch_size: int = 10):
        """Execute coroutines in batches for optimization."""
        results = []
        
        for i in range(0, len(coroutines), batch_size):
            batch = coroutines[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
            
            # Small delay between batches to prevent overwhelming
            await asyncio.sleep(0.01)
        
        return results


class MemoryOptimizer:
    """Memory usage optimizer."""
    
    def __init__(self):
        self.object_registry: Dict[str, weakref.ref] = {}
        self.cleanup_threshold = 1000
    
    def register_object(self, obj: Any, name: str = None):
        """Register object for memory tracking."""
        if name is None:
            name = f"obj_{id(obj)}"
        
        self.object_registry[name] = weakref.ref(obj)
        
        # Cleanup if too many objects
        if len(self.object_registry) > self.cleanup_threshold:
            self._cleanup_dead_references()
    
    def _cleanup_dead_references(self):
        """Clean up dead object references."""
        dead_refs = []
        
        for name, ref in self.object_registry.items():
            if ref() is None:
                dead_refs.append(name)
        
        for name in dead_refs:
            del self.object_registry[name]
        
        logger.debug(f"Cleaned up {len(dead_refs)} dead references")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": process.memory_percent(),
            "registered_objects": len(self.object_registry)
        }


class CacheOptimizer:
    """Cache optimization system."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        # Check TTL
        if datetime.now() - self.access_times[key] > timedelta(seconds=self.ttl):
            self.delete(key)
            return None
        
        # Update access time
        self.access_times[key] = datetime.now()
        return self.cache[key]["value"]
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        # Check cache size
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {"value": value, "created": datetime.now()}
        self.access_times[key] = datetime.now()
    
    def delete(self, key: str):
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def _evict_oldest(self):
        """Evict oldest cache entry."""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(oldest_key)
    
    def clear_expired(self):
        """Clear expired cache entries."""
        now = datetime.now()
        expired_keys = []
        
        for key, access_time in self.access_times.items():
            if now - access_time > timedelta(seconds=self.ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        logger.debug(f"Cleared {len(expired_keys)} expired cache entries")


def performance_monitor(func):
    """Decorator for performance monitoring."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            execution_time = end_time - start_time
            memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB
            
            logger.debug(
                f"{func.__name__}: {execution_time:.3f}s, "
                f"memory: {memory_delta:+.2f}MB"
            )
    
    return wrapper


def cached_async(maxsize: int = 128, ttl: int = 3600):
    """Async cache decorator."""
    def decorator(func):
        cache = {}
        access_times = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check cache
            if key in cache:
                if datetime.now() - access_times[key] < timedelta(seconds=ttl):
                    access_times[key] = datetime.now()
                    return cache[key]
                else:
                    # Expired
                    del cache[key]
                    del access_times[key]
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if len(cache) < maxsize:
                cache[key] = result
                access_times[key] = datetime.now()
            
            return result
        
        return wrapper
    return decorator


class ResourceManager:
    """Advanced resource management system."""
    
    def __init__(self):
        self.resources: Dict[str, Any] = {}
        self.resource_limits: Dict[str, int] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_resource(self, name: str, resource: Any, limit: int = None):
        """Register a resource."""
        self.resources[name] = resource
        if limit:
            self.resource_limits[name] = limit
        self.usage_stats[name] = {
            "created": datetime.now(),
            "access_count": 0,
            "last_access": None
        }
    
    def get_resource(self, name: str) -> Optional[Any]:
        """Get a resource."""
        if name not in self.resources:
            return None
        
        # Update usage stats
        self.usage_stats[name]["access_count"] += 1
        self.usage_stats[name]["last_access"] = datetime.now()
        
        return self.resources[name]
    
    def cleanup_unused_resources(self, max_age_hours: int = 24):
        """Cleanup unused resources."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        unused_resources = []
        
        for name, stats in self.usage_stats.items():
            if stats["last_access"] and stats["last_access"] < cutoff_time:
                unused_resources.append(name)
        
        for name in unused_resources:
            if hasattr(self.resources[name], 'cleanup'):
                self.resources[name].cleanup()
            del self.resources[name]
            del self.usage_stats[name]
        
        logger.info(f"Cleaned up {len(unused_resources)} unused resources")


# Global optimization instances
performance_optimizer = PerformanceOptimizer()
async_optimizer = AsyncOptimizer()
memory_optimizer = MemoryOptimizer()
cache_optimizer = CacheOptimizer()
resource_manager = ResourceManager()


async def initialize_optimization():
    """Initialize optimization systems."""
    logger.info("Initializing optimization systems...")
    
    # Start background optimization task
    asyncio.create_task(_background_optimization())
    
    logger.info("Optimization systems initialized")


async def _background_optimization():
    """Background optimization task."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await performance_optimizer.optimize_system()
            cache_optimizer.clear_expired()
            resource_manager.cleanup_unused_resources()
        except Exception as e:
            logger.error(f"Background optimization error: {e}")


def get_system_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics."""
    process = psutil.Process()
    
    return {
        "cpu": {
            "percent": psutil.cpu_percent(),
            "count": psutil.cpu_count(),
            "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        },
        "memory": {
            "total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            "available": psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
            "percent": psutil.virtual_memory().percent,
            "process_rss": process.memory_info().rss / 1024 / 1024,  # MB
            "process_vms": process.memory_info().vms / 1024 / 1024,  # MB
        },
        "disk": {
            "total": psutil.disk_usage('/').total / 1024 / 1024 / 1024,  # GB
            "used": psutil.disk_usage('/').used / 1024 / 1024 / 1024,  # GB
            "free": psutil.disk_usage('/').free / 1024 / 1024 / 1024,  # GB
            "percent": psutil.disk_usage('/').percent
        },
        "network": {
            "connections": len(psutil.net_connections()),
            "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        },
        "optimization": {
            "cache_size": len(cache_optimizer.cache),
            "registered_objects": len(memory_optimizer.object_registry),
            "active_resources": len(resource_manager.resources)
        }
    }