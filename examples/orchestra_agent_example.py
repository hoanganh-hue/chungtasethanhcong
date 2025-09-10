"""
Orchestra Agent Example.

This example demonstrates how to use the OrchestraAgent for multi-agent
coordination, workflow management, and complex task orchestration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.agents.orchestra_agent import OrchestraAgent, WorkflowStatus, TaskDependency
from src.agents.simple_agent import SimpleAgent
from src.agents.browser_agent import BrowserAgent
from src.core.config import UnifiedConfig
from src.core.tool_registry import BaseTool, ToolMetadata, ToolDefinition, ToolCategory
from src.utils.logger import setup_logging


class WorkflowManagerTool(BaseTool):
    """Example workflow management tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="workflow_manager",
            description="Manage and coordinate workflows",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "workflow_id": {"type": "str", "description": "Workflow identifier"},
                "action": {"type": "str", "description": "Action to perform"}
            },
            return_type=dict
        )
    
    async def execute(self, workflow_id: str, action: str = "manage", **kwargs) -> dict:
        """Execute workflow management."""
        # Simulate workflow management
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "workflow_id": workflow_id,
            "action": action,
            "result": {
                "status": "managed",
                "tasks_coordinated": 3,
                "resources_allocated": True,
                "workflow_optimized": True
            },
            "status": "success"
        }


class TaskDistributorTool(BaseTool):
    """Example task distribution tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="task_distributor",
            description="Distribute tasks among available agents",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "tasks": {"type": "list", "description": "List of tasks to distribute"},
                "agents": {"type": "list", "description": "Available agents"}
            },
            return_type=dict
        )
    
    async def execute(self, tasks: list, agents: list = None, **kwargs) -> dict:
        """Execute task distribution."""
        # Simulate task distribution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        agents = agents or ["SimpleAgent", "BrowserAgent"]
        
        return {
            "tasks": tasks,
            "agents": agents,
            "result": {
                "distribution": {
                    "SimpleAgent": tasks[:len(tasks)//2] if len(tasks) > 1 else tasks,
                    "BrowserAgent": tasks[len(tasks)//2:] if len(tasks) > 1 else []
                },
                "load_balanced": True,
                "efficiency_score": 0.95
            },
            "status": "success"
        }


class ResultAggregatorTool(BaseTool):
    """Example result aggregation tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="result_aggregator",
            description="Aggregate results from multiple agents",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "results": {"type": "list", "description": "List of results to aggregate"},
                "aggregation_type": {"type": "str", "description": "Type of aggregation"}
            },
            return_type=dict
        )
    
    async def execute(self, results: list, aggregation_type: str = "merge", **kwargs) -> dict:
        """Execute result aggregation."""
        # Simulate result aggregation
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "results": results,
            "aggregation_type": aggregation_type,
            "result": {
                "aggregated_data": {
                    "total_results": len(results),
                    "successful_results": len([r for r in results if r.get("success", False)]),
                    "failed_results": len([r for r in results if not r.get("success", False)]),
                    "combined_insights": [
                        "All agents completed their tasks",
                        "Data quality is high",
                        "No critical errors detected"
                    ]
                },
                "summary": f"Successfully aggregated {len(results)} results using {aggregation_type} method"
            },
            "status": "success"
        }


async def main():
    """Main example function."""
    # Setup logging
    setup_logging(level="INFO")
    
    print("🎼 Orchestra Agent Example")
    print("=" * 50)
    
    # Create configuration
    config = UnifiedConfig(
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.7
    )
    
    # Create tools
    tools = [
        WorkflowManagerTool(),
        TaskDistributorTool(),
        ResultAggregatorTool()
    ]
    
    # Create Orchestra Agent
    agent = OrchestraAgent(
        name="example_orchestra_agent",
        description="An example orchestra agent for multi-agent coordination",
        config=config,
        tools=tools,
        max_concurrent_agents=3,
        workflow_timeout=300,
        retry_attempts=2
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Max concurrent agents: {agent.max_concurrent_agents}")
    print(f"Workflow timeout: {agent.workflow_timeout}s")
    print(f"Retry attempts: {agent.retry_attempts}")
    print(f"Tools available: {[tool._get_metadata().name for tool in tools]}")
    print()
    
    # Setup agent
    print("Setting up agent...")
    await agent.setup()
    print("✅ Agent setup completed")
    print()
    
    # Example 1: Sequential Workflow
    print("🔄 Example 1: Sequential Workflow")
    print("-" * 30)
    
    sequential_workflow = {
        "tasks": [
            {
                "id": "task1",
                "agent_type": "SimpleAgent",
                "task": "Analyze the data and extract key insights",
                "parameters": {"data": "Sample data for analysis"},
                "dependencies": [],
                "dependency_type": "sequential"
            },
            {
                "id": "task2",
                "agent_type": "BrowserAgent",
                "task": "Search for additional information online",
                "parameters": {"query": "data analysis techniques"},
                "dependencies": ["task1"],
                "dependency_type": "sequential"
            },
            {
                "id": "task3",
                "agent_type": "SimpleAgent",
                "task": "Generate a comprehensive report",
                "parameters": {"format": "markdown"},
                "dependencies": ["task2"],
                "dependency_type": "sequential"
            }
        ]
    }
    
    result1 = await agent.run(
        "Execute a sequential workflow for data analysis and reporting",
        workflow=sequential_workflow
    )
    
    print(f"Task: {result1['task']}")
    print(f"Success: {result1['success']}")
    print(f"Execution time: {result1['execution_time']:.2f}s")
    
    if result1['success']:
        print("Results:")
        for key, value in result1['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for task_id, task_result in value.items():
                    print(f"    {task_id}: {task_result}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 2: Parallel Workflow
    print("⚡ Example 2: Parallel Workflow")
    print("-" * 30)
    
    parallel_workflow = {
        "tasks": [
            {
                "id": "parallel_task1",
                "agent_type": "SimpleAgent",
                "task": "Process customer data",
                "parameters": {"data_type": "customer"},
                "dependencies": [],
                "dependency_type": "parallel"
            },
            {
                "id": "parallel_task2",
                "agent_type": "SimpleAgent",
                "task": "Process product data",
                "parameters": {"data_type": "product"},
                "dependencies": [],
                "dependency_type": "parallel"
            },
            {
                "id": "parallel_task3",
                "agent_type": "BrowserAgent",
                "task": "Scrape market data",
                "parameters": {"url": "https://example.com/market"},
                "dependencies": [],
                "dependency_type": "parallel"
            }
        ]
    }
    
    result2 = await agent.run(
        "Execute a parallel workflow for data processing",
        workflow=parallel_workflow
    )
    
    print(f"Task: {result2['task']}")
    print(f"Success: {result2['success']}")
    print(f"Execution time: {result2['execution_time']:.2f}s")
    
    if result2['success']:
        print("Results:")
        for key, value in result2['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for task_id, task_result in value.items():
                    print(f"    {task_id}: {task_result}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 3: Conditional Workflow
    print("🔀 Example 3: Conditional Workflow")
    print("-" * 30)
    
    conditional_workflow = {
        "tasks": [
            {
                "id": "conditional_task1",
                "agent_type": "SimpleAgent",
                "task": "Check data quality",
                "parameters": {"threshold": 0.8},
                "dependencies": [],
                "dependency_type": "conditional",
                "conditions": [
                    {"type": "always", "value": True}
                ]
            },
            {
                "id": "conditional_task2",
                "agent_type": "SimpleAgent",
                "task": "Process high-quality data",
                "parameters": {"quality": "high"},
                "dependencies": ["conditional_task1"],
                "dependency_type": "conditional",
                "conditions": [
                    {"type": "random", "probability": 0.7}
                ]
            },
            {
                "id": "conditional_task3",
                "agent_type": "SimpleAgent",
                "task": "Process low-quality data",
                "parameters": {"quality": "low"},
                "dependencies": ["conditional_task1"],
                "dependency_type": "conditional",
                "conditions": [
                    {"type": "random", "probability": 0.3}
                ]
            }
        ]
    }
    
    result3 = await agent.run(
        "Execute a conditional workflow based on data quality",
        workflow=conditional_workflow
    )
    
    print(f"Task: {result3['task']}")
    print(f"Success: {result3['success']}")
    print(f"Execution time: {result3['execution_time']:.2f}s")
    
    if result3['success']:
        print("Results:")
        for key, value in result3['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for task_id, task_result in value.items():
                    print(f"    {task_id}: {task_result}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 4: Complex Multi-Agent Coordination
    print("🎯 Example 4: Complex Multi-Agent Coordination")
    print("-" * 30)
    
    complex_workflow = {
        "tasks": [
            {
                "id": "research_task",
                "agent_type": "BrowserAgent",
                "task": "Research the latest AI trends",
                "parameters": {"query": "artificial intelligence trends 2024"},
                "dependencies": [],
                "dependency_type": "sequential"
            },
            {
                "id": "analysis_task",
                "agent_type": "SimpleAgent",
                "task": "Analyze the research data",
                "parameters": {"analysis_type": "trend_analysis"},
                "dependencies": ["research_task"],
                "dependency_type": "sequential"
            },
            {
                "id": "report_task",
                "agent_type": "SimpleAgent",
                "task": "Generate a comprehensive report",
                "parameters": {"format": "pdf", "include_charts": True},
                "dependencies": ["analysis_task"],
                "dependency_type": "sequential"
            },
            {
                "id": "validation_task",
                "agent_type": "SimpleAgent",
                "task": "Validate the report quality",
                "parameters": {"quality_checks": ["grammar", "accuracy", "completeness"]},
                "dependencies": ["report_task"],
                "dependency_type": "parallel"
            },
            {
                "id": "distribution_task",
                "agent_type": "BrowserAgent",
                "task": "Distribute the report via email",
                "parameters": {"recipients": ["team@example.com"]},
                "dependencies": ["validation_task"],
                "dependency_type": "sequential"
            }
        ]
    }
    
    result4 = await agent.run(
        "Execute a complex multi-agent workflow for AI research and reporting",
        workflow=complex_workflow
    )
    
    print(f"Task: {result4['task']}")
    print(f"Success: {result4['success']}")
    print(f"Execution time: {result4['execution_time']:.2f}s")
    
    if result4['success']:
        print("Results:")
        for key, value in result4['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for task_id, task_result in value.items():
                    print(f"    {task_id}: {task_result}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Show agent statistics
    print("📈 Agent Statistics")
    print("-" * 30)
    
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print()
    
    # Show managed agents
    print("🤖 Managed Agents")
    print("-" * 30)
    
    for agent_id, managed_agent in agent.managed_agents.items():
        print(f"  {agent_id}: {managed_agent.name} ({managed_agent.__class__.__name__})")
    
    print()
    
    # Show workflow history
    print("📋 Workflow History")
    print("-" * 30)
    
    for workflow in agent.workflow_history:
        print(f"  Workflow {workflow['id']}: {workflow['status']} - {workflow['task']}")
    
    print()
    
    # Cleanup
    print("🧹 Cleaning up agent...")
    await agent.cleanup()
    print("✅ Agent cleanup completed")
    
    print()
    print("🎉 Orchestra Agent Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())