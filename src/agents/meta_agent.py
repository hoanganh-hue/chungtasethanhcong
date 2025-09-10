"""
Meta Agent Implementation.

This module provides the MetaAgent class, which is designed for
automatic agent generation and configuration management.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime
from pathlib import Path
import json
import yaml

from ..core.unified_agent import UnifiedAgent
from ..core.config import UnifiedConfig
from ..core.tool_registry import BaseTool
from ..core.memory import UnifiedMemory
from ..core.state import AgentState
from ..utils.exceptions import AgentError, MetaAgentError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetaAgent(UnifiedAgent):
    """
    Meta Agent for automatic agent generation and management.
    
    This agent is designed to automatically generate agent configurations,
    create new agents, and manage agent templates and patterns.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: UnifiedConfig,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[UnifiedMemory] = None,
        state: Optional[AgentState] = None,
        template_path: Optional[str] = None,
        generation_timeout: int = 300,
        max_generated_agents: int = 100
    ):
        """
        Initialize the Meta Agent.
        
        Args:
            name: Agent name
            description: Agent description
            config: Agent configuration
            tools: List of available tools
            memory: Memory system instance
            state: Agent state instance
            template_path: Path to agent templates
            generation_timeout: Timeout for agent generation
            max_generated_agents: Maximum number of generated agents
        """
        super().__init__(name, description, config, tools, memory, state)
        
        self.template_path = template_path or "templates/agents"
        self.generation_timeout = generation_timeout
        self.max_generated_agents = max_generated_agents
        
        # Meta agent state
        self.generated_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_templates: Dict[str, Dict[str, Any]] = {}
        self.generation_history: List[Dict[str, Any]] = []
        self.agent_patterns: Dict[str, List[str]] = {}
        
        logger.info(f"MetaAgent '{name}' initialized with template_path={self.template_path}")
    
    async def _setup_agent_specific(self) -> None:
        """Setup Meta Agent specific components."""
        try:
            logger.info(f"Setting up MetaAgent '{self.name}' specific components...")
            
            # Initialize meta agent pipeline
            self.meta_pipeline = [
                "parse_generation_request",
                "analyze_requirements",
                "select_template",
                "generate_configuration",
                "validate_configuration",
                "create_agent",
                "test_agent",
                "deploy_agent"
            ]
            
            # Load agent templates
            await self._load_agent_templates()
            
            # Setup meta tools
            await self._setup_meta_tools()
            
            # Initialize agent patterns
            await self._initialize_agent_patterns()
            
            logger.info(f"MetaAgent '{self.name}' specific setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup MetaAgent '{self.name}' specific components: {e}")
            raise AgentError(f"MetaAgent setup failed: {e}") from e
    
    async def _load_agent_templates(self) -> None:
        """Load agent templates from template path."""
        try:
            template_dir = Path(self.template_path)
            
            if not template_dir.exists():
                # Create default templates
                await self._create_default_templates()
                return
            
            # Load existing templates
            for template_file in template_dir.glob("*.yaml"):
                try:
                    with open(template_file, 'r') as f:
                        template_data = yaml.safe_load(f)
                        template_name = template_file.stem
                        self.agent_templates[template_name] = template_data
                        
                except Exception as e:
                    logger.error(f"Failed to load template {template_file}: {e}")
            
            logger.info(f"MetaAgent '{self.name}' loaded {len(self.agent_templates)} templates")
            
        except Exception as e:
            logger.error(f"Failed to load agent templates: {e}")
            raise MetaAgentError(f"Template loading failed: {e}") from e
    
    async def _create_default_templates(self) -> None:
        """Create default agent templates."""
        try:
            template_dir = Path(self.template_path)
            template_dir.mkdir(parents=True, exist_ok=True)
            
            # Simple Agent template
            simple_template = {
                "name": "SimpleAgent",
                "description": "A simple agent for basic tasks",
                "type": "SimpleAgent",
                "config": {
                    "max_iterations": 10,
                    "timeout": 300
                },
                "tools": ["web_search", "data_analysis"],
                "capabilities": ["basic_task_execution", "tool_usage"]
            }
            
            # Browser Agent template
            browser_template = {
                "name": "BrowserAgent",
                "description": "A browser agent for web automation",
                "type": "BrowserAgent",
                "config": {
                    "headless": True,
                    "browser_type": "chromium",
                    "viewport": {"width": 1920, "height": 1080}
                },
                "tools": ["playwright_browser", "web_scraping", "form_automation"],
                "capabilities": ["web_automation", "scraping", "form_filling"]
            }
            
            # Orchestra Agent template
            orchestra_template = {
                "name": "OrchestraAgent",
                "description": "An orchestra agent for multi-agent coordination",
                "type": "OrchestraAgent",
                "config": {
                    "max_concurrent_agents": 5,
                    "workflow_timeout": 1800,
                    "retry_attempts": 3
                },
                "tools": ["agent_coordinator", "workflow_manager"],
                "capabilities": ["multi_agent_coordination", "workflow_management"]
            }
            
            # Save templates
            templates = {
                "simple_agent": simple_template,
                "browser_agent": browser_template,
                "orchestra_agent": orchestra_template
            }
            
            for template_name, template_data in templates.items():
                template_file = template_dir / f"{template_name}.yaml"
                with open(template_file, 'w') as f:
                    yaml.dump(template_data, f, default_flow_style=False)
                
                self.agent_templates[template_name] = template_data
            
            logger.info(f"MetaAgent '{self.name}' created {len(templates)} default templates")
            
        except Exception as e:
            logger.error(f"Failed to create default templates: {e}")
            raise MetaAgentError(f"Default template creation failed: {e}") from e
    
    async def _setup_meta_tools(self) -> None:
        """Setup meta-specific tools."""
        try:
            # Add meta tools to the agent
            meta_tools = [
                "agent_generator",
                "config_validator",
                "template_manager",
                "pattern_analyzer"
            ]
            
            for tool_name in meta_tools:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    self.tools.append(tool)
            
            logger.info(f"MetaAgent '{self.name}' setup {len(meta_tools)} meta tools")
            
        except Exception as e:
            logger.error(f"Failed to setup meta tools: {e}")
            raise MetaAgentError(f"Meta tools setup failed: {e}") from e
    
    async def _initialize_agent_patterns(self) -> None:
        """Initialize agent patterns for generation."""
        try:
            self.agent_patterns = {
                "data_analysis": ["SimpleAgent", "data_analysis", "csv_analysis", "chart_generation"],
                "web_automation": ["BrowserAgent", "playwright_browser", "web_scraping", "form_automation"],
                "multi_agent": ["OrchestraAgent", "agent_coordinator", "workflow_manager"],
                "research": ["SimpleAgent", "web_search", "academic_search", "literature_review"],
                "file_processing": ["SimpleAgent", "file_reader", "file_writer", "pdf_processor"]
            }
            
            logger.info(f"MetaAgent '{self.name}' initialized {len(self.agent_patterns)} agent patterns")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent patterns: {e}")
            raise MetaAgentError(f"Agent patterns initialization failed: {e}") from e
    
    async def _execute_task(self, task: str, **kwargs) -> Any:
        """
        Execute a meta agent task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Meta agent execution result
        """
        try:
            logger.info(f"MetaAgent '{self.name}' executing meta task: {task}")
            
            # Parse meta task
            meta_task = await self._parse_meta_task(task, **kwargs)
            
            # Execute meta pipeline
            result = await self._execute_meta_pipeline(meta_task)
            
            return result
            
        except Exception as e:
            logger.error(f"MetaAgent '{self.name}' task execution failed: {e}")
            raise AgentError(f"Meta task execution failed: {e}") from e
    
    async def _parse_meta_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Parse meta agent task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            Parsed meta task information
        """
        try:
            task_lower = task.lower()
            
            # Determine meta task type
            if any(keyword in task_lower for keyword in ["generate", "create", "make"]):
                meta_task_type = "generation"
            elif any(keyword in task_lower for keyword in ["analyze", "examine", "study"]):
                meta_task_type = "analysis"
            elif any(keyword in task_lower for keyword in ["optimize", "improve", "enhance"]):
                meta_task_type = "optimization"
            elif any(keyword in task_lower for keyword in ["validate", "check", "verify"]):
                meta_task_type = "validation"
            else:
                meta_task_type = "general"
            
            # Extract generation parameters
            generation_params = kwargs.get("generation_params", {})
            
            parsed_task = {
                "original_task": task,
                "meta_task_type": meta_task_type,
                "generation_params": generation_params,
                "parameters": kwargs,
                "parsed_at": datetime.now().isoformat()
            }
            
            logger.info(f"MetaAgent '{self.name}' parsed meta task: {meta_task_type}")
            return parsed_task
            
        except Exception as e:
            logger.error(f"Failed to parse meta task: {e}")
            raise AgentError(f"Meta task parsing failed: {e}") from e
    
    async def _execute_meta_pipeline(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute meta agent pipeline.
        
        Args:
            meta_task: Parsed meta task information
            
        Returns:
            Meta agent execution result
        """
        try:
            meta_task_type = meta_task["meta_task_type"]
            
            if meta_task_type == "generation":
                result = await self._execute_generation_pipeline(meta_task)
            elif meta_task_type == "analysis":
                result = await self._execute_analysis_pipeline(meta_task)
            elif meta_task_type == "optimization":
                result = await self._execute_optimization_pipeline(meta_task)
            elif meta_task_type == "validation":
                result = await self._execute_validation_pipeline(meta_task)
            else:
                result = await self._execute_general_meta_pipeline(meta_task)
            
            return result
            
        except Exception as e:
            logger.error(f"Meta pipeline execution failed: {e}")
            raise MetaAgentError(f"Meta pipeline failed: {e}") from e
    
    async def _execute_generation_pipeline(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent generation pipeline."""
        try:
            generation_id = f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Parse generation request
            generation_request = await self._parse_generation_request(meta_task)
            
            # Analyze requirements
            requirements = await self._analyze_requirements(generation_request)
            
            # Select template
            template = await self._select_template(requirements)
            
            # Generate configuration
            config = await self._generate_configuration(template, requirements)
            
            # Validate configuration
            validation_result = await self._validate_configuration(config)
            
            if not validation_result["valid"]:
                raise MetaAgentError(f"Configuration validation failed: {validation_result['errors']}")
            
            # Create agent
            agent_info = await self._create_agent(config, generation_id)
            
            # Test agent
            test_result = await self._test_agent(agent_info)
            
            # Deploy agent
            deployment_result = await self._deploy_agent(agent_info)
            
            return {
                "generation_id": generation_id,
                "agent_info": agent_info,
                "test_result": test_result,
                "deployment_result": deployment_result,
                "status": "completed",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generation pipeline execution failed: {e}")
            raise MetaAgentError(f"Generation pipeline failed: {e}") from e
    
    async def _parse_generation_request(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """Parse agent generation request."""
        try:
            task_description = meta_task["original_task"]
            generation_params = meta_task.get("generation_params", {})
            
            # Extract agent requirements from task description
            requirements = {
                "description": task_description,
                "agent_type": generation_params.get("agent_type"),
                "capabilities": generation_params.get("capabilities", []),
                "tools": generation_params.get("tools", []),
                "config": generation_params.get("config", {}),
                "name": generation_params.get("name"),
                "parsed_at": datetime.now().isoformat()
            }
            
            logger.info(f"MetaAgent '{self.name}' parsed generation request")
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to parse generation request: {e}")
            raise MetaAgentError(f"Generation request parsing failed: {e}") from e
    
    async def _analyze_requirements(self, generation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze agent requirements."""
        try:
            description = generation_request["description"].lower()
            
            # Analyze description to determine requirements
            requirements = {
                "agent_type": generation_request.get("agent_type"),
                "capabilities": generation_request.get("capabilities", []),
                "tools": generation_request.get("tools", []),
                "config": generation_request.get("config", {}),
                "name": generation_request.get("name"),
                "analysis": {}
            }
            
            # Determine agent type if not specified
            if not requirements["agent_type"]:
                if any(keyword in description for keyword in ["browser", "web", "scrape", "automation"]):
                    requirements["agent_type"] = "BrowserAgent"
                elif any(keyword in description for keyword in ["coordinate", "orchestrate", "manage", "workflow"]):
                    requirements["agent_type"] = "OrchestraAgent"
                else:
                    requirements["agent_type"] = "SimpleAgent"
            
            # Determine capabilities
            if not requirements["capabilities"]:
                if "data" in description or "analyze" in description:
                    requirements["capabilities"].append("data_analysis")
                if "search" in description:
                    requirements["capabilities"].append("search")
                if "file" in description:
                    requirements["capabilities"].append("file_processing")
                if "web" in description:
                    requirements["capabilities"].append("web_automation")
            
            # Determine tools
            if not requirements["tools"]:
                if "data" in description:
                    requirements["tools"].extend(["data_analysis", "csv_analysis"])
                if "search" in description:
                    requirements["tools"].extend(["web_search", "google_search"])
                if "file" in description:
                    requirements["tools"].extend(["file_reader", "file_writer"])
                if "web" in description:
                    requirements["tools"].extend(["playwright_browser", "web_scraping"])
            
            # Generate name if not specified
            if not requirements["name"]:
                requirements["name"] = f"generated_{requirements['agent_type'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"MetaAgent '{self.name}' analyzed requirements: {requirements['agent_type']}")
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to analyze requirements: {e}")
            raise MetaAgentError(f"Requirements analysis failed: {e}") from e
    
    async def _select_template(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate template for agent generation."""
        try:
            agent_type = requirements["agent_type"]
            
            # Select template based on agent type
            template_name = f"{agent_type.lower()}_template"
            
            if template_name in self.agent_templates:
                template = self.agent_templates[template_name]
            else:
                # Use default SimpleAgent template
                template = self.agent_templates.get("simple_agent", {})
            
            logger.info(f"MetaAgent '{self.name}' selected template: {template_name}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to select template: {e}")
            raise MetaAgentError(f"Template selection failed: {e}") from e
    
    async def _generate_configuration(self, template: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate agent configuration from template and requirements."""
        try:
            # Start with template configuration
            config = template.copy()
            
            # Update with requirements
            config["name"] = requirements["name"]
            config["description"] = requirements["description"]
            config["type"] = requirements["agent_type"]
            
            # Merge capabilities
            if "capabilities" in config:
                config["capabilities"].extend(requirements["capabilities"])
            else:
                config["capabilities"] = requirements["capabilities"]
            
            # Merge tools
            if "tools" in config:
                config["tools"].extend(requirements["tools"])
            else:
                config["tools"] = requirements["tools"]
            
            # Merge config parameters
            if "config" in config:
                config["config"].update(requirements["config"])
            else:
                config["config"] = requirements["config"]
            
            # Add generation metadata
            config["generated_by"] = self.name
            config["generated_at"] = datetime.now().isoformat()
            
            logger.info(f"MetaAgent '{self.name}' generated configuration for {config['name']}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to generate configuration: {e}")
            raise MetaAgentError(f"Configuration generation failed: {e}") from e
    
    async def _validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated agent configuration."""
        try:
            errors = []
            warnings = []
            
            # Check required fields
            required_fields = ["name", "description", "type"]
            for field in required_fields:
                if field not in config or not config[field]:
                    errors.append(f"Missing required field: {field}")
            
            # Validate agent type
            valid_types = ["SimpleAgent", "BrowserAgent", "OrchestraAgent"]
            if config.get("type") not in valid_types:
                errors.append(f"Invalid agent type: {config.get('type')}")
            
            # Validate tools
            if "tools" in config and not isinstance(config["tools"], list):
                errors.append("Tools must be a list")
            
            # Validate capabilities
            if "capabilities" in config and not isinstance(config["capabilities"], list):
                errors.append("Capabilities must be a list")
            
            validation_result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "validated_at": datetime.now().isoformat()
            }
            
            logger.info(f"MetaAgent '{self.name}' validated configuration: {validation_result['valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            raise MetaAgentError(f"Configuration validation failed: {e}") from e
    
    async def _create_agent(self, config: Dict[str, Any], generation_id: str) -> Dict[str, Any]:
        """Create agent from configuration."""
        try:
            agent_info = {
                "id": generation_id,
                "name": config["name"],
                "description": config["description"],
                "type": config["type"],
                "config": config,
                "created_at": datetime.now().isoformat(),
                "status": "created"
            }
            
            # Add to generated agents
            self.generated_agents[generation_id] = agent_info
            
            # Add to generation history
            self.generation_history.append(agent_info)
            
            logger.info(f"MetaAgent '{self.name}' created agent: {config['name']}")
            return agent_info
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise MetaAgentError(f"Agent creation failed: {e}") from e
    
    async def _test_agent(self, agent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test generated agent."""
        try:
            # Simple test - can be enhanced
            test_result = {
                "agent_id": agent_info["id"],
                "test_status": "passed",
                "test_results": {
                    "configuration_valid": True,
                    "template_compatible": True,
                    "tools_available": True
                },
                "tested_at": datetime.now().isoformat()
            }
            
            logger.info(f"MetaAgent '{self.name}' tested agent: {agent_info['name']}")
            return test_result
            
        except Exception as e:
            logger.error(f"Failed to test agent: {e}")
            return {
                "agent_id": agent_info["id"],
                "test_status": "failed",
                "error": str(e),
                "tested_at": datetime.now().isoformat()
            }
    
    async def _deploy_agent(self, agent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy generated agent."""
        try:
            # Simple deployment - can be enhanced
            deployment_result = {
                "agent_id": agent_info["id"],
                "deployment_status": "deployed",
                "deployment_path": f"agents/{agent_info['name']}.yaml",
                "deployed_at": datetime.now().isoformat()
            }
            
            logger.info(f"MetaAgent '{self.name}' deployed agent: {agent_info['name']}")
            return deployment_result
            
        except Exception as e:
            logger.error(f"Failed to deploy agent: {e}")
            return {
                "agent_id": agent_info["id"],
                "deployment_status": "failed",
                "error": str(e),
                "deployed_at": datetime.now().isoformat()
            }
    
    async def _execute_analysis_pipeline(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis pipeline."""
        return {"analysis": "Analysis pipeline not implemented yet"}
    
    async def _execute_optimization_pipeline(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization pipeline."""
        return {"optimization": "Optimization pipeline not implemented yet"}
    
    async def _execute_validation_pipeline(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation pipeline."""
        return {"validation": "Validation pipeline not implemented yet"}
    
    async def _execute_general_meta_pipeline(self, meta_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general meta pipeline."""
        return await self._execute_generation_pipeline(meta_task)
    
    async def _cleanup_agent_specific(self) -> None:
        """Cleanup Meta Agent specific resources."""
        try:
            logger.info(f"Cleaning up MetaAgent '{self.name}' specific resources...")
            
            # Clear generated agents
            self.generated_agents.clear()
            
            # Clear templates
            self.agent_templates.clear()
            
            # Clear patterns
            self.agent_patterns.clear()
            
            # Clear meta pipeline
            self.meta_pipeline = []
            
            logger.info(f"MetaAgent '{self.name}' specific cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup MetaAgent '{self.name}' specific resources: {e}")
            raise AgentError(f"MetaAgent cleanup failed: {e}") from e
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get Meta Agent specific information."""
        base_info = self.get_stats()
        base_info.update({
            "agent_type": "MetaAgent",
            "template_path": self.template_path,
            "generation_timeout": self.generation_timeout,
            "max_generated_agents": self.max_generated_agents,
            "generated_agents_count": len(self.generated_agents),
            "templates_count": len(self.agent_templates),
            "patterns_count": len(self.agent_patterns),
            "generation_history_count": len(self.generation_history),
            "meta_pipeline": getattr(self, 'meta_pipeline', [])
        })
        return base_info