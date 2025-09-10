"""
Orchestra Agent Implementation.

This module provides the OrchestraAgent class, which is designed for
multi-agent coordination and workflow management.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum

from ..core.unified_agent import UnifiedAgent
from ..core.config import UnifiedConfig
from ..core.tool_registry import BaseTool
from ..core.memory import UnifiedMemory
from ..core.state import AgentState
from ..utils.exceptions import AgentError, OrchestrationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskDependency(Enum):
    """Task dependency types."""
    SEQUENTIAL = "sequential"  # Tasks must run in order
    PARALLEL = "parallel"      # Tasks can run simultaneously
    CONDITIONAL = "conditional"  # Tasks depend on conditions


class OrchestraAgent(UnifiedAgent):
    """
    Orchestra Agent for multi-agent coordination.
    
    This agent is designed to coordinate multiple agents, manage workflows,
    and orchestrate complex multi-step tasks across different agent types.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: UnifiedConfig,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[UnifiedMemory] = None,
        state: Optional[AgentState] = None,
        max_concurrent_agents: int = 5,
        workflow_timeout: int = 1800,
        retry_attempts: int = 3
    ):
        """
        Initialize the Orchestra Agent.
        
        Args:
            name: Agent name
            description: Agent description
            config: Agent configuration
            tools: List of available tools
            memory: Memory system instance
            state: Agent state instance
            max_concurrent_agents: Maximum number of concurrent agents
            workflow_timeout: Workflow execution timeout in seconds
            retry_attempts: Number of retry attempts for failed tasks
        """
        super().__init__(name, description, config, tools, memory, state)
        
        self.max_concurrent_agents = max_concurrent_agents
        self.workflow_timeout = workflow_timeout
        self.retry_attempts = retry_attempts
        
        # Orchestration state
        self.managed_agents: Dict[str, UnifiedAgent] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        self.task_queue: List[Dict[str, Any]] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info(f"OrchestraAgent '{name}' initialized with max_concurrent={max_concurrent_agents}")
    
    async def _setup_agent_specific(self) -> None:
        """Setup Orchestra Agent specific components."""
        try:
            logger.info(f"Setting up OrchestraAgent '{self.name}' specific components...")
            
            # Initialize orchestration pipeline
            self.orchestration_pipeline = [
                "parse_workflow",
                "validate_workflow",
                "schedule_tasks",
                "execute_workflow",
                "monitor_progress",
                "collect_results",
                "cleanup_workflow"
            ]
            
            # Setup orchestration tools
            await self._setup_orchestration_tools()
            
            # Initialize task scheduler
            await self._initialize_task_scheduler()
            
            logger.info(f"OrchestraAgent '{self.name}' specific setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup OrchestraAgent '{self.name}' specific components: {e}")
            raise AgentError(f"OrchestraAgent setup failed: {e}") from e
    
    async def _setup_orchestration_tools(self) -> None:
        """Setup orchestration-specific tools."""
        try:
            # Add orchestration tools to the agent
            orchestration_tools = [
                "agent_coordinator",
                "workflow_manager",
                "task_distributor",
                "result_aggregator"
            ]
            
            for tool_name in orchestration_tools:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    self.tools.append(tool)
            
            logger.info(f"OrchestraAgent '{self.name}' setup {len(orchestration_tools)} orchestration tools")
            
        except Exception as e:
            logger.error(f"Failed to setup orchestration tools: {e}")
            raise AgentError(f"Orchestration tools setup failed: {e}") from e
    
    async def _initialize_task_scheduler(self) -> None:
        """Initialize the task scheduler."""
        try:
            self.task_scheduler = {
                "max_concurrent": self.max_concurrent_agents,
                "current_running": 0,
                "queue_size": 0,
                "scheduler_status": "initialized"
            }
            
            logger.info(f"OrchestraAgent '{self.name}' task scheduler initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize task scheduler: {e}")
            raise AgentError(f"Task scheduler initialization failed: {e}") from e
    
    async def _execute_task(self, task: str, **kwargs) -> Any:
        """
        Execute an orchestration task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Orchestration result
        """
        try:
            logger.info(f"OrchestraAgent '{self.name}' executing orchestration task: {task}")
            
            # Parse orchestration task
            orchestration_task = await self._parse_orchestration_task(task, **kwargs)
            
            # Execute orchestration pipeline
            result = await self._execute_orchestration_pipeline(orchestration_task)
            
            return result
            
        except Exception as e:
            logger.error(f"OrchestraAgent '{self.name}' task execution failed: {e}")
            raise AgentError(f"Orchestration task execution failed: {e}") from e
    
    async def _parse_orchestration_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Parse orchestration task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Parsed orchestration task information
        """
        try:
            task_lower = task.lower()
            
            # Determine orchestration type
            if any(keyword in task_lower for keyword in ["coordinate", "manage", "orchestrate"]):
                orchestration_type = "coordination"
            elif any(keyword in task_lower for keyword in ["workflow", "pipeline", "sequence"]):
                orchestration_type = "workflow"
            elif any(keyword in task_lower for keyword in ["parallel", "concurrent", "simultaneous"]):
                orchestration_type = "parallel_execution"
            elif any(keyword in task_lower for keyword in ["conditional", "if", "when"]):
                orchestration_type = "conditional_execution"
            else:
                orchestration_type = "general"
            
            # Extract workflow definition if provided
            workflow_definition = kwargs.get("workflow", {})
            
            parsed_task = {
                "original_task": task,
                "orchestration_type": orchestration_type,
                "workflow_definition": workflow_definition,
                "parameters": kwargs,
                "parsed_at": datetime.now().isoformat()
            }
            
            logger.info(f"OrchestraAgent '{self.name}' parsed orchestration task: {orchestration_type}")
            return parsed_task
            
        except Exception as e:
            logger.error(f"Failed to parse orchestration task: {e}")
            raise AgentError(f"Orchestration task parsing failed: {e}") from e
    
    async def _execute_orchestration_pipeline(self, orchestration_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration pipeline.
        
        Args:
            orchestration_task: Parsed orchestration task information
            
        Returns:
            Orchestration result
        """
        try:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize workflow
            workflow = await self._initialize_workflow(workflow_id, orchestration_task)
            
            # Execute workflow
            result = await self._execute_workflow(workflow)
            
            # Cleanup workflow
            await self._cleanup_workflow(workflow_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Orchestration pipeline execution failed: {e}")
            raise AgentError(f"Orchestration pipeline failed: {e}") from e
    
    async def _initialize_workflow(self, workflow_id: str, orchestration_task: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new workflow."""
        try:
            workflow = {
                "id": workflow_id,
                "status": WorkflowStatus.PENDING,
                "task": orchestration_task["original_task"],
                "type": orchestration_task["orchestration_type"],
                "definition": orchestration_task["workflow_definition"],
                "created_at": datetime.now().isoformat(),
                "tasks": [],
                "results": {},
                "errors": []
            }
            
            # Add to active workflows
            self.active_workflows[workflow_id] = workflow
            
            logger.info(f"OrchestraAgent '{self.name}' initialized workflow: {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow: {e}")
            raise OrchestrationError(f"Workflow initialization failed: {e}") from e
    
    async def _execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        try:
            workflow_id = workflow["id"]
            workflow["status"] = WorkflowStatus.RUNNING
            
            logger.info(f"OrchestraAgent '{self.name}' executing workflow: {workflow_id}")
            
            # Parse workflow definition
            tasks = await self._parse_workflow_definition(workflow["definition"])
            workflow["tasks"] = tasks
            
            # Execute tasks based on orchestration type
            if workflow["type"] == "coordination":
                result = await self._execute_coordination_workflow(workflow)
            elif workflow["type"] == "workflow":
                result = await self._execute_sequential_workflow(workflow)
            elif workflow["type"] == "parallel_execution":
                result = await self._execute_parallel_workflow(workflow)
            elif workflow["type"] == "conditional_execution":
                result = await self._execute_conditional_workflow(workflow)
            else:
                result = await self._execute_general_workflow(workflow)
            
            workflow["status"] = WorkflowStatus.COMPLETED
            workflow["results"] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            workflow["status"] = WorkflowStatus.FAILED
            workflow["errors"].append(str(e))
            raise OrchestrationError(f"Workflow execution failed: {e}") from e
    
    async def _parse_workflow_definition(self, definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse workflow definition into executable tasks."""
        try:
            tasks = []
            
            if "tasks" in definition:
                for task_def in definition["tasks"]:
                    task = {
                        "id": task_def.get("id", f"task_{len(tasks)}"),
                        "agent_type": task_def.get("agent_type", "SimpleAgent"),
                        "task": task_def.get("task", ""),
                        "parameters": task_def.get("parameters", {}),
                        "dependencies": task_def.get("dependencies", []),
                        "dependency_type": TaskDependency(task_def.get("dependency_type", "sequential")),
                        "status": WorkflowStatus.PENDING,
                        "retry_count": 0
                    }
                    tasks.append(task)
            
            logger.info(f"OrchestraAgent '{self.name}' parsed {len(tasks)} tasks from workflow definition")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to parse workflow definition: {e}")
            raise OrchestrationError(f"Workflow definition parsing failed: {e}") from e
    
    async def _execute_coordination_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordination workflow."""
        try:
            results = {}
            
            for task in workflow["tasks"]:
                # Get or create agent for this task
                agent = await self._get_or_create_agent(task["agent_type"], task["id"])
                
                # Execute task
                task_result = await self._execute_task_with_agent(agent, task)
                results[task["id"]] = task_result
                
                # Update task status
                task["status"] = WorkflowStatus.COMPLETED
            
            return {
                "workflow_type": "coordination",
                "results": results,
                "completed_tasks": len(workflow["tasks"]),
                "total_tasks": len(workflow["tasks"])
            }
            
        except Exception as e:
            logger.error(f"Coordination workflow execution failed: {e}")
            raise OrchestrationError(f"Coordination workflow failed: {e}") from e
    
    async def _execute_sequential_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sequential workflow."""
        try:
            results = {}
            
            for task in workflow["tasks"]:
                # Get or create agent for this task
                agent = await self._get_or_create_agent(task["agent_type"], task["id"])
                
                # Execute task sequentially
                task_result = await self._execute_task_with_agent(agent, task)
                results[task["id"]] = task_result
                
                # Update task status
                task["status"] = WorkflowStatus.COMPLETED
            
            return {
                "workflow_type": "sequential",
                "results": results,
                "completed_tasks": len(workflow["tasks"]),
                "total_tasks": len(workflow["tasks"])
            }
            
        except Exception as e:
            logger.error(f"Sequential workflow execution failed: {e}")
            raise OrchestrationError(f"Sequential workflow failed: {e}") from e
    
    async def _execute_parallel_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parallel workflow."""
        try:
            # Create tasks for parallel execution
            tasks = []
            for task_def in workflow["tasks"]:
                agent = await self._get_or_create_agent(task_def["agent_type"], task_def["id"])
                task = self._execute_task_with_agent(agent, task_def)
                tasks.append(task)
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = {}
            for i, result in enumerate(results):
                task_id = workflow["tasks"][i]["id"]
                if isinstance(result, Exception):
                    processed_results[task_id] = {"error": str(result), "success": False}
                    workflow["tasks"][i]["status"] = WorkflowStatus.FAILED
                else:
                    processed_results[task_id] = result
                    workflow["tasks"][i]["status"] = WorkflowStatus.COMPLETED
            
            return {
                "workflow_type": "parallel",
                "results": processed_results,
                "completed_tasks": len([r for r in processed_results.values() if r.get("success", False)]),
                "total_tasks": len(workflow["tasks"])
            }
            
        except Exception as e:
            logger.error(f"Parallel workflow execution failed: {e}")
            raise OrchestrationError(f"Parallel workflow failed: {e}") from e
    
    async def _execute_conditional_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conditional workflow."""
        try:
            results = {}
            
            for task in workflow["tasks"]:
                # Check conditions
                if await self._evaluate_task_conditions(task):
                    # Get or create agent for this task
                    agent = await self._get_or_create_agent(task["agent_type"], task["id"])
                    
                    # Execute task
                    task_result = await self._execute_task_with_agent(agent, task)
                    results[task["id"]] = task_result
                    
                    # Update task status
                    task["status"] = WorkflowStatus.COMPLETED
                else:
                    # Skip task
                    results[task["id"]] = {"skipped": True, "reason": "condition_not_met"}
                    task["status"] = WorkflowStatus.CANCELLED
            
            return {
                "workflow_type": "conditional",
                "results": results,
                "completed_tasks": len([r for r in results.values() if not r.get("skipped", False)]),
                "total_tasks": len(workflow["tasks"])
            }
            
        except Exception as e:
            logger.error(f"Conditional workflow execution failed: {e}")
            raise OrchestrationError(f"Conditional workflow failed: {e}") from e
    
    async def _execute_general_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general workflow."""
        return await self._execute_coordination_workflow(workflow)
    
    async def _get_or_create_agent(self, agent_type: str, agent_id: str) -> UnifiedAgent:
        """Get or create an agent for task execution."""
        try:
            if agent_id in self.managed_agents:
                return self.managed_agents[agent_id]
            
            # Create new agent based on type
            if agent_type == "SimpleAgent":
                from .simple_agent import SimpleAgent
                agent = SimpleAgent(
                    name=f"{agent_type}_{agent_id}",
                    description=f"Managed {agent_type} for orchestration",
                    config=self.config
                )
            elif agent_type == "BrowserAgent":
                from .browser_agent import BrowserAgent
                agent = BrowserAgent(
                    name=f"{agent_type}_{agent_id}",
                    description=f"Managed {agent_type} for orchestration",
                    config=self.config
                )
            else:
                # Default to SimpleAgent
                from .simple_agent import SimpleAgent
                agent = SimpleAgent(
                    name=f"{agent_type}_{agent_id}",
                    description=f"Managed {agent_type} for orchestration",
                    config=self.config
                )
            
            # Setup agent
            await agent.setup()
            
            # Add to managed agents
            self.managed_agents[agent_id] = agent
            
            logger.info(f"OrchestraAgent '{self.name}' created managed agent: {agent_type}_{agent_id}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to get or create agent: {e}")
            raise OrchestrationError(f"Agent creation failed: {e}") from e
    
    async def _execute_task_with_agent(self, agent: UnifiedAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with a specific agent."""
        try:
            result = await agent.run(task["task"], **task.get("parameters", {}))
            return result
            
        except Exception as e:
            logger.error(f"Task execution with agent failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "agent": agent.name,
                "task": task["task"]
            }
    
    async def _evaluate_task_conditions(self, task: Dict[str, Any]) -> bool:
        """Evaluate conditions for conditional task execution."""
        try:
            conditions = task.get("conditions", [])
            
            if not conditions:
                return True  # No conditions, always execute
            
            # Simple condition evaluation - can be enhanced
            for condition in conditions:
                if not await self._evaluate_condition(condition):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to evaluate task conditions: {e}")
            return False
    
    async def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition."""
        try:
            condition_type = condition.get("type", "always")
            
            if condition_type == "always":
                return True
            elif condition_type == "never":
                return False
            elif condition_type == "random":
                import random
                return random.random() < condition.get("probability", 0.5)
            else:
                return True  # Default to true for unknown conditions
            
        except Exception as e:
            logger.error(f"Failed to evaluate condition: {e}")
            return False
    
    async def _cleanup_workflow(self, workflow_id: str) -> None:
        """Cleanup workflow resources."""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                
                # Move to history
                self.workflow_history.append(workflow)
                
                # Remove from active workflows
                del self.active_workflows[workflow_id]
                
                logger.info(f"OrchestraAgent '{self.name}' cleaned up workflow: {workflow_id}")
            
        except Exception as e:
            logger.error(f"Workflow cleanup failed: {e}")
    
    async def _cleanup_agent_specific(self) -> None:
        """Cleanup Orchestra Agent specific resources."""
        try:
            logger.info(f"Cleaning up OrchestraAgent '{self.name}' specific resources...")
            
            # Cleanup managed agents
            for agent_id, agent in self.managed_agents.items():
                try:
                    await agent.cleanup()
                except Exception as e:
                    logger.error(f"Failed to cleanup managed agent {agent_id}: {e}")
            
            self.managed_agents.clear()
            
            # Cleanup active workflows
            for workflow_id in list(self.active_workflows.keys()):
                await self._cleanup_workflow(workflow_id)
            
            # Clear orchestration pipeline
            self.orchestration_pipeline = []
            
            logger.info(f"OrchestraAgent '{self.name}' specific cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup OrchestraAgent '{self.name}' specific resources: {e}")
            raise AgentError(f"OrchestraAgent cleanup failed: {e}") from e
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get Orchestra Agent specific information."""
        base_info = self.get_stats()
        base_info.update({
            "agent_type": "OrchestraAgent",
            "max_concurrent_agents": self.max_concurrent_agents,
            "workflow_timeout": self.workflow_timeout,
            "retry_attempts": self.retry_attempts,
            "managed_agents_count": len(self.managed_agents),
            "active_workflows_count": len(self.active_workflows),
            "workflow_history_count": len(self.workflow_history),
            "orchestration_pipeline": getattr(self, 'orchestration_pipeline', [])
        })
        return base_info