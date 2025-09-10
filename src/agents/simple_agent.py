"""
Simple Agent Implementation.

This module provides the SimpleAgent class, which is designed for
single-purpose tasks with basic tool usage and memory management.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..core.unified_agent import UnifiedAgent
from ..core.config import UnifiedConfig
from ..core.tool_registry import BaseTool
from ..core.memory import UnifiedMemory
from ..core.state import AgentState
from ..utils.exceptions import AgentError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SimpleAgent(UnifiedAgent):
    """
    Simple Agent for single-purpose tasks.
    
    This agent is designed for straightforward tasks that require
    basic tool usage and simple memory management. It's ideal for
    tasks like data processing, file operations, and simple analysis.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: UnifiedConfig,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[UnifiedMemory] = None,
        state: Optional[AgentState] = None,
        max_iterations: int = 10,
        timeout: int = 300
    ):
        """
        Initialize the Simple Agent.
        
        Args:
            name: Agent name
            description: Agent description
            config: Agent configuration
            tools: List of available tools
            memory: Memory system instance
            state: Agent state instance
            max_iterations: Maximum number of execution iterations
            timeout: Execution timeout in seconds
        """
        super().__init__(name, description, config, tools, memory, state)
        
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.current_iteration = 0
        
        logger.info(f"SimpleAgent '{name}' initialized with max_iterations={max_iterations}, timeout={timeout}")
    
    async def _setup_agent_specific(self) -> None:
        """Setup Simple Agent specific components."""
        try:
            logger.info(f"Setting up SimpleAgent '{self.name}' specific components...")
            
            # Initialize iteration counter
            self.current_iteration = 0
            
            # Setup simple execution pipeline
            self.execution_pipeline = [
                "parse_task",
                "select_tools",
                "execute_tools",
                "process_results",
                "generate_response"
            ]
            
            logger.info(f"SimpleAgent '{self.name}' specific setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup SimpleAgent '{self.name}' specific components: {e}")
            raise AgentError(f"SimpleAgent setup failed: {e}") from e
    
    async def _execute_task(self, task: str, **kwargs) -> Any:
        """
        Execute a simple task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Task execution result
        """
        try:
            logger.info(f"SimpleAgent '{self.name}' executing task: {task}")
            
            # Reset iteration counter
            self.current_iteration = 0
            
            # Execute the task with timeout
            result = await asyncio.wait_for(
                self._execute_with_iterations(task, **kwargs),
                timeout=self.timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            raise AgentError(f"Task execution timed out after {self.timeout} seconds")
        except Exception as e:
            logger.error(f"SimpleAgent '{self.name}' task execution failed: {e}")
            raise AgentError(f"Task execution failed: {e}") from e
    
    async def _execute_with_iterations(self, task: str, **kwargs) -> Any:
        """
        Execute task with iteration control.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Task execution result
        """
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration
            
            try:
                logger.info(f"SimpleAgent '{self.name}' iteration {iteration + 1}/{self.max_iterations}")
                
                # Parse the task
                parsed_task = await self._parse_task(task, **kwargs)
                
                # Select appropriate tools
                selected_tools = await self._select_tools(parsed_task)
                
                # Execute tools
                tool_results = await self._execute_tools(selected_tools, parsed_task)
                
                # Process results
                processed_results = await self._process_results(tool_results, parsed_task)
                
                # Check if task is complete
                if await self._is_task_complete(processed_results, parsed_task):
                    # Generate final response
                    final_response = await self._generate_response(processed_results, parsed_task)
                    return final_response
                
                # Store intermediate results
                await self.memory.store(f"iteration_{iteration}", processed_results)
                
            except Exception as e:
                logger.error(f"SimpleAgent '{self.name}' iteration {iteration + 1} failed: {e}")
                if iteration == self.max_iterations - 1:
                    raise
                continue
        
        # If we reach here, max iterations exceeded
        raise AgentError(f"Task execution exceeded maximum iterations ({self.max_iterations})")
    
    async def _parse_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Parse the task description.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Parsed task information
        """
        try:
            # Simple task parsing - can be enhanced with NLP
            parsed_task = {
                "original_task": task,
                "task_type": self._classify_task_type(task),
                "required_tools": self._identify_required_tools(task),
                "parameters": kwargs,
                "parsed_at": datetime.now().isoformat()
            }
            
            logger.info(f"SimpleAgent '{self.name}' parsed task: {parsed_task['task_type']}")
            return parsed_task
            
        except Exception as e:
            logger.error(f"Failed to parse task: {e}")
            raise AgentError(f"Task parsing failed: {e}") from e
    
    def _classify_task_type(self, task: str) -> str:
        """Classify the task type based on keywords."""
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ["search", "find", "lookup"]):
            return "search"
        elif any(keyword in task_lower for keyword in ["analyze", "process", "examine"]):
            return "analysis"
        elif any(keyword in task_lower for keyword in ["create", "generate", "make"]):
            return "creation"
        elif any(keyword in task_lower for keyword in ["read", "load", "open"]):
            return "file_operation"
        elif any(keyword in task_lower for keyword in ["write", "save", "export"]):
            return "file_operation"
        else:
            return "general"
    
    def _identify_required_tools(self, task: str) -> List[str]:
        """Identify required tools based on task description."""
        task_lower = task.lower()
        required_tools = []
        
        # Map task keywords to tool names
        tool_mapping = {
            "search": ["web_search", "google_search"],
            "file": ["file_reader", "file_writer"],
            "data": ["data_analysis", "csv_analysis"],
            "chart": ["chart_generation", "data_visualization"],
            "pdf": ["pdf_processor"],
            "excel": ["excel_processor"]
        }
        
        for keyword, tools in tool_mapping.items():
            if keyword in task_lower:
                required_tools.extend(tools)
        
        return list(set(required_tools))  # Remove duplicates
    
    async def _select_tools(self, parsed_task: Dict[str, Any]) -> List[BaseTool]:
        """
        Select appropriate tools for the task.
        
        Args:
            parsed_task: Parsed task information
            
        Returns:
            List of selected tools
        """
        try:
            required_tools = parsed_task.get("required_tools", [])
            selected_tools = []
            
            for tool_name in required_tools:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    selected_tools.append(tool)
                else:
                    logger.warning(f"Required tool '{tool_name}' not available")
            
            logger.info(f"SimpleAgent '{self.name}' selected {len(selected_tools)} tools")
            return selected_tools
            
        except Exception as e:
            logger.error(f"Failed to select tools: {e}")
            raise AgentError(f"Tool selection failed: {e}") from e
    
    async def _execute_tools(self, tools: List[BaseTool], parsed_task: Dict[str, Any]) -> List[Any]:
        """
        Execute selected tools.
        
        Args:
            tools: List of tools to execute
            parsed_task: Parsed task information
            
        Returns:
            List of tool execution results
        """
        try:
            results = []
            
            for tool in tools:
                try:
                    logger.info(f"SimpleAgent '{self.name}' executing tool: {tool._get_metadata().name}")
                    
                    # Execute tool with task context
                    result = await tool.execute(
                        task=parsed_task["original_task"],
                        task_type=parsed_task["task_type"],
                        **parsed_task.get("parameters", {})
                    )
                    
                    results.append({
                        "tool": tool._get_metadata().name,
                        "result": result,
                        "success": True
                    })
                    
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    results.append({
                        "tool": tool._get_metadata().name,
                        "error": str(e),
                        "success": False
                    })
            
            logger.info(f"SimpleAgent '{self.name}' executed {len(tools)} tools")
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute tools: {e}")
            raise AgentError(f"Tool execution failed: {e}") from e
    
    async def _process_results(self, tool_results: List[Any], parsed_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process tool execution results.
        
        Args:
            tool_results: List of tool execution results
            parsed_task: Parsed task information
            
        Returns:
            Processed results
        """
        try:
            processed_results = {
                "task": parsed_task["original_task"],
                "task_type": parsed_task["task_type"],
                "tool_results": tool_results,
                "successful_tools": [r for r in tool_results if r.get("success", False)],
                "failed_tools": [r for r in tool_results if not r.get("success", False)],
                "processed_at": datetime.now().isoformat()
            }
            
            # Combine successful results
            combined_results = []
            for result in processed_results["successful_tools"]:
                combined_results.append(result["result"])
            
            processed_results["combined_results"] = combined_results
            
            logger.info(f"SimpleAgent '{self.name}' processed {len(tool_results)} tool results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to process results: {e}")
            raise AgentError(f"Result processing failed: {e}") from e
    
    async def _is_task_complete(self, processed_results: Dict[str, Any], parsed_task: Dict[str, Any]) -> bool:
        """
        Check if the task is complete.
        
        Args:
            processed_results: Processed tool results
            parsed_task: Parsed task information
            
        Returns:
            True if task is complete, False otherwise
        """
        # Simple completion check - can be enhanced
        successful_tools = processed_results.get("successful_tools", [])
        required_tools = parsed_task.get("required_tools", [])
        
        # Task is complete if we have at least one successful tool result
        return len(successful_tools) > 0
    
    async def _generate_response(self, processed_results: Dict[str, Any], parsed_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final response.
        
        Args:
            processed_results: Processed tool results
            parsed_task: Parsed task information
            
        Returns:
            Final response
        """
        try:
            response = {
                "task": parsed_task["original_task"],
                "task_type": parsed_task["task_type"],
                "status": "completed",
                "results": processed_results["combined_results"],
                "tools_used": [r["tool"] for r in processed_results["successful_tools"]],
                "tools_failed": [r["tool"] for r in processed_results["failed_tools"]],
                "iterations": self.current_iteration + 1,
                "completed_at": datetime.now().isoformat()
            }
            
            # Generate summary
            if processed_results["combined_results"]:
                response["summary"] = f"Successfully completed {parsed_task['task_type']} task using {len(processed_results['successful_tools'])} tools"
            else:
                response["summary"] = f"Task completed with no successful tool executions"
            
            logger.info(f"SimpleAgent '{self.name}' generated response: {response['summary']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise AgentError(f"Response generation failed: {e}") from e
    
    async def _cleanup_agent_specific(self) -> None:
        """Cleanup Simple Agent specific resources."""
        try:
            logger.info(f"Cleaning up SimpleAgent '{self.name}' specific resources...")
            
            # Reset iteration counter
            self.current_iteration = 0
            
            # Clear execution pipeline
            self.execution_pipeline = []
            
            logger.info(f"SimpleAgent '{self.name}' specific cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup SimpleAgent '{self.name}' specific resources: {e}")
            raise AgentError(f"SimpleAgent cleanup failed: {e}") from e
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get Simple Agent specific information."""
        base_info = self.get_stats()
        base_info.update({
            "agent_type": "SimpleAgent",
            "max_iterations": self.max_iterations,
            "timeout": self.timeout,
            "current_iteration": self.current_iteration,
            "execution_pipeline": getattr(self, 'execution_pipeline', [])
        })
        return base_info