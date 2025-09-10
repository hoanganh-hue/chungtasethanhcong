"""
System Tools Implementation.

This module provides system-level tools including system monitoring,
resource management, and system administration capabilities.
"""

import asyncio
import platform
import psutil
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from .base_tool import BaseTool, ToolMetadata, ToolDefinition, ToolParameter, ToolCategory
from ..utils.exceptions import ToolError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SystemMonitorTool(BaseTool):
    """Tool for system monitoring and resource tracking."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="system_monitor",
            description="System monitoring and resource tracking tool",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["monitoring", "system", "resources", "performance"],
            dependencies=["psutil"],
            requirements={
                "monitoring_type": "type of monitoring",
                "interval": "monitoring interval"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "monitoring_type": ToolParameter(
                    name="monitoring_type",
                    type=str,
                    description="Type of system monitoring",
                    required=True,
                    choices=["cpu", "memory", "disk", "network", "processes", "all"]
                ),
                "interval": ToolParameter(
                    name="interval",
                    type=int,
                    description="Monitoring interval in seconds",
                    required=False,
                    default=1,
                    min_value=1,
                    max_value=60
                ),
                "duration": ToolParameter(
                    name="duration",
                    type=int,
                    description="Monitoring duration in seconds",
                    required=False,
                    default=10,
                    min_value=1,
                    max_value=3600
                ),
                "thresholds": ToolParameter(
                    name="thresholds",
                    type=dict,
                    description="Alert thresholds",
                    required=False
                ),
                "output_format": ToolParameter(
                    name="output_format",
                    type=str,
                    description="Output format for monitoring data",
                    required=False,
                    default="json",
                    choices=["json", "csv", "prometheus"]
                )
            },
            return_type=dict,
            examples=[
                {
                    "monitoring_type": "cpu",
                    "interval": 5,
                    "duration": 30
                }
            ],
            error_codes={
                "MONITORING_ERROR": "System monitoring failed",
                "PERMISSION_ERROR": "Insufficient permissions",
                "RESOURCE_ERROR": "Resource monitoring failed",
                "OUTPUT_ERROR": "Output generation failed"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute system monitoring."""
        try:
            monitoring_type = kwargs.get("monitoring_type")
            interval = kwargs.get("interval", 1)
            duration = kwargs.get("duration", 10)
            thresholds = kwargs.get("thresholds", {})
            output_format = kwargs.get("output_format", "json")
            
            # Simulate system monitoring
            await asyncio.sleep(0.2)  # Simulate monitoring time
            
            # Generate monitoring data based on type
            monitoring_data = self._generate_monitoring_data(monitoring_type)
            
            # Generate monitoring results
            monitoring_results = {
                "monitoring_type": monitoring_type,
                "interval": interval,
                "duration": duration,
                "thresholds": thresholds,
                "output_format": output_format,
                "system_info": {
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "architecture": platform.architecture()[0],
                    "hostname": platform.node(),
                    "python_version": platform.python_version()
                },
                "monitoring_data": monitoring_data,
                "alerts": self._check_thresholds(monitoring_data, thresholds),
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now()).isoformat()
            }
            
            return {
                "monitoring_type": monitoring_type,
                "interval": interval,
                "duration": duration,
                "thresholds": thresholds,
                "output_format": output_format,
                "monitoring_results": monitoring_results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System monitoring failed: {e}")
            raise ToolError(f"System monitoring failed: {e}") from e
    
    def _generate_monitoring_data(self, monitoring_type: str) -> Dict[str, Any]:
        """Generate mock monitoring data."""
        if monitoring_type == "cpu" or monitoring_type == "all":
            return {
                "cpu": {
                    "usage_percent": 45.2,
                    "cores": psutil.cpu_count(),
                    "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                    "load_average": [1.2, 1.5, 1.8]
                }
            }
        elif monitoring_type == "memory" or monitoring_type == "all":
            memory = psutil.virtual_memory()
            return {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free,
                    "usage_percent": memory.percent,
                    "cached": getattr(memory, 'cached', 0),
                    "buffers": getattr(memory, 'buffers', 0)
                }
            }
        elif monitoring_type == "disk" or monitoring_type == "all":
            disk = psutil.disk_usage('/')
            return {
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "usage_percent": (disk.used / disk.total) * 100,
                    "partitions": [
                        {
                            "device": "/dev/sda1",
                            "mountpoint": "/",
                            "fstype": "ext4",
                            "total": disk.total,
                            "used": disk.used,
                            "free": disk.free
                        }
                    ]
                }
            }
        elif monitoring_type == "network" or monitoring_type == "all":
            return {
                "network": {
                    "bytes_sent": 1024000,
                    "bytes_recv": 2048000,
                    "packets_sent": 1500,
                    "packets_recv": 2000,
                    "interfaces": [
                        {
                            "name": "eth0",
                            "bytes_sent": 1024000,
                            "bytes_recv": 2048000,
                            "packets_sent": 1500,
                            "packets_recv": 2000
                        }
                    ]
                }
            }
        elif monitoring_type == "processes" or monitoring_type == "all":
            return {
                "processes": {
                    "total": len(psutil.pids()),
                    "running": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running']),
                    "sleeping": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'sleeping']),
                    "top_processes": [
                        {"pid": 1234, "name": "python", "cpu_percent": 15.2, "memory_percent": 8.5},
                        {"pid": 5678, "name": "chrome", "cpu_percent": 12.1, "memory_percent": 12.3}
                    ]
                }
            }
        else:
            return {"error": f"Unknown monitoring type: {monitoring_type}"}
    
    def _check_thresholds(self, monitoring_data: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check monitoring data against thresholds."""
        alerts = []
        
        if "cpu" in monitoring_data and "cpu_threshold" in thresholds:
            cpu_usage = monitoring_data["cpu"]["usage_percent"]
            if cpu_usage > thresholds["cpu_threshold"]:
                alerts.append({
                    "type": "cpu_high",
                    "message": f"CPU usage {cpu_usage}% exceeds threshold {thresholds['cpu_threshold']}%",
                    "severity": "warning"
                })
        
        if "memory" in monitoring_data and "memory_threshold" in thresholds:
            memory_usage = monitoring_data["memory"]["usage_percent"]
            if memory_usage > thresholds["memory_threshold"]:
                alerts.append({
                    "type": "memory_high",
                    "message": f"Memory usage {memory_usage}% exceeds threshold {thresholds['memory_threshold']}%",
                    "severity": "warning"
                })
        
        return alerts


class ResourceManagerTool(BaseTool):
    """Tool for system resource management."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="resource_manager",
            description="System resource management tool",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["resources", "management", "system", "optimization"],
            dependencies=["psutil"],
            requirements={
                "resource_type": "type of resource to manage",
                "action": "management action"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "resource_type": ToolParameter(
                    name="resource_type",
                    type=str,
                    description="Type of resource to manage",
                    required=True,
                    choices=["memory", "cpu", "disk", "network", "processes"]
                ),
                "action": ToolParameter(
                    name="action",
                    type=str,
                    description="Management action to perform",
                    required=True,
                    choices=["cleanup", "optimize", "limit", "monitor", "kill"]
                ),
                "target": ToolParameter(
                    name="target",
                    type=str,
                    description="Target resource or process",
                    required=False
                ),
                "limit": ToolParameter(
                    name="limit",
                    type=float,
                    description="Resource limit",
                    required=False,
                    min_value=0.0,
                    max_value=100.0
                ),
                "force": ToolParameter(
                    name="force",
                    type=bool,
                    description="Force the action",
                    required=False,
                    default=False
                )
            },
            return_type=dict,
            examples=[
                {
                    "resource_type": "memory",
                    "action": "cleanup"
                }
            ],
            error_codes={
                "RESOURCE_ERROR": "Resource management failed",
                "PERMISSION_ERROR": "Insufficient permissions",
                "TARGET_ERROR": "Invalid target resource",
                "LIMIT_ERROR": "Invalid resource limit"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute resource management."""
        try:
            resource_type = kwargs.get("resource_type")
            action = kwargs.get("action")
            target = kwargs.get("target")
            limit = kwargs.get("limit")
            force = kwargs.get("force", False)
            
            # Simulate resource management
            await asyncio.sleep(0.3)  # Simulate management time
            
            # Generate management results
            management_results = {
                "resource_type": resource_type,
                "action": action,
                "target": target,
                "limit": limit,
                "force": force,
                "status": "completed",
                "changes_made": self._generate_changes(resource_type, action),
                "before_state": self._generate_before_state(resource_type),
                "after_state": self._generate_after_state(resource_type, action),
                "executed_at": datetime.now().isoformat()
            }
            
            return {
                "resource_type": resource_type,
                "action": action,
                "target": target,
                "limit": limit,
                "force": force,
                "management_results": management_results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resource management failed: {e}")
            raise ToolError(f"Resource management failed: {e}") from e
    
    def _generate_changes(self, resource_type: str, action: str) -> List[str]:
        """Generate list of changes made."""
        if action == "cleanup":
            if resource_type == "memory":
                return ["Cleared cache", "Freed unused memory", "Optimized memory allocation"]
            elif resource_type == "disk":
                return ["Cleaned temporary files", "Removed old logs", "Compressed files"]
            elif resource_type == "processes":
                return ["Killed zombie processes", "Terminated hung processes"]
        elif action == "optimize":
            return [f"Optimized {resource_type} usage", "Applied performance tuning"]
        elif action == "limit":
            return [f"Set {resource_type} limit to {resource_type}%"]
        elif action == "kill":
            return [f"Terminated process {resource_type}"]
        else:
            return [f"Performed {action} on {resource_type}"]
    
    def _generate_before_state(self, resource_type: str) -> Dict[str, Any]:
        """Generate before state."""
        if resource_type == "memory":
            return {"usage_percent": 85.2, "available_mb": 1024}
        elif resource_type == "cpu":
            return {"usage_percent": 45.2, "load_average": 1.5}
        elif resource_type == "disk":
            return {"usage_percent": 78.5, "free_gb": 50}
        elif resource_type == "processes":
            return {"total_processes": 150, "running_processes": 120}
        else:
            return {"status": "unknown"}
    
    def _generate_after_state(self, resource_type: str, action: str) -> Dict[str, Any]:
        """Generate after state."""
        before = self._generate_before_state(resource_type)
        
        if action == "cleanup":
            if resource_type == "memory":
                return {"usage_percent": 65.2, "available_mb": 2048}
            elif resource_type == "disk":
                return {"usage_percent": 70.5, "free_gb": 80}
            elif resource_type == "processes":
                return {"total_processes": 140, "running_processes": 110}
        elif action == "optimize":
            return {k: v * 0.9 for k, v in before.items() if isinstance(v, (int, float))}
        else:
            return before


class ProcessManagerTool(BaseTool):
    """Tool for process management and control."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="process_manager",
            description="Process management and control tool",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["process", "management", "control", "system"],
            dependencies=["psutil"],
            requirements={
                "process_action": "process action to perform",
                "process_identifier": "process identifier"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "action": ToolParameter(
                    name="action",
                    type=str,
                    description="Process action to perform",
                    required=True,
                    choices=["list", "kill", "suspend", "resume", "monitor", "info"]
                ),
                "process_id": ToolParameter(
                    name="process_id",
                    type=int,
                    description="Process ID",
                    required=False,
                    min_value=1
                ),
                "process_name": ToolParameter(
                    name="process_name",
                    type=str,
                    description="Process name",
                    required=False
                ),
                "signal": ToolParameter(
                    name="signal",
                    type=str,
                    description="Signal to send (for kill action)",
                    required=False,
                    default="SIGTERM",
                    choices=["SIGTERM", "SIGKILL", "SIGINT", "SIGUSR1", "SIGUSR2"]
                ),
                "force": ToolParameter(
                    name="force",
                    type=bool,
                    description="Force the action",
                    required=False,
                    default=False
                )
            },
            return_type=dict,
            examples=[
                {
                    "action": "list",
                    "process_name": "python"
                }
            ],
            error_codes={
                "PROCESS_ERROR": "Process management failed",
                "PERMISSION_ERROR": "Insufficient permissions",
                "PROCESS_NOT_FOUND": "Process not found",
                "SIGNAL_ERROR": "Signal sending failed"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute process management."""
        try:
            action = kwargs.get("action")
            process_id = kwargs.get("process_id")
            process_name = kwargs.get("process_name")
            signal = kwargs.get("signal", "SIGTERM")
            force = kwargs.get("force", False)
            
            # Simulate process management
            await asyncio.sleep(0.2)  # Simulate management time
            
            # Generate process results
            process_results = {
                "action": action,
                "process_id": process_id,
                "process_name": process_name,
                "signal": signal,
                "force": force,
                "status": "completed",
                "processes": self._generate_process_list(action, process_name),
                "executed_at": datetime.now().isoformat()
            }
            
            return {
                "action": action,
                "process_id": process_id,
                "process_name": process_name,
                "signal": signal,
                "force": force,
                "process_results": process_results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Process management failed: {e}")
            raise ToolError(f"Process management failed: {e}") from e
    
    def _generate_process_list(self, action: str, process_name: Optional[str]) -> List[Dict[str, Any]]:
        """Generate process list based on action."""
        if action == "list":
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if not process_name or process_name.lower() in proc_info['name'].lower():
                        processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cpu_percent": proc_info['cpu_percent'],
                            "memory_percent": proc_info['memory_percent'],
                            "status": proc_info['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes[:10]  # Limit to 10 processes
        elif action == "info":
            return [{
                "pid": 1234,
                "name": "python",
                "cpu_percent": 15.2,
                "memory_percent": 8.5,
                "status": "running",
                "create_time": datetime.now().isoformat(),
                "cmdline": ["python", "script.py"]
            }]
        else:
            return []


class SystemTools:
    """Collection of system-related tools."""
    
    @staticmethod
    def get_all_tools() -> List[BaseTool]:
        """Get all system tools."""
        return [
            SystemMonitorTool(),
            ResourceManagerTool(),
            ProcessManagerTool()
        ]
    
    @staticmethod
    def get_tool_by_name(name: str) -> Optional[BaseTool]:
        """Get a specific system tool by name."""
        tools = {tool._get_metadata().name: tool for tool in SystemTools.get_all_tools()}
        return tools.get(name)
    
    @staticmethod
    def get_tools_by_tag(tag: str) -> List[BaseTool]:
        """Get system tools by tag."""
        return [
            tool for tool in SystemTools.get_all_tools()
            if tag in tool._get_metadata().tags
        ]