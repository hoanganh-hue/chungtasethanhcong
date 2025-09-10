"""
Test suite for agent implementations.

This module contains comprehensive tests for all agent types
in the unified framework.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.core.unified_agent import UnifiedAgent
from src.core.config import UnifiedConfig
from src.core.tool_registry import BaseTool, ToolMetadata, ToolDefinition, ToolCategory
from src.core.memory import UnifiedMemory
from src.core.state import AgentState
from src.agents.simple_agent import SimpleAgent
from src.agents.browser_agent import BrowserAgent
from src.agents.orchestra_agent import OrchestraAgent, WorkflowStatus, TaskDependency
from src.agents.meta_agent import MetaAgent
from src.utils.exceptions import AgentError, ToolError, OrchestrationError, MetaAgentError


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="mock_tool",
            description="Mock tool for testing",
            category=ToolCategory.UTILITY,
            version="1.0.0",
            author="Test"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={},
            return_type=str
        )
    
    async def execute(self, **kwargs) -> str:
        return "mock_result"


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock(spec=UnifiedConfig)
    config.model = "gpt-4o"
    config.max_tokens = 4096
    config.temperature = 0.7
    return config


@pytest.fixture
def mock_tools():
    """Create mock tools for testing."""
    return [MockTool()]


@pytest.fixture
def mock_memory():
    """Create a mock memory system for testing."""
    memory = Mock(spec=UnifiedMemory)
    memory.initialize = AsyncMock()
    memory.cleanup = AsyncMock()
    memory.store = AsyncMock()
    memory.get = AsyncMock(return_value=None)
    memory.store_execution = AsyncMock()
    memory.store_tool_usage = AsyncMock()
    return memory


@pytest.fixture
def mock_state():
    """Create a mock state system for testing."""
    state = Mock(spec=AgentState)
    state.update_state = Mock()
    state.get_state = Mock(return_value={"status": "idle"})
    return state


class TestSimpleAgent:
    """Test suite for SimpleAgent."""
    
    @pytest.mark.asyncio
    async def test_simple_agent_initialization(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test SimpleAgent initialization."""
        agent = SimpleAgent(
            name="test_simple",
            description="Test simple agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state,
            max_iterations=5,
            timeout=60
        )
        
        assert agent.name == "test_simple"
        assert agent.description == "Test simple agent"
        assert agent.max_iterations == 5
        assert agent.timeout == 60
        assert agent.current_iteration == 0
        assert not agent.initialized
    
    @pytest.mark.asyncio
    async def test_simple_agent_setup(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test SimpleAgent setup."""
        agent = SimpleAgent(
            name="test_simple",
            description="Test simple agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        assert agent.initialized
        assert hasattr(agent, 'execution_pipeline')
        assert len(agent.execution_pipeline) == 5
    
    @pytest.mark.asyncio
    async def test_simple_agent_task_execution(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test SimpleAgent task execution."""
        agent = SimpleAgent(
            name="test_simple",
            description="Test simple agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state,
            max_iterations=1
        )
        
        await agent.setup()
        
        result = await agent.run("Test task")
        
        assert result["agent"] == "test_simple"
        assert result["task"] == "Test task"
        assert result["success"] is True
        assert "execution_time" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_simple_agent_task_classification(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test SimpleAgent task classification."""
        agent = SimpleAgent(
            name="test_simple",
            description="Test simple agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        # Test search task classification
        task_type = agent._classify_task_type("Search for information about AI")
        assert task_type == "search"
        
        # Test analysis task classification
        task_type = agent._classify_task_type("Analyze this data")
        assert task_type == "analysis"
        
        # Test creation task classification
        task_type = agent._classify_task_type("Create a report")
        assert task_type == "creation"
        
        # Test file operation classification
        task_type = agent._classify_task_type("Read the file")
        assert task_type == "file_operation"
    
    @pytest.mark.asyncio
    async def test_simple_agent_tool_identification(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test SimpleAgent tool identification."""
        agent = SimpleAgent(
            name="test_simple",
            description="Test simple agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        # Test search tool identification
        tools = agent._identify_required_tools("Search for information")
        assert "web_search" in tools
        assert "google_search" in tools
        
        # Test file tool identification
        tools = agent._identify_required_tools("Read the file")
        assert "file_reader" in tools
        assert "file_writer" in tools
        
        # Test data tool identification
        tools = agent._identify_required_tools("Analyze the data")
        assert "data_analysis" in tools
        assert "csv_analysis" in tools


class TestBrowserAgent:
    """Test suite for BrowserAgent."""
    
    @pytest.mark.asyncio
    async def test_browser_agent_initialization(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test BrowserAgent initialization."""
        agent = BrowserAgent(
            name="test_browser",
            description="Test browser agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state,
            headless=True,
            browser_type="chromium",
            viewport={"width": 1920, "height": 1080}
        )
        
        assert agent.name == "test_browser"
        assert agent.headless is True
        assert agent.browser_type == "chromium"
        assert agent.viewport == {"width": 1920, "height": 1080}
        assert agent.browser is None
        assert agent.context is None
        assert agent.page is None
    
    @pytest.mark.asyncio
    async def test_browser_agent_setup(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test BrowserAgent setup."""
        agent = BrowserAgent(
            name="test_browser",
            description="Test browser agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        assert agent.initialized
        assert hasattr(agent, 'browser_pipeline')
        assert len(agent.browser_pipeline) == 6
    
    @pytest.mark.asyncio
    async def test_browser_agent_task_parsing(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test BrowserAgent task parsing."""
        agent = BrowserAgent(
            name="test_browser",
            description="Test browser agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        # Test navigation task parsing
        task = await agent._parse_browser_task("Navigate to https://example.com")
        assert task["task_type"] == "navigation"
        assert task["url"] == "https://example.com"
        
        # Test scraping task parsing
        task = await agent._parse_browser_task("Scrape data from the website")
        assert task["task_type"] == "scraping"
        
        # Test form automation task parsing
        task = await agent._parse_browser_task("Fill the form with data")
        assert task["task_type"] == "form_automation"
        
        # Test interaction task parsing
        task = await agent._parse_browser_task("Click the button")
        assert task["task_type"] == "interaction"
        
        # Test screenshot task parsing
        task = await agent._parse_browser_task("Take a screenshot")
        assert task["task_type"] == "screenshot"
    
    @pytest.mark.asyncio
    async def test_browser_agent_url_extraction(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test BrowserAgent URL extraction."""
        agent = BrowserAgent(
            name="test_browser",
            description="Test browser agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        # Test URL extraction
        url = agent._extract_url_from_task("Go to https://example.com and scrape data")
        assert url == "https://example.com"
        
        # Test no URL case
        url = agent._extract_url_from_task("Scrape data from the website")
        assert url is None
    
    @pytest.mark.asyncio
    async def test_browser_agent_browser_lifecycle(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test BrowserAgent browser lifecycle."""
        agent = BrowserAgent(
            name="test_browser",
            description="Test browser agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        # Test browser launch
        await agent._launch_browser({"browser_type": "chromium", "headless": True})
        assert agent.browser is not None
        assert agent.browser["type"] == "chromium"
        
        # Test context creation
        await agent._create_context({"viewport": {"width": 1920, "height": 1080}})
        assert agent.context is not None
        assert agent.context["viewport"] == {"width": 1920, "height": 1080}
        
        # Test page navigation
        await agent._navigate_to_page("https://example.com")
        assert agent.page is not None
        assert agent.page["url"] == "https://example.com"
        assert agent.current_url == "https://example.com"
        
        # Test browser cleanup
        await agent._cleanup_browser()
        assert agent.browser is None
        assert agent.context is None
        assert agent.page is None
        assert agent.current_url is None


class TestOrchestraAgent:
    """Test suite for OrchestraAgent."""
    
    @pytest.mark.asyncio
    async def test_orchestra_agent_initialization(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test OrchestraAgent initialization."""
        agent = OrchestraAgent(
            name="test_orchestra",
            description="Test orchestra agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state,
            max_concurrent_agents=3,
            workflow_timeout=600,
            retry_attempts=2
        )
        
        assert agent.name == "test_orchestra"
        assert agent.max_concurrent_agents == 3
        assert agent.workflow_timeout == 600
        assert agent.retry_attempts == 2
        assert len(agent.managed_agents) == 0
        assert len(agent.active_workflows) == 0
        assert len(agent.workflow_history) == 0
    
    @pytest.mark.asyncio
    async def test_orchestra_agent_setup(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test OrchestraAgent setup."""
        agent = OrchestraAgent(
            name="test_orchestra",
            description="Test orchestra agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        assert agent.initialized
        assert hasattr(agent, 'orchestration_pipeline')
        assert len(agent.orchestration_pipeline) == 7
        assert hasattr(agent, 'task_scheduler')
        assert agent.task_scheduler["scheduler_status"] == "initialized"
    
    @pytest.mark.asyncio
    async def test_orchestra_agent_workflow_initialization(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test OrchestraAgent workflow initialization."""
        agent = OrchestraAgent(
            name="test_orchestra",
            description="Test orchestra agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        orchestration_task = {
            "original_task": "Test orchestration",
            "orchestration_type": "coordination",
            "workflow_definition": {"tasks": []},
            "parameters": {}
        }
        
        workflow = await agent._initialize_workflow("test_workflow", orchestration_task)
        
        assert workflow["id"] == "test_workflow"
        assert workflow["status"] == WorkflowStatus.PENDING
        assert workflow["task"] == "Test orchestration"
        assert workflow["type"] == "coordination"
        assert "test_workflow" in agent.active_workflows
    
    @pytest.mark.asyncio
    async def test_orchestra_agent_workflow_definition_parsing(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test OrchestraAgent workflow definition parsing."""
        agent = OrchestraAgent(
            name="test_orchestra",
            description="Test orchestra agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        workflow_definition = {
            "tasks": [
                {
                    "id": "task1",
                    "agent_type": "SimpleAgent",
                    "task": "Test task 1",
                    "parameters": {"param1": "value1"},
                    "dependencies": [],
                    "dependency_type": "sequential"
                },
                {
                    "id": "task2",
                    "agent_type": "BrowserAgent",
                    "task": "Test task 2",
                    "parameters": {"param2": "value2"},
                    "dependencies": ["task1"],
                    "dependency_type": "parallel"
                }
            ]
        }
        
        tasks = await agent._parse_workflow_definition(workflow_definition)
        
        assert len(tasks) == 2
        assert tasks[0]["id"] == "task1"
        assert tasks[0]["agent_type"] == "SimpleAgent"
        assert tasks[0]["dependency_type"] == TaskDependency.SEQUENTIAL
        assert tasks[1]["id"] == "task2"
        assert tasks[1]["agent_type"] == "BrowserAgent"
        assert tasks[1]["dependency_type"] == TaskDependency.PARALLEL
    
    @pytest.mark.asyncio
    async def test_orchestra_agent_agent_creation(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test OrchestraAgent agent creation."""
        agent = OrchestraAgent(
            name="test_orchestra",
            description="Test orchestra agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        # Test SimpleAgent creation
        simple_agent = await agent._get_or_create_agent("SimpleAgent", "test_simple")
        assert simple_agent is not None
        assert simple_agent.name == "SimpleAgent_test_simple"
        assert "test_simple" in agent.managed_agents
        
        # Test BrowserAgent creation
        browser_agent = await agent._get_or_create_agent("BrowserAgent", "test_browser")
        assert browser_agent is not None
        assert browser_agent.name == "BrowserAgent_test_browser"
        assert "test_browser" in agent.managed_agents
        
        # Test agent reuse
        simple_agent_2 = await agent._get_or_create_agent("SimpleAgent", "test_simple")
        assert simple_agent_2 is simple_agent  # Should be the same instance


class TestMetaAgent:
    """Test suite for MetaAgent."""
    
    @pytest.mark.asyncio
    async def test_meta_agent_initialization(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent initialization."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state,
            template_path="test_templates",
            generation_timeout=120,
            max_generated_agents=50
        )
        
        assert agent.name == "test_meta"
        assert agent.template_path == "test_templates"
        assert agent.generation_timeout == 120
        assert agent.max_generated_agents == 50
        assert len(agent.generated_agents) == 0
        assert len(agent.agent_templates) == 0
        assert len(agent.generation_history) == 0
    
    @pytest.mark.asyncio
    async def test_meta_agent_setup(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent setup."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        assert agent.initialized
        assert hasattr(agent, 'meta_pipeline')
        assert len(agent.meta_pipeline) == 8
        assert len(agent.agent_templates) > 0  # Should have default templates
        assert len(agent.agent_patterns) > 0  # Should have default patterns
    
    @pytest.mark.asyncio
    async def test_meta_agent_generation_request_parsing(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent generation request parsing."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        meta_task = {
            "original_task": "Create a data analysis agent",
            "generation_params": {
                "agent_type": "SimpleAgent",
                "capabilities": ["data_analysis"],
                "tools": ["csv_analysis", "chart_generation"],
                "name": "data_analyzer"
            }
        }
        
        request = await agent._parse_generation_request(meta_task)
        
        assert request["description"] == "Create a data analysis agent"
        assert request["agent_type"] == "SimpleAgent"
        assert request["capabilities"] == ["data_analysis"]
        assert request["tools"] == ["csv_analysis", "chart_generation"]
        assert request["name"] == "data_analyzer"
    
    @pytest.mark.asyncio
    async def test_meta_agent_requirements_analysis(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent requirements analysis."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        generation_request = {
            "description": "Create a browser automation agent for web scraping",
            "agent_type": None,
            "capabilities": [],
            "tools": [],
            "config": {},
            "name": None
        }
        
        requirements = await agent._analyze_requirements(generation_request)
        
        assert requirements["agent_type"] == "BrowserAgent"
        assert "web_automation" in requirements["capabilities"]
        assert "playwright_browser" in requirements["tools"]
        assert requirements["name"] is not None
    
    @pytest.mark.asyncio
    async def test_meta_agent_template_selection(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent template selection."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        requirements = {
            "agent_type": "SimpleAgent",
            "capabilities": ["data_analysis"],
            "tools": ["csv_analysis"],
            "config": {},
            "name": "test_agent"
        }
        
        template = await agent._select_template(requirements)
        
        assert template is not None
        assert "name" in template
        assert "type" in template
        assert "config" in template
    
    @pytest.mark.asyncio
    async def test_meta_agent_configuration_generation(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent configuration generation."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        template = {
            "name": "SimpleAgent",
            "description": "A simple agent",
            "type": "SimpleAgent",
            "config": {"max_iterations": 10},
            "tools": ["web_search"],
            "capabilities": ["basic_task_execution"]
        }
        
        requirements = {
            "agent_type": "SimpleAgent",
            "capabilities": ["data_analysis"],
            "tools": ["csv_analysis"],
            "config": {"timeout": 300},
            "name": "data_analyzer",
            "description": "A data analysis agent"
        }
        
        config = await agent._generate_configuration(template, requirements)
        
        assert config["name"] == "data_analyzer"
        assert config["description"] == "A data analysis agent"
        assert config["type"] == "SimpleAgent"
        assert "data_analysis" in config["capabilities"]
        assert "csv_analysis" in config["tools"]
        assert config["config"]["timeout"] == 300
        assert config["generated_by"] == "test_meta"
    
    @pytest.mark.asyncio
    async def test_meta_agent_configuration_validation(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent configuration validation."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        # Test valid configuration
        valid_config = {
            "name": "test_agent",
            "description": "A test agent",
            "type": "SimpleAgent",
            "tools": ["web_search"],
            "capabilities": ["basic_task_execution"],
            "config": {"max_iterations": 10}
        }
        
        validation_result = await agent._validate_configuration(valid_config)
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        
        # Test invalid configuration
        invalid_config = {
            "name": "",  # Empty name
            "description": "A test agent",
            "type": "InvalidAgent",  # Invalid type
            "tools": "not_a_list",  # Invalid tools format
            "capabilities": ["basic_task_execution"],
            "config": {"max_iterations": 10}
        }
        
        validation_result = await agent._validate_configuration(invalid_config)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_meta_agent_agent_creation(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test MetaAgent agent creation."""
        agent = MetaAgent(
            name="test_meta",
            description="Test meta agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        config = {
            "name": "test_agent",
            "description": "A test agent",
            "type": "SimpleAgent",
            "tools": ["web_search"],
            "capabilities": ["basic_task_execution"],
            "config": {"max_iterations": 10}
        }
        
        agent_info = await agent._create_agent(config, "test_generation")
        
        assert agent_info["id"] == "test_generation"
        assert agent_info["name"] == "test_agent"
        assert agent_info["type"] == "SimpleAgent"
        assert agent_info["status"] == "created"
        assert "test_generation" in agent.generated_agents
        assert len(agent.generation_history) == 1


class TestAgentIntegration:
    """Integration tests for agent interactions."""
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test complete agent lifecycle."""
        agent = SimpleAgent(
            name="test_lifecycle",
            description="Test lifecycle agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        # Test initialization
        assert not agent.initialized
        assert agent.execution_count == 0
        
        # Test setup
        await agent.setup()
        assert agent.initialized
        
        # Test execution
        result = await agent.run("Test task")
        assert result["success"] is True
        assert agent.execution_count == 1
        
        # Test stats
        stats = agent.get_stats()
        assert stats["execution_count"] == 1
        assert stats["name"] == "test_lifecycle"
        
        # Test cleanup
        await agent.cleanup()
        assert not agent.initialized
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test agent error handling."""
        agent = SimpleAgent(
            name="test_error",
            description="Test error agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state,
            max_iterations=1
        )
        
        await agent.setup()
        
        # Test error handling in task execution
        with patch.object(agent, '_execute_with_iterations', side_effect=Exception("Test error")):
            result = await agent.run("Test task")
            assert result["success"] is False
            assert "Test error" in result["error"]
            assert agent.error_count == 1
    
    @pytest.mark.asyncio
    async def test_agent_memory_integration(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test agent memory integration."""
        agent = SimpleAgent(
            name="test_memory",
            description="Test memory agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        # Test memory storage
        await agent.store_memory("test_key", "test_value")
        mock_memory.store.assert_called_with("test_key", "test_value")
        
        # Test memory retrieval
        await agent.get_memory("test_key")
        mock_memory.get.assert_called_with("test_key")
    
    @pytest.mark.asyncio
    async def test_agent_tool_integration(self, mock_config, mock_tools, mock_memory, mock_state):
        """Test agent tool integration."""
        agent = SimpleAgent(
            name="test_tools",
            description="Test tools agent",
            config=mock_config,
            tools=mock_tools,
            memory=mock_memory,
            state=mock_state
        )
        
        await agent.setup()
        
        # Test tool usage
        result = await agent.use_tool("mock_tool", param1="value1")
        assert result == "mock_result"
        
        # Test tool error handling
        with patch.object(agent.tool_registry, 'get_tool', return_value=None):
            with pytest.raises(ToolError):
                await agent.use_tool("nonexistent_tool")


if __name__ == "__main__":
    pytest.main([__file__])