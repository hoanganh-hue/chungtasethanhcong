"""
Multi-Agent Orchestration System for OpenManus-Youtu Integrated Framework
Advanced orchestration capabilities for managing multiple AI agents
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class OrchestrationMode(Enum):
    """Orchestration execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    CONDITIONAL = "conditional"
    LOOP = "loop"

class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class AgentTask:
    """Individual agent task definition."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    task_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    timeout: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class OrchestrationPlan:
    """Orchestration execution plan."""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    mode: OrchestrationMode = OrchestrationMode.SEQUENTIAL
    tasks: List[AgentTask] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    max_concurrent: int = 5
    timeout: int = 3600
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"

class AgentOrchestrator:
    """Advanced multi-agent orchestration system."""
    
    def __init__(self, max_concurrent_agents: int = 10):
        self.max_concurrent_agents = max_concurrent_agents
        self.active_agents: Dict[str, AgentTask] = {}
        self.agent_registry: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._semaphore = asyncio.Semaphore(max_concurrent_agents)
        
    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """Register an agent for orchestration."""
        self.agent_registry[agent_id] = agent_instance
        logger.info(f"Registered agent: {agent_id}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add event handler for orchestration events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit orchestration event."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
    
    async def execute_plan(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute orchestration plan."""
        logger.info(f"Starting orchestration plan: {plan.name}")
        
        plan.status = "running"
        start_time = datetime.now()
        
        try:
            if plan.mode == OrchestrationMode.SEQUENTIAL:
                results = await self._execute_sequential(plan)
            elif plan.mode == OrchestrationMode.PARALLEL:
                results = await self._execute_parallel(plan)
            elif plan.mode == OrchestrationMode.PIPELINE:
                results = await self._execute_pipeline(plan)
            elif plan.mode == OrchestrationMode.CONDITIONAL:
                results = await self._execute_conditional(plan)
            elif plan.mode == OrchestrationMode.LOOP:
                results = await self._execute_loop(plan)
            else:
                raise ValueError(f"Unsupported orchestration mode: {plan.mode}")
            
            plan.status = "completed"
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "plan_id": plan.plan_id,
                "status": "completed",
                "execution_time": execution_time,
                "results": results,
                "success_count": len([r for r in results.values() if r.get("status") == "success"]),
                "total_tasks": len(plan.tasks)
            }
            
            await self._emit_event("plan_completed", result)
            return result
            
        except Exception as e:
            plan.status = "failed"
            logger.error(f"Orchestration plan failed: {e}")
            
            result = {
                "plan_id": plan.plan_id,
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
            
            await self._emit_event("plan_failed", result)
            return result
    
    async def _execute_sequential(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks sequentially."""
        results = {}
        
        for task in plan.tasks:
            result = await self._execute_task(task)
            results[task.task_id] = result
            
            # Check if task failed and should stop execution
            if result.get("status") == "failed" and not task.retry_count < task.max_retries:
                break
        
        return results
    
    async def _execute_parallel(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks in parallel."""
        semaphore = asyncio.Semaphore(plan.max_concurrent)
        
        async def execute_with_semaphore(task: AgentTask):
            async with semaphore:
                return await self._execute_task(task)
        
        tasks = [execute_with_semaphore(task) for task in plan.tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            task.task_id: result if not isinstance(result, Exception) else {"status": "failed", "error": str(result)}
            for task, result in zip(plan.tasks, results)
        }
    
    async def _execute_pipeline(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks in pipeline mode (output of one becomes input of next)."""
        results = {}
        pipeline_data = {}
        
        for task in plan.tasks:
            # Pass pipeline data to task parameters
            task.parameters.update(pipeline_data)
            
            result = await self._execute_task(task)
            results[task.task_id] = result
            
            # Extract output data for next task
            if result.get("status") == "success" and "output" in result:
                pipeline_data = result["output"]
        
        return results
    
    async def _execute_conditional(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks based on conditions."""
        results = {}
        
        for task in plan.tasks:
            # Check conditions
            if self._evaluate_conditions(task, results, plan.conditions):
                result = await self._execute_task(task)
                results[task.task_id] = result
            else:
                results[task.task_id] = {
                    "status": "skipped",
                    "reason": "Condition not met"
                }
        
        return results
    
    async def _execute_loop(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks in a loop."""
        results = {}
        loop_count = 0
        max_loops = plan.conditions.get("max_loops", 10)
        
        while loop_count < max_loops:
            loop_results = {}
            
            for task in plan.tasks:
                result = await self._execute_task(task)
                loop_results[task.task_id] = result
            
            results[f"loop_{loop_count}"] = loop_results
            loop_count += 1
            
            # Check loop exit condition
            if self._check_loop_exit_condition(loop_results, plan.conditions):
                break
        
        return results
    
    def _evaluate_conditions(self, task: AgentTask, results: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Evaluate task execution conditions."""
        if not task.dependencies:
            return True
        
        # Check if all dependencies are completed successfully
        for dep_id in task.dependencies:
            if dep_id not in results:
                return False
            if results[dep_id].get("status") != "success":
                return False
        
        return True
    
    def _check_loop_exit_condition(self, results: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Check if loop should exit."""
        exit_condition = conditions.get("exit_condition")
        if not exit_condition:
            return False
        
        # Simple condition evaluation (can be extended)
        if exit_condition.get("type") == "all_success":
            return all(r.get("status") == "success" for r in results.values())
        elif exit_condition.get("type") == "any_failure":
            return any(r.get("status") == "failed" for r in results.values())
        
        return False
    
    async def _execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute individual agent task."""
        task.status = AgentStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            if task.agent_id not in self.agent_registry:
                raise ValueError(f"Agent not found: {task.agent_id}")
            
            agent = self.agent_registry[task.agent_id]
            
            # Execute task with timeout
            result = await asyncio.wait_for(
                self._run_agent_task(agent, task),
                timeout=task.timeout
            )
            
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            await self._emit_event("task_completed", {
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "result": result
            })
            
            return {
                "status": "success",
                "result": result,
                "execution_time": (task.completed_at - task.started_at).total_seconds()
            }
            
        except asyncio.TimeoutError:
            task.status = AgentStatus.FAILED
            task.error = f"Task timeout after {task.timeout} seconds"
            
            return {
                "status": "failed",
                "error": task.error,
                "execution_time": task.timeout
            }
            
        except Exception as e:
            task.status = AgentStatus.FAILED
            task.error = str(e)
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = AgentStatus.IDLE
                logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count})")
                
                # Wait before retry
                await asyncio.sleep(2 ** task.retry_count)
                return await self._execute_task(task)
            
            return {
                "status": "failed",
                "error": str(e),
                "retry_count": task.retry_count
            }
    
    async def _run_agent_task(self, agent: Any, task: AgentTask) -> Any:
        """Run agent task (to be implemented by specific agents)."""
        # This is a placeholder - actual implementation depends on agent type
        if hasattr(agent, 'execute_task'):
            return await agent.execute_task(task.task_type, task.parameters)
        elif hasattr(agent, 'run'):
            return await agent.run(task.parameters)
        else:
            raise NotImplementedError(f"Agent {task.agent_id} does not support task execution")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an agent."""
        if agent_id in self.active_agents:
            task = self.active_agents[agent_id]
            return {
                "agent_id": agent_id,
                "status": task.status.value,
                "task_id": task.task_id,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "progress": self._calculate_progress(task)
            }
        return None
    
    def _calculate_progress(self, task: AgentTask) -> float:
        """Calculate task progress percentage."""
        if task.status == AgentStatus.COMPLETED:
            return 100.0
        elif task.status == AgentStatus.FAILED:
            return 0.0
        elif task.status == AgentStatus.RUNNING and task.started_at:
            elapsed = (datetime.now() - task.started_at).total_seconds()
            return min((elapsed / task.timeout) * 100, 99.0)
        return 0.0
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration system statistics."""
        return {
            "total_agents": len(self.agent_registry),
            "active_agents": len(self.active_agents),
            "max_concurrent": self.max_concurrent_agents,
            "execution_history_count": len(self.execution_history),
            "event_handlers": {event: len(handlers) for event, handlers in self.event_handlers.items()}
        }

# Global orchestrator instance
orchestrator = AgentOrchestrator()

# Convenience functions
async def execute_sequential_tasks(tasks: List[AgentTask]) -> Dict[str, Any]:
    """Execute tasks sequentially."""
    plan = OrchestrationPlan(
        name="Sequential Execution",
        mode=OrchestrationMode.SEQUENTIAL,
        tasks=tasks
    )
    return await orchestrator.execute_plan(plan)

async def execute_parallel_tasks(tasks: List[AgentTask], max_concurrent: int = 5) -> Dict[str, Any]:
    """Execute tasks in parallel."""
    plan = OrchestrationPlan(
        name="Parallel Execution",
        mode=OrchestrationMode.PARALLEL,
        tasks=tasks,
        max_concurrent=max_concurrent
    )
    return await orchestrator.execute_plan(plan)

async def execute_pipeline_tasks(tasks: List[AgentTask]) -> Dict[str, Any]:
    """Execute tasks in pipeline mode."""
    plan = OrchestrationPlan(
        name="Pipeline Execution",
        mode=OrchestrationMode.PIPELINE,
        tasks=tasks
    )
    return await orchestrator.execute_plan(plan)