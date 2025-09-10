"""
Dynamic Agent Creation System for OpenManus-Youtu Integrated Framework
Create and manage agents dynamically at runtime
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Type, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import inspect
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Dynamic agent types."""
    CCCD = "cccd"
    TAX = "tax"
    DATA_ANALYSIS = "data_analysis"
    WEB_AUTOMATION = "web_automation"
    GENERAL = "general"
    CUSTOM = "custom"

class AgentCapability(Enum):
    """Agent capabilities."""
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    MEMORY = "memory"
    TOOL_USAGE = "tool_usage"
    MULTI_MODAL = "multi_modal"
    CODE_GENERATION = "code_generation"
    DATA_PROCESSING = "data_processing"
    WEB_SCRAPING = "web_scraping"

@dataclass
class AgentConfiguration:
    """Dynamic agent configuration."""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    agent_type: AgentType = AgentType.GENERAL
    capabilities: List[AgentCapability] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    model_config: Dict[str, Any] = field(default_factory=dict)
    memory_config: Dict[str, Any] = field(default_factory=dict)
    behavior_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class AgentTemplate:
    """Agent creation template."""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    agent_type: AgentType = AgentType.GENERAL
    default_capabilities: List[AgentCapability] = field(default_factory=list)
    default_tools: List[str] = field(default_factory=list)
    default_config: Dict[str, Any] = field(default_factory=dict)
    creation_function: Optional[Callable] = None

class DynamicAgent(ABC):
    """Base class for dynamically created agents."""
    
    def __init__(self, config: AgentConfiguration):
        self.config = config
        self.status = "idle"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.memory = {}
        self.tools = {}
        self.conversation_history = []
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def execute_task(self, task_type: str, parameters: Dict[str, Any]) -> Any:
        """Execute a task."""
        pass
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message."""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        self.status = "inactive"
        logger.info(f"Agent {self.config.agent_id} cleaned up")

class DynamicAgentFactory:
    """Factory for creating dynamic agents."""
    
    def __init__(self):
        self.agent_templates: Dict[str, AgentTemplate] = {}
        self.active_agents: Dict[str, DynamicAgent] = {}
        self.agent_registry: Dict[str, Type[DynamicAgent]] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default agent templates."""
        
        # CCCD Agent Template
        cccd_template = AgentTemplate(
            name="CCCD Agent Template",
            description="Template for CCCD generation and validation agents",
            agent_type=AgentType.CCCD,
            default_capabilities=[
                AgentCapability.FUNCTION_CALLING,
                AgentCapability.MEMORY,
                AgentCapability.DATA_PROCESSING
            ],
            default_tools=["cccd_generator", "cccd_validator", "data_formatter"],
            default_config={
                "model": "gemini-2.0-flash",
                "temperature": 0.7,
                "max_tokens": 2048,
                "specialization": "cccd_processing"
            }
        )
        self.agent_templates["cccd"] = cccd_template
        
        # Tax Agent Template
        tax_template = AgentTemplate(
            name="Tax Agent Template",
            description="Template for tax lookup and validation agents",
            agent_type=AgentType.TAX,
            default_capabilities=[
                AgentCapability.FUNCTION_CALLING,
                AgentCapability.WEB_SCRAPING,
                AgentCapability.DATA_PROCESSING
            ],
            default_tools=["tax_lookup", "web_scraper", "data_validator"],
            default_config={
                "model": "gemini-2.0-flash",
                "temperature": 0.5,
                "max_tokens": 1024,
                "specialization": "tax_processing"
            }
        )
        self.agent_templates["tax"] = tax_template
        
        # Data Analysis Agent Template
        data_template = AgentTemplate(
            name="Data Analysis Agent Template",
            description="Template for data analysis and processing agents",
            agent_type=AgentType.DATA_ANALYSIS,
            default_capabilities=[
                AgentCapability.DATA_PROCESSING,
                AgentCapability.CODE_GENERATION,
                AgentCapability.MEMORY
            ],
            default_tools=["data_analyzer", "chart_generator", "statistics_calculator"],
            default_config={
                "model": "gemini-2.0-flash",
                "temperature": 0.3,
                "max_tokens": 4096,
                "specialization": "data_analysis"
            }
        )
        self.agent_templates["data_analysis"] = data_template
        
        # Web Automation Agent Template
        web_template = AgentTemplate(
            name="Web Automation Agent Template",
            description="Template for web automation and scraping agents",
            agent_type=AgentType.WEB_AUTOMATION,
            default_capabilities=[
                AgentCapability.WEB_SCRAPING,
                AgentCapability.TOOL_USAGE,
                AgentCapability.MEMORY
            ],
            default_tools=["browser_controller", "web_scraper", "form_automator"],
            default_config={
                "model": "gemini-2.0-flash",
                "temperature": 0.6,
                "max_tokens": 1536,
                "specialization": "web_automation"
            }
        )
        self.agent_templates["web_automation"] = web_template
        
        # General Agent Template
        general_template = AgentTemplate(
            name="General Agent Template",
            description="Template for general purpose agents",
            agent_type=AgentType.GENERAL,
            default_capabilities=[
                AgentCapability.FUNCTION_CALLING,
                AgentCapability.STREAMING,
                AgentCapability.MEMORY
            ],
            default_tools=["general_processor", "text_analyzer", "response_generator"],
            default_config={
                "model": "gemini-2.0-flash",
                "temperature": 0.7,
                "max_tokens": 2048,
                "specialization": "general_purpose"
            }
        )
        self.agent_templates["general"] = general_template
    
    def register_agent_class(self, agent_type: AgentType, agent_class: Type[DynamicAgent]) -> None:
        """Register an agent class for dynamic creation."""
        self.agent_registry[agent_type.value] = agent_class
        logger.info(f"Registered agent class: {agent_type.value}")
    
    def create_agent_from_template(self, template_name: str, custom_config: Dict[str, Any] = None) -> Optional[DynamicAgent]:
        """Create an agent from a template."""
        if template_name not in self.agent_templates:
            logger.error(f"Template not found: {template_name}")
            return None
        
        template = self.agent_templates[template_name]
        
        # Merge template config with custom config
        config = template.default_config.copy()
        if custom_config:
            config.update(custom_config)
        
        # Create agent configuration
        agent_config = AgentConfiguration(
            name=config.get("name", f"{template.name} Instance"),
            description=config.get("description", template.description),
            agent_type=template.agent_type,
            capabilities=template.default_capabilities.copy(),
            tools=template.default_tools.copy(),
            model_config=config.get("model_config", {}),
            memory_config=config.get("memory_config", {}),
            behavior_config=config.get("behavior_config", {})
        )
        
        # Create agent instance
        agent_class = self.agent_registry.get(template.agent_type.value)
        if not agent_class:
            logger.error(f"Agent class not registered: {template.agent_type.value}")
            return None
        
        try:
            agent = agent_class(agent_config)
            self.active_agents[agent_config.agent_id] = agent
            logger.info(f"Created agent from template: {agent_config.agent_id}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return None
    
    def create_custom_agent(self, name: str, description: str, capabilities: List[AgentCapability],
                          tools: List[str], config: Dict[str, Any]) -> Optional[DynamicAgent]:
        """Create a custom agent with specified configuration."""
        
        agent_config = AgentConfiguration(
            name=name,
            description=description,
            agent_type=AgentType.CUSTOM,
            capabilities=capabilities,
            tools=tools,
            model_config=config.get("model_config", {}),
            memory_config=config.get("memory_config", {}),
            behavior_config=config.get("behavior_config", {})
        )
        
        # Use general agent class for custom agents
        agent_class = self.agent_registry.get("general")
        if not agent_class:
            logger.error("General agent class not registered")
            return None
        
        try:
            agent = agent_class(agent_config)
            self.active_agents[agent_config.agent_id] = agent
            logger.info(f"Created custom agent: {agent_config.agent_id}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create custom agent: {e}")
            return None
    
    async def create_agent_from_description(self, description: str, requirements: Dict[str, Any] = None) -> Optional[DynamicAgent]:
        """Create an agent from natural language description."""
        
        # Analyze description to determine agent type and capabilities
        agent_type = self._analyze_description_for_type(description)
        capabilities = self._analyze_description_for_capabilities(description)
        tools = self._analyze_description_for_tools(description)
        
        # Create configuration
        config = {
            "name": requirements.get("name", f"Auto-generated {agent_type.value} Agent"),
            "description": description,
            "model_config": requirements.get("model_config", {}),
            "memory_config": requirements.get("memory_config", {}),
            "behavior_config": requirements.get("behavior_config", {})
        }
        
        if agent_type in [AgentType.CCCD, AgentType.TAX, AgentType.DATA_ANALYSIS, AgentType.WEB_AUTOMATION, AgentType.GENERAL]:
            return self.create_agent_from_template(agent_type.value, config)
        else:
            return self.create_custom_agent(
                config["name"],
                description,
                capabilities,
                tools,
                config
            )
    
    def _analyze_description_for_type(self, description: str) -> AgentType:
        """Analyze description to determine agent type."""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ["cccd", "căn cước", "thẻ căn cước"]):
            return AgentType.CCCD
        elif any(keyword in description_lower for keyword in ["thuế", "tax", "mã số thuế"]):
            return AgentType.TAX
        elif any(keyword in description_lower for keyword in ["phân tích", "data", "dữ liệu", "analysis"]):
            return AgentType.DATA_ANALYSIS
        elif any(keyword in description_lower for keyword in ["web", "scraping", "automation", "tự động"]):
            return AgentType.WEB_AUTOMATION
        else:
            return AgentType.GENERAL
    
    def _analyze_description_for_capabilities(self, description: str) -> List[AgentCapability]:
        """Analyze description to determine required capabilities."""
        capabilities = []
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ["function", "chức năng", "tool", "công cụ"]):
            capabilities.append(AgentCapability.FUNCTION_CALLING)
        
        if any(keyword in description_lower for keyword in ["stream", "real-time", "thời gian thực"]):
            capabilities.append(AgentCapability.STREAMING)
        
        if any(keyword in description_lower for keyword in ["memory", "nhớ", "lưu trữ"]):
            capabilities.append(AgentCapability.MEMORY)
        
        if any(keyword in description_lower for keyword in ["code", "lập trình", "programming"]):
            capabilities.append(AgentCapability.CODE_GENERATION)
        
        if any(keyword in description_lower for keyword in ["data", "dữ liệu", "processing"]):
            capabilities.append(AgentCapability.DATA_PROCESSING)
        
        if any(keyword in description_lower for keyword in ["web", "scraping", "thu thập"]):
            capabilities.append(AgentCapability.WEB_SCRAPING)
        
        return capabilities if capabilities else [AgentCapability.FUNCTION_CALLING, AgentCapability.MEMORY]
    
    def _analyze_description_for_tools(self, description: str) -> List[str]:
        """Analyze description to determine required tools."""
        tools = []
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ["cccd", "căn cước"]):
            tools.extend(["cccd_generator", "cccd_validator"])
        
        if any(keyword in description_lower for keyword in ["thuế", "tax"]):
            tools.extend(["tax_lookup", "web_scraper"])
        
        if any(keyword in description_lower for keyword in ["phân tích", "analysis"]):
            tools.extend(["data_analyzer", "chart_generator"])
        
        if any(keyword in description_lower for keyword in ["web", "scraping"]):
            tools.extend(["browser_controller", "web_scraper"])
        
        return tools if tools else ["general_processor"]
    
    def get_agent(self, agent_id: str) -> Optional[DynamicAgent]:
        """Get an active agent by ID."""
        return self.active_agents.get(agent_id)
    
    def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all active agents."""
        return [
            {
                "agent_id": agent.config.agent_id,
                "name": agent.config.name,
                "type": agent.config.agent_type.value,
                "status": agent.status,
                "created_at": agent.created_at.isoformat(),
                "last_activity": agent.last_activity.isoformat()
            }
            for agent in self.active_agents.values()
        ]
    
    async def destroy_agent(self, agent_id: str) -> bool:
        """Destroy an active agent."""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            await agent.cleanup()
            del self.active_agents[agent_id]
            logger.info(f"Destroyed agent: {agent_id}")
            return True
        return False
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Get factory statistics."""
        return {
            "total_templates": len(self.agent_templates),
            "active_agents": len(self.active_agents),
            "registered_classes": len(self.agent_registry),
            "agent_types": {
                agent_type.value: len([a for a in self.active_agents.values() if a.config.agent_type == agent_type])
                for agent_type in AgentType
            }
        }

# Global dynamic agent factory
dynamic_agent_factory = DynamicAgentFactory()

# Convenience functions
def create_agent_from_template(template_name: str, custom_config: Dict[str, Any] = None) -> Optional[DynamicAgent]:
    """Create an agent from a template."""
    return dynamic_agent_factory.create_agent_from_template(template_name, custom_config)

def create_custom_agent(name: str, description: str, capabilities: List[AgentCapability],
                       tools: List[str], config: Dict[str, Any]) -> Optional[DynamicAgent]:
    """Create a custom agent."""
    return dynamic_agent_factory.create_custom_agent(name, description, capabilities, tools, config)

async def create_agent_from_description(description: str, requirements: Dict[str, Any] = None) -> Optional[DynamicAgent]:
    """Create an agent from natural language description."""
    return await dynamic_agent_factory.create_agent_from_description(description, requirements)

def get_active_agent(agent_id: str) -> Optional[DynamicAgent]:
    """Get an active agent."""
    return dynamic_agent_factory.get_agent(agent_id)

def list_all_agents() -> List[Dict[str, Any]]:
    """List all active agents."""
    return dynamic_agent_factory.list_active_agents()