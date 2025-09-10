"""
Meta Agent Example.

This example demonstrates how to use the MetaAgent for automatic agent
generation, configuration management, and agent template handling.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.agents.meta_agent import MetaAgent
from src.core.config import UnifiedConfig
from src.core.tool_registry import BaseTool, ToolMetadata, ToolDefinition, ToolCategory
from src.utils.logger import setup_logging


class AgentGeneratorTool(BaseTool):
    """Example agent generation tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="agent_generator",
            description="Generate new agents from templates",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "template": {"type": "str", "description": "Template to use"},
                "parameters": {"type": "dict", "description": "Generation parameters"}
            },
            return_type=dict
        )
    
    async def execute(self, template: str, parameters: dict = None, **kwargs) -> dict:
        """Execute agent generation."""
        # Simulate agent generation
        await asyncio.sleep(0.2)  # Simulate generation time
        
        parameters = parameters or {}
        
        return {
            "template": template,
            "parameters": parameters,
            "result": {
                "agent_id": f"generated_{template}_{asyncio.get_event_loop().time()}",
                "agent_name": parameters.get("name", f"Generated {template}"),
                "agent_type": template,
                "configuration": {
                    "model": "gpt-4o",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    **parameters.get("config", {})
                },
                "tools": parameters.get("tools", []),
                "capabilities": parameters.get("capabilities", []),
                "generation_status": "success"
            },
            "status": "success"
        }


class ConfigValidatorTool(BaseTool):
    """Example configuration validation tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="config_validator",
            description="Validate agent configurations",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "config": {"type": "dict", "description": "Configuration to validate"},
                "strict": {"type": "bool", "description": "Use strict validation"}
            },
            return_type=dict
        )
    
    async def execute(self, config: dict, strict: bool = True, **kwargs) -> dict:
        """Execute configuration validation."""
        # Simulate configuration validation
        await asyncio.sleep(0.1)  # Simulate validation time
        
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ["name", "type", "description"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Check agent type
        valid_types = ["SimpleAgent", "BrowserAgent", "OrchestraAgent"]
        if config.get("type") not in valid_types:
            errors.append(f"Invalid agent type: {config.get('type')}")
        
        # Check tools
        if "tools" in config and not isinstance(config["tools"], list):
            errors.append("Tools must be a list")
        
        # Check capabilities
        if "capabilities" in config and not isinstance(config["capabilities"], list):
            errors.append("Capabilities must be a list")
        
        # Warnings for optional fields
        if "config" not in config:
            warnings.append("No configuration parameters specified")
        
        return {
            "config": config,
            "strict": strict,
            "result": {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "validation_score": 1.0 if len(errors) == 0 else 0.0,
                "recommendations": [
                    "Consider adding more specific configuration parameters",
                    "Ensure all required tools are available",
                    "Test the agent configuration before deployment"
                ]
            },
            "status": "success"
        }


class TemplateManagerTool(BaseTool):
    """Example template management tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="template_manager",
            description="Manage agent templates",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "action": {"type": "str", "description": "Action to perform"},
                "template_name": {"type": "str", "description": "Template name"}
            },
            return_type=dict
        )
    
    async def execute(self, action: str, template_name: str = None, **kwargs) -> dict:
        """Execute template management."""
        # Simulate template management
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if action == "list":
            return {
                "action": action,
                "template_name": template_name,
                "result": {
                    "templates": [
                        {"name": "simple_agent", "type": "SimpleAgent", "description": "Basic agent template"},
                        {"name": "browser_agent", "type": "BrowserAgent", "description": "Web automation agent template"},
                        {"name": "orchestra_agent", "type": "OrchestraAgent", "description": "Multi-agent coordination template"}
                    ],
                    "total_templates": 3
                },
                "status": "success"
            }
        elif action == "get":
            return {
                "action": action,
                "template_name": template_name,
                "result": {
                    "template": {
                        "name": template_name,
                        "type": template_name.replace("_agent", "Agent").title(),
                        "description": f"Template for {template_name}",
                        "config": {"max_iterations": 10, "timeout": 300},
                        "tools": ["web_search", "data_analysis"],
                        "capabilities": ["basic_task_execution", "tool_usage"]
                    }
                },
                "status": "success"
            }
        else:
            return {
                "action": action,
                "template_name": template_name,
                "result": {
                    "message": f"Action '{action}' completed successfully"
                },
                "status": "success"
            }


async def main():
    """Main example function."""
    # Setup logging
    setup_logging(level="INFO")
    
    print("🧠 Meta Agent Example")
    print("=" * 50)
    
    # Create configuration
    config = UnifiedConfig(
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.7
    )
    
    # Create tools
    tools = [
        AgentGeneratorTool(),
        ConfigValidatorTool(),
        TemplateManagerTool()
    ]
    
    # Create Meta Agent
    agent = MetaAgent(
        name="example_meta_agent",
        description="An example meta agent for automatic agent generation",
        config=config,
        tools=tools,
        template_path="examples/templates",
        generation_timeout=120,
        max_generated_agents=50
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Template path: {agent.template_path}")
    print(f"Generation timeout: {agent.generation_timeout}s")
    print(f"Max generated agents: {agent.max_generated_agents}")
    print(f"Tools available: {[tool._get_metadata().name for tool in tools]}")
    print()
    
    # Setup agent
    print("Setting up agent...")
    await agent.setup()
    print("✅ Agent setup completed")
    print()
    
    # Example 1: Simple Agent Generation
    print("🤖 Example 1: Simple Agent Generation")
    print("-" * 30)
    
    simple_generation_task = "Create a simple agent for data analysis tasks"
    
    result1 = await agent.run(
        simple_generation_task,
        generation_params={
            "agent_type": "SimpleAgent",
            "name": "data_analyzer",
            "capabilities": ["data_analysis", "report_generation"],
            "tools": ["csv_analysis", "chart_generation", "data_visualization"],
            "config": {"max_iterations": 15, "timeout": 600}
        }
    )
    
    print(f"Task: {result1['task']}")
    print(f"Success: {result1['success']}")
    print(f"Execution time: {result1['execution_time']:.2f}s")
    
    if result1['success']:
        print("Results:")
        for key, value in result1['result'].items():
            if key == 'agent_info':
                print(f"  {key}:")
                for info_key, info_value in value.items():
                    print(f"    {info_key}: {info_value}")
            elif key == 'test_result':
                print(f"  {key}:")
                for test_key, test_value in value.items():
                    print(f"    {test_key}: {test_value}")
            elif key == 'deployment_result':
                print(f"  {key}:")
                for deploy_key, deploy_value in value.items():
                    print(f"    {deploy_key}: {deploy_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 2: Browser Agent Generation
    print("🌐 Example 2: Browser Agent Generation")
    print("-" * 30)
    
    browser_generation_task = "Generate a browser agent for web scraping and automation"
    
    result2 = await agent.run(
        browser_generation_task,
        generation_params={
            "agent_type": "BrowserAgent",
            "name": "web_scraper",
            "capabilities": ["web_automation", "data_scraping", "form_filling"],
            "tools": ["playwright_browser", "web_scraping", "screenshot_capture"],
            "config": {
                "headless": True,
                "browser_type": "chromium",
                "viewport": {"width": 1920, "height": 1080}
            }
        }
    )
    
    print(f"Task: {result2['task']}")
    print(f"Success: {result2['success']}")
    print(f"Execution time: {result2['execution_time']:.2f}s")
    
    if result2['success']:
        print("Results:")
        for key, value in result2['result'].items():
            if key == 'agent_info':
                print(f"  {key}:")
                for info_key, info_value in value.items():
                    print(f"    {info_key}: {info_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 3: Orchestra Agent Generation
    print("🎼 Example 3: Orchestra Agent Generation")
    print("-" * 30)
    
    orchestra_generation_task = "Create an orchestra agent for managing multiple data processing agents"
    
    result3 = await agent.run(
        orchestra_generation_task,
        generation_params={
            "agent_type": "OrchestraAgent",
            "name": "data_orchestrator",
            "capabilities": ["multi_agent_coordination", "workflow_management", "task_distribution"],
            "tools": ["agent_coordinator", "workflow_manager", "result_aggregator"],
            "config": {
                "max_concurrent_agents": 5,
                "workflow_timeout": 1800,
                "retry_attempts": 3
            }
        }
    )
    
    print(f"Task: {result3['task']}")
    print(f"Success: {result3['success']}")
    print(f"Execution time: {result3['execution_time']:.2f}s")
    
    if result3['success']:
        print("Results:")
        for key, value in result3['result'].items():
            if key == 'agent_info':
                print(f"  {key}:")
                for info_key, info_value in value.items():
                    print(f"    {info_key}: {info_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 4: Natural Language Agent Generation
    print("💬 Example 4: Natural Language Agent Generation")
    print("-" * 30)
    
    natural_language_task = "Create an agent that can help with customer support by analyzing emails and generating responses"
    
    result4 = await agent.run(
        natural_language_task,
        generation_params={
            "name": "customer_support_agent",
            "capabilities": ["email_analysis", "response_generation", "sentiment_analysis"],
            "tools": ["email_processor", "nlp_analysis", "response_generator"],
            "config": {"max_iterations": 20, "temperature": 0.3}
        }
    )
    
    print(f"Task: {result4['task']}")
    print(f"Success: {result4['success']}")
    print(f"Execution time: {result4['execution_time']:.2f}s")
    
    if result4['success']:
        print("Results:")
        for key, value in result4['result'].items():
            if key == 'agent_info':
                print(f"  {key}:")
                for info_key, info_value in value.items():
                    print(f"    {info_key}: {info_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 5: Template Management
    print("📋 Example 5: Template Management")
    print("-" * 30)
    
    template_task = "List all available agent templates and show details for the simple agent template"
    
    result5 = await agent.run(
        template_task,
        generation_params={
            "action": "list_templates",
            "template_name": "simple_agent"
        }
    )
    
    print(f"Task: {result5['task']}")
    print(f"Success: {result5['success']}")
    print(f"Execution time: {result5['execution_time']:.2f}s")
    
    if result5['success']:
        print("Results:")
        for key, value in result5['result'].items():
            print(f"  {key}: {value}")
    
    print()
    
    # Show agent statistics
    print("📈 Agent Statistics")
    print("-" * 30)
    
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print()
    
    # Show generated agents
    print("🤖 Generated Agents")
    print("-" * 30)
    
    for agent_id, agent_info in agent.generated_agents.items():
        print(f"  {agent_id}: {agent_info['name']} ({agent_info['type']})")
        print(f"    Description: {agent_info['description']}")
        print(f"    Created: {agent_info['created_at']}")
        print(f"    Status: {agent_info['status']}")
        print()
    
    # Show generation history
    print("📋 Generation History")
    print("-" * 30)
    
    for i, generation in enumerate(agent.generation_history, 1):
        print(f"  {i}. {generation['name']} ({generation['type']}) - {generation['created_at']}")
    
    print()
    
    # Show available templates
    print("📄 Available Templates")
    print("-" * 30)
    
    for template_name, template_data in agent.agent_templates.items():
        print(f"  {template_name}: {template_data.get('description', 'No description')}")
    
    print()
    
    # Show agent patterns
    print("🔍 Agent Patterns")
    print("-" * 30)
    
    for pattern_name, pattern_data in agent.agent_patterns.items():
        print(f"  {pattern_name}: {pattern_data}")
    
    print()
    
    # Cleanup
    print("🧹 Cleaning up agent...")
    await agent.cleanup()
    print("✅ Agent cleanup completed")
    
    print()
    print("🎉 Meta Agent Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())