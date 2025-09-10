"""
API Routes for OpenManus-Youtu Integrated Framework

This module defines FastAPI routes for the unified framework API.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import time
import uuid
from datetime import datetime

from .models import (
    AgentRequest,
    AgentResponse,
    ToolRequest,
    ToolResponse,
    WorkflowRequest,
    WorkflowResponse,
    HealthResponse,
    ErrorResponse,
    ListResponse,
    AgentType,
    ToolCategory
)
from ..core.unified_agent import UnifiedAgent
from ..agents.simple_agent import SimpleAgent
from ..agents.browser_agent import BrowserAgent
from ..agents.orchestra_agent import OrchestraAgent
from ..agents.meta_agent import MetaAgent
from ..tools.base_tool import BaseTool
from ..utils.tool_registry import ToolRegistry
from ..utils.environment_manager import EnvironmentManager

# Create router
router = APIRouter()

# Global instances
tool_registry = ToolRegistry()
environment_manager = EnvironmentManager()
active_agents: Dict[str, UnifiedAgent] = {}
active_workflows: Dict[str, Dict[str, Any]] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        components = {
            "tool_registry": "healthy" if tool_registry else "unhealthy",
            "environment_manager": "healthy" if environment_manager else "unhealthy",
            "agents": "healthy" if active_agents else "healthy",
            "workflows": "healthy" if active_workflows else "healthy"
        }
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime=time.time(),
            components=components,
            metrics={
                "active_agents": len(active_agents),
                "active_workflows": len(active_workflows),
                "registered_tools": len(tool_registry.get_all_tools()) if tool_registry else 0
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/tools", response_model=ListResponse)
async def list_tools(
    category: Optional[ToolCategory] = None,
    page: int = 1,
    page_size: int = 10
):
    """List available tools."""
    try:
        all_tools = tool_registry.get_all_tools()
        
        if category:
            all_tools = [tool for tool in all_tools if tool.category == category.value]
        
        total = len(all_tools)
        start = (page - 1) * page_size
        end = start + page_size
        items = all_tools[start:end]
        
        return ListResponse(
            items=[tool.to_dict() for tool in items],
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total,
            has_prev=page > 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Get specific tool information."""
    try:
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        return tool.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool: {str(e)}")


@router.post("/tools/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool."""
    start_time = time.time()
    
    try:
        tool = tool_registry.get_tool(request.tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
        
        # Execute tool
        result = await tool.run(**request.parameters)
        execution_time = time.time() - start_time
        
        return ToolResponse(
            success=True,
            result=result,
            execution_time=execution_time,
            metadata={
                "tool_name": request.tool_name,
                "parameters": request.parameters,
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        return ToolResponse(
            success=False,
            error=str(e),
            execution_time=execution_time,
            metadata={
                "tool_name": request.tool_name,
                "parameters": request.parameters,
                "timestamp": datetime.now().isoformat()
            }
        )


@router.post("/agents/create", response_model=AgentResponse)
async def create_agent(request: AgentRequest):
    """Create a new agent."""
    start_time = time.time()
    
    try:
        agent_id = str(uuid.uuid4())
        
        # Create agent based on type
        if request.agent_type == AgentType.SIMPLE:
            agent = SimpleAgent(
                name=request.name or f"simple_agent_{agent_id[:8]}",
                config=request.config or {}
            )
        elif request.agent_type == AgentType.BROWSER:
            agent = BrowserAgent(
                name=request.name or f"browser_agent_{agent_id[:8]}",
                config=request.config or {}
            )
        elif request.agent_type == AgentType.ORCHESTRA:
            agent = OrchestraAgent(
                name=request.name or f"orchestra_agent_{agent_id[:8]}",
                config=request.config or {}
            )
        elif request.agent_type == AgentType.META:
            agent = MetaAgent(
                name=request.name or f"meta_agent_{agent_id[:8]}",
                config=request.config or {}
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported agent type: {request.agent_type}")
        
        # Store agent
        active_agents[agent_id] = agent
        execution_time = time.time() - start_time
        
        return AgentResponse(
            success=True,
            agent_id=agent_id,
            execution_time=execution_time,
            metadata={
                "agent_type": request.agent_type.value,
                "name": agent.name,
                "created_at": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            error=str(e),
            execution_time=execution_time
        )


@router.post("/agents/{agent_id}/execute", response_model=AgentResponse)
async def execute_agent(agent_id: str, request: AgentRequest):
    """Execute a task with an agent."""
    start_time = time.time()
    
    try:
        if agent_id not in active_agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        agent = active_agents[agent_id]
        
        if not request.task:
            raise HTTPException(status_code=400, detail="Task is required for execution")
        
        # Execute task
        result = await agent.execute_task(
            task=request.task,
            parameters=request.parameters or {}
        )
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            success=True,
            result=result,
            execution_time=execution_time,
            metadata={
                "agent_id": agent_id,
                "task": request.task,
                "parameters": request.parameters,
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            error=str(e),
            execution_time=execution_time,
            metadata={
                "agent_id": agent_id,
                "task": request.task,
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/agents", response_model=ListResponse)
async def list_agents(page: int = 1, page_size: int = 10):
    """List active agents."""
    try:
        agent_list = []
        for agent_id, agent in active_agents.items():
            agent_list.append({
                "agent_id": agent_id,
                "name": agent.name,
                "type": agent.__class__.__name__,
                "status": "active",
                "created_at": getattr(agent, 'created_at', datetime.now().isoformat())
            })
        
        total = len(agent_list)
        start = (page - 1) * page_size
        end = start + page_size
        items = agent_list[start:end]
        
        return ListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total,
            has_prev=page > 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    try:
        if agent_id not in active_agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        # Cleanup agent resources
        agent = active_agents[agent_id]
        if hasattr(agent, 'cleanup'):
            await agent.cleanup()
        
        del active_agents[agent_id]
        
        return {"success": True, "message": f"Agent '{agent_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


@router.post("/workflows/execute", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Execute a workflow."""
    start_time = time.time()
    workflow_id = str(uuid.uuid4())
    
    try:
        # Store workflow
        active_workflows[workflow_id] = {
            "name": request.name,
            "description": request.description,
            "steps": request.steps,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "results": {}
        }
        
        # Execute workflow in background
        background_tasks.add_task(
            _execute_workflow_steps,
            workflow_id,
            request.steps,
            request.parallel,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return WorkflowResponse(
            success=True,
            workflow_id=workflow_id,
            execution_time=execution_time,
            metadata={
                "name": request.name,
                "steps_count": len(request.steps),
                "parallel": request.parallel,
                "created_at": datetime.now().isoformat()
            }
        )
    except Exception as e:
        execution_time = time.time() - start_time
        return WorkflowResponse(
            success=False,
            error=str(e),
            execution_time=execution_time
        )


@router.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow execution status."""
    try:
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
        
        workflow = active_workflows[workflow_id]
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


@router.get("/workflows", response_model=ListResponse)
async def list_workflows(page: int = 1, page_size: int = 10):
    """List active workflows."""
    try:
        workflow_list = []
        for workflow_id, workflow in active_workflows.items():
            workflow_list.append({
                "workflow_id": workflow_id,
                "name": workflow["name"],
                "status": workflow["status"],
                "created_at": workflow["created_at"],
                "steps_count": len(workflow["steps"])
            })
        
        total = len(workflow_list)
        start = (page - 1) * page_size
        end = start + page_size
        items = workflow_list[start:end]
        
        return ListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total,
            has_prev=page > 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


async def _execute_workflow_steps(
    workflow_id: str,
    steps: List[Dict[str, Any]],
    parallel: bool,
    timeout: int
):
    """Execute workflow steps in background."""
    try:
        results = {}
        
        if parallel:
            # Execute steps in parallel
            import asyncio
            tasks = []
            for step in steps:
                task = _execute_workflow_step(step)
                tasks.append(task)
            
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(step_results):
                step_id = steps[i]["step_id"]
                if isinstance(result, Exception):
                    results[step_id] = {"success": False, "error": str(result)}
                else:
                    results[step_id] = {"success": True, "result": result}
        else:
            # Execute steps sequentially
            for step in steps:
                try:
                    result = await _execute_workflow_step(step)
                    results[step["step_id"]] = {"success": True, "result": result}
                except Exception as e:
                    results[step["step_id"]] = {"success": False, "error": str(e)}
                    break  # Stop on first error
        
        # Update workflow status
        active_workflows[workflow_id]["status"] = "completed"
        active_workflows[workflow_id]["results"] = results
        
    except Exception as e:
        active_workflows[workflow_id]["status"] = "failed"
        active_workflows[workflow_id]["error"] = str(e)


async def _execute_workflow_step(step: Dict[str, Any]) -> Any:
    """Execute a single workflow step."""
    step_id = step["step_id"]
    
    if step.get("agent_type"):
        # Execute with agent
        agent_type = step["agent_type"]
        if agent_type not in active_agents:
            raise ValueError(f"Agent '{agent_type}' not found")
        
        agent = active_agents[agent_type]
        return await agent.execute_task(
            task=step.get("task", ""),
            parameters=step.get("parameters", {})
        )
    
    elif step.get("tool_name"):
        # Execute with tool
        tool_name = step["tool_name"]
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        return await tool.run(**step.get("parameters", {}))
    
    else:
        raise ValueError("Step must specify either agent_type or tool_name")