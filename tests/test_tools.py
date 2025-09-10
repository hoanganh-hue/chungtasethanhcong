"""
Test suite for tool implementations.

This module contains comprehensive tests for all tool types
in the unified framework.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.tools.base_tool import BaseTool, ToolMetadata, ToolDefinition, ToolParameter, ToolCategory, ToolRegistry
from src.tools.web_tools import WebTools
from src.tools.search_tools import SearchTools
from src.tools.analysis_tools import AnalysisTools
from src.tools.data_tools import DataTools
from src.tools.file_tools import FileTools
from src.tools.automation_tools import AutomationTools
from src.tools.communication_tools import CommunicationTools
from src.tools.system_tools import SystemTools
from src.utils.exceptions import ToolError


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
            parameters={
                "test_param": ToolParameter(
                    name="test_param",
                    type=str,
                    description="Test parameter",
                    required=True
                )
            },
            return_type=str
        )
    
    async def _execute(self, **kwargs) -> str:
        return "mock_result"


class TestBaseTool:
    """Test suite for BaseTool."""
    
    @pytest.mark.asyncio
    async def test_base_tool_initialization(self):
        """Test BaseTool initialization."""
        tool = MockTool()
        
        assert tool.execution_count == 0
        assert tool.total_execution_time == 0.0
        assert tool.error_count == 0
        assert tool.last_executed is None
        assert tool.config == {}
    
    @pytest.mark.asyncio
    async def test_base_tool_execution(self):
        """Test BaseTool execution."""
        tool = MockTool()
        
        result = await tool.execute(test_param="test_value")
        
        assert result == "mock_result"
        assert tool.execution_count == 1
        assert tool.last_executed is not None
    
    @pytest.mark.asyncio
    async def test_base_tool_parameter_validation(self):
        """Test BaseTool parameter validation."""
        tool = MockTool()
        
        # Test missing required parameter
        with pytest.raises(ToolError):
            await tool.execute()
        
        # Test invalid parameter type
        with pytest.raises(ToolError):
            await tool.execute(test_param=123)
    
    @pytest.mark.asyncio
    async def test_base_tool_stats(self):
        """Test BaseTool statistics."""
        tool = MockTool()
        
        await tool.execute(test_param="test_value")
        stats = tool.get_stats()
        
        assert stats["name"] == "mock_tool"
        assert stats["execution_count"] == 1
        assert stats["error_count"] == 0
        assert stats["error_rate"] == 0.0
    
    @pytest.mark.asyncio
    async def test_base_tool_info(self):
        """Test BaseTool info."""
        tool = MockTool()
        
        info = tool.get_info()
        
        assert "metadata" in info
        assert "definition" in info
        assert "statistics" in info
        assert info["metadata"]["name"] == "mock_tool"


class TestToolRegistry:
    """Test suite for ToolRegistry."""
    
    def test_tool_registry_initialization(self):
        """Test ToolRegistry initialization."""
        registry = ToolRegistry()
        
        assert len(registry) == 0
        assert registry.get_all_tools() == []
    
    def test_tool_registration(self):
        """Test tool registration."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register_tool(tool)
        
        assert len(registry) == 1
        assert "mock_tool" in registry
        assert registry.get_tool("mock_tool") == tool
    
    def test_tool_unregistration(self):
        """Test tool unregistration."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register_tool(tool)
        registry.unregister_tool("mock_tool")
        
        assert len(registry) == 0
        assert "mock_tool" not in registry
    
    def test_tool_search(self):
        """Test tool search."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register_tool(tool)
        
        results = registry.search_tools("mock")
        assert len(results) == 1
        assert results[0] == tool
        
        results = registry.search_tools("nonexistent")
        assert len(results) == 0
    
    def test_tools_by_category(self):
        """Test getting tools by category."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register_tool(tool)
        
        utility_tools = registry.get_tools_by_category(ToolCategory.UTILITY)
        assert len(utility_tools) == 1
        assert utility_tools[0] == tool
        
        web_tools = registry.get_tools_by_category(ToolCategory.WEB)
        assert len(web_tools) == 0


class TestWebTools:
    """Test suite for WebTools."""
    
    @pytest.mark.asyncio
    async def test_playwright_browser_tool(self):
        """Test PlaywrightBrowserTool."""
        from src.tools.web_tools import PlaywrightBrowserTool
        
        tool = PlaywrightBrowserTool()
        
        result = await tool.execute(
            action="navigate",
            url="https://example.com"
        )
        
        assert result["action"] == "navigate"
        assert result["url"] == "https://example.com"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_web_scraping_tool(self):
        """Test WebScrapingTool."""
        from src.tools.web_tools import WebScrapingTool
        
        tool = WebScrapingTool()
        
        result = await tool.execute(
            url="https://example.com",
            selectors={"title": "h1", "content": "p"}
        )
        
        assert result["url"] == "https://example.com"
        assert "scraped_data" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_form_automation_tool(self):
        """Test FormAutomationTool."""
        from src.tools.web_tools import FormAutomationTool
        
        tool = FormAutomationTool()
        
        result = await tool.execute(
            form_data={"name": "John Doe", "email": "john@example.com"},
            submit=True
        )
        
        assert result["form_data"]["name"] == "John Doe"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_screenshot_capture_tool(self):
        """Test ScreenshotCaptureTool."""
        from src.tools.web_tools import ScreenshotCaptureTool
        
        tool = ScreenshotCaptureTool()
        
        result = await tool.execute(
            url="https://example.com",
            filename="test_screenshot.png"
        )
        
        assert result["url"] == "https://example.com"
        assert result["filename"] == "test_screenshot.png"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_element_interaction_tool(self):
        """Test ElementInteractionTool."""
        from src.tools.web_tools import ElementInteractionTool
        
        tool = ElementInteractionTool()
        
        result = await tool.execute(
            selector="button.submit",
            action="click"
        )
        
        assert result["selector"] == "button.submit"
        assert result["action"] == "click"
        assert result["success"] is True


class TestSearchTools:
    """Test suite for SearchTools."""
    
    @pytest.mark.asyncio
    async def test_web_search_tool(self):
        """Test WebSearchTool."""
        from src.tools.search_tools import WebSearchTool
        
        tool = WebSearchTool()
        
        result = await tool.execute(
            query="artificial intelligence",
            max_results=5
        )
        
        assert result["query"] == "artificial intelligence"
        assert result["max_results"] == 5
        assert len(result["results"]) <= 5
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_google_search_tool(self):
        """Test GoogleSearchTool."""
        from src.tools.search_tools import GoogleSearchTool
        
        tool = GoogleSearchTool()
        
        result = await tool.execute(
            query="machine learning",
            search_type="web"
        )
        
        assert result["query"] == "machine learning"
        assert result["search_type"] == "web"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_bing_search_tool(self):
        """Test BingSearchTool."""
        from src.tools.search_tools import BingSearchTool
        
        tool = BingSearchTool()
        
        result = await tool.execute(
            query="data science",
            market="en-US"
        )
        
        assert result["query"] == "data science"
        assert result["market"] == "en-US"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_tool(self):
        """Test DuckDuckGoSearchTool."""
        from src.tools.search_tools import DuckDuckGoSearchTool
        
        tool = DuckDuckGoSearchTool()
        
        result = await tool.execute(
            query="privacy search",
            region="us-en"
        )
        
        assert result["query"] == "privacy search"
        assert result["region"] == "us-en"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_academic_search_tool(self):
        """Test AcademicSearchTool."""
        from src.tools.search_tools import AcademicSearchTool
        
        tool = AcademicSearchTool()
        
        result = await tool.execute(
            query="deep learning",
            database="arxiv"
        )
        
        assert result["query"] == "deep learning"
        assert result["database"] == "arxiv"
        assert result["success"] is True


class TestAnalysisTools:
    """Test suite for AnalysisTools."""
    
    @pytest.mark.asyncio
    async def test_data_analysis_tool(self):
        """Test DataAnalysisTool."""
        from src.tools.analysis_tools import DataAnalysisTool
        
        tool = DataAnalysisTool()
        
        result = await tool.execute(
            data='{"values": [1, 2, 3, 4, 5]}',
            analysis_type="descriptive"
        )
        
        assert result["analysis_type"] == "descriptive"
        assert "analysis_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_csv_analysis_tool(self):
        """Test CSVAnalysisTool."""
        from src.tools.analysis_tools import CSVAnalysisTool
        
        tool = CSVAnalysisTool()
        
        result = await tool.execute(
            file_path="data/sample.csv",
            analysis_types=["summary", "missing"]
        )
        
        assert result["file_path"] == "data/sample.csv"
        assert "summary" in result["analysis_results"]
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_chart_generation_tool(self):
        """Test ChartGenerationTool."""
        from src.tools.analysis_tools import ChartGenerationTool
        
        tool = ChartGenerationTool()
        
        result = await tool.execute(
            data={"x": [1, 2, 3], "y": [2, 4, 6]},
            chart_type="line",
            title="Sample Chart"
        )
        
        assert result["chart_type"] == "line"
        assert result["title"] == "Sample Chart"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_statistical_analysis_tool(self):
        """Test StatisticalAnalysisTool."""
        from src.tools.analysis_tools import StatisticalAnalysisTool
        
        tool = StatisticalAnalysisTool()
        
        result = await tool.execute(
            data=[1, 2, 3, 4, 5],
            test_type="t_test"
        )
        
        assert result["test_type"] == "t_test"
        assert "statistical_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_report_generation_tool(self):
        """Test ReportGenerationTool."""
        from src.tools.analysis_tools import ReportGenerationTool
        
        tool = ReportGenerationTool()
        
        result = await tool.execute(
            analysis_results={"summary": "Analysis completed"},
            report_type="summary"
        )
        
        assert result["report_type"] == "summary"
        assert "report_metadata" in result
        assert result["success"] is True


class TestDataTools:
    """Test suite for DataTools."""
    
    @pytest.mark.asyncio
    async def test_data_cleaning_tool(self):
        """Test DataCleaningTool."""
        from src.tools.data_tools import DataCleaningTool
        
        tool = DataCleaningTool()
        
        result = await tool.execute(
            data='{"values": [1, 2, null, 4, 5]}',
            cleaning_options=["handle_missing", "remove_outliers"]
        )
        
        assert "handle_missing" in result["cleaning_options"]
        assert "cleaning_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_data_transformation_tool(self):
        """Test DataTransformationTool."""
        from src.tools.data_tools import DataTransformationTool
        
        tool = DataTransformationTool()
        
        result = await tool.execute(
            data='{"values": [1, 2, 3, 4, 5]}',
            transformations=["log_transform", "scaling"]
        )
        
        assert "log_transform" in result["transformations"]
        assert "transformation_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_data_validation_tool(self):
        """Test DataValidationTool."""
        from src.tools.data_tools import DataValidationTool
        
        tool = DataValidationTool()
        
        result = await tool.execute(
            data='{"values": [1, 2, 3, 4, 5]}',
            validation_rules={"min_value": 0, "max_value": 10}
        )
        
        assert "validation_results" in result
        assert "validation_report" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_data_merge_tool(self):
        """Test DataMergeTool."""
        from src.tools.data_tools import DataMergeTool
        
        tool = DataMergeTool()
        
        result = await tool.execute(
            datasets=["dataset1.csv", "dataset2.csv"],
            merge_type="inner",
            join_keys=["id"]
        )
        
        assert result["merge_type"] == "inner"
        assert result["join_keys"] == ["id"]
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_data_aggregation_tool(self):
        """Test DataAggregationTool."""
        from src.tools.data_tools import DataAggregationTool
        
        tool = DataAggregationTool()
        
        result = await tool.execute(
            data="sales_data.csv",
            group_columns=["region", "product"],
            agg_functions={"sales": "sum", "quantity": "mean"}
        )
        
        assert result["group_columns"] == ["region", "product"]
        assert result["agg_functions"]["sales"] == "sum"
        assert result["success"] is True


class TestFileTools:
    """Test suite for FileTools."""
    
    @pytest.mark.asyncio
    async def test_file_reader_tool(self):
        """Test FileReaderTool."""
        from src.tools.file_tools import FileReaderTool
        
        tool = FileReaderTool()
        
        result = await tool.execute(
            file_path="data/sample.csv",
            file_format="csv"
        )
        
        assert result["file_path"] == "data/sample.csv"
        assert result["file_format"] == "csv"
        assert "content" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_file_writer_tool(self):
        """Test FileWriterTool."""
        from src.tools.file_tools import FileWriterTool
        
        tool = FileWriterTool()
        
        result = await tool.execute(
            data={"users": [{"id": 1, "name": "John"}]},
            file_path="output/users.json",
            file_format="json"
        )
        
        assert result["file_path"] == "output/users.json"
        assert result["file_format"] == "json"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_pdf_processor_tool(self):
        """Test PDFProcessorTool."""
        from src.tools.file_tools import PDFProcessorTool
        
        tool = PDFProcessorTool()
        
        result = await tool.execute(
            file_path="document.pdf",
            operation="extract_text"
        )
        
        assert result["file_path"] == "document.pdf"
        assert result["operation"] == "extract_text"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_excel_processor_tool(self):
        """Test ExcelProcessorTool."""
        from src.tools.file_tools import ExcelProcessorTool
        
        tool = ExcelProcessorTool()
        
        result = await tool.execute(
            file_path="data.xlsx",
            operation="read",
            sheet_name="Sheet1"
        )
        
        assert result["file_path"] == "data.xlsx"
        assert result["operation"] == "read"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_image_processor_tool(self):
        """Test ImageProcessorTool."""
        from src.tools.file_tools import ImageProcessorTool
        
        tool = ImageProcessorTool()
        
        result = await tool.execute(
            file_path="image.jpg",
            operation="resize",
            width=800,
            height=600
        )
        
        assert result["file_path"] == "image.jpg"
        assert result["operation"] == "resize"
        assert result["width"] == 800
        assert result["success"] is True


class TestAutomationTools:
    """Test suite for AutomationTools."""
    
    @pytest.mark.asyncio
    async def test_workflow_automation_tool(self):
        """Test WorkflowAutomationTool."""
        from src.tools.automation_tools import WorkflowAutomationTool
        
        tool = WorkflowAutomationTool()
        
        result = await tool.execute(
            workflow_definition={
                "steps": [
                    {"id": "step1", "action": "data_extraction"},
                    {"id": "step2", "action": "data_processing", "depends_on": ["step1"]}
                ]
            },
            execution_mode="sequential"
        )
        
        assert result["execution_mode"] == "sequential"
        assert "execution_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_task_scheduler_tool(self):
        """Test TaskSchedulerTool."""
        from src.tools.automation_tools import TaskSchedulerTool
        
        tool = TaskSchedulerTool()
        
        result = await tool.execute(
            task_definition={
                "action": "data_backup",
                "parameters": {"source": "/data", "destination": "/backup"}
            },
            schedule="0 2 * * *"
        )
        
        assert result["schedule"] == "0 2 * * *"
        assert "scheduling_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_process_automation_tool(self):
        """Test ProcessAutomationTool."""
        from src.tools.automation_tools import ProcessAutomationTool
        
        tool = ProcessAutomationTool()
        
        result = await tool.execute(
            process_definition={
                "command": "python",
                "args": ["script.py", "--input", "data.csv"],
                "working_directory": "/app"
            },
            execution_environment="local"
        )
        
        assert result["execution_environment"] == "local"
        assert "execution_results" in result
        assert result["success"] is True


class TestCommunicationTools:
    """Test suite for CommunicationTools."""
    
    @pytest.mark.asyncio
    async def test_email_tool(self):
        """Test EmailTool."""
        from src.tools.communication_tools import EmailTool
        
        tool = EmailTool()
        
        result = await tool.execute(
            to=["user@example.com"],
            subject="Test Email",
            body="This is a test email message."
        )
        
        assert result["to"] == ["user@example.com"]
        assert result["subject"] == "Test Email"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_slack_tool(self):
        """Test SlackTool."""
        from src.tools.communication_tools import SlackTool
        
        tool = SlackTool()
        
        result = await tool.execute(
            channel="#general",
            message="Hello from the bot!"
        )
        
        assert result["channel"] == "#general"
        assert result["message"] == "Hello from the bot!"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_discord_tool(self):
        """Test DiscordTool."""
        from src.tools.communication_tools import DiscordTool
        
        tool = DiscordTool()
        
        result = await tool.execute(
            channel_id="123456789012345678",
            message="Hello from Discord bot!"
        )
        
        assert result["channel_id"] == "123456789012345678"
        assert result["message"] == "Hello from Discord bot!"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_webhook_tool(self):
        """Test WebhookTool."""
        from src.tools.communication_tools import WebhookTool
        
        tool = WebhookTool()
        
        result = await tool.execute(
            url="https://hooks.slack.com/services/...",
            method="POST",
            data={"text": "Hello from webhook!"}
        )
        
        assert result["url"] == "https://hooks.slack.com/services/..."
        assert result["method"] == "POST"
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_notification_tool(self):
        """Test NotificationTool."""
        from src.tools.communication_tools import NotificationTool
        
        tool = NotificationTool()
        
        result = await tool.execute(
            message="System maintenance scheduled",
            notification_type="info",
            recipients=["admin@example.com"],
            channels=["email", "slack"]
        )
        
        assert result["message"] == "System maintenance scheduled"
        assert result["notification_type"] == "info"
        assert result["success"] is True


class TestSystemTools:
    """Test suite for SystemTools."""
    
    @pytest.mark.asyncio
    async def test_system_monitor_tool(self):
        """Test SystemMonitorTool."""
        from src.tools.system_tools import SystemMonitorTool
        
        tool = SystemMonitorTool()
        
        result = await tool.execute(
            monitoring_type="cpu",
            interval=5,
            duration=30
        )
        
        assert result["monitoring_type"] == "cpu"
        assert result["interval"] == 5
        assert "monitoring_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_resource_manager_tool(self):
        """Test ResourceManagerTool."""
        from src.tools.system_tools import ResourceManagerTool
        
        tool = ResourceManagerTool()
        
        result = await tool.execute(
            resource_type="memory",
            action="cleanup"
        )
        
        assert result["resource_type"] == "memory"
        assert result["action"] == "cleanup"
        assert "management_results" in result
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_process_manager_tool(self):
        """Test ProcessManagerTool."""
        from src.tools.system_tools import ProcessManagerTool
        
        tool = ProcessManagerTool()
        
        result = await tool.execute(
            action="list",
            process_name="python"
        )
        
        assert result["action"] == "list"
        assert result["process_name"] == "python"
        assert "process_results" in result
        assert result["success"] is True


class TestToolCollections:
    """Test suite for tool collections."""
    
    def test_web_tools_collection(self):
        """Test WebTools collection."""
        tools = WebTools.get_all_tools()
        assert len(tools) == 5
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "playwright_browser", "web_scraping", "form_automation",
            "screenshot_capture", "element_interaction"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_search_tools_collection(self):
        """Test SearchTools collection."""
        tools = SearchTools.get_all_tools()
        assert len(tools) == 5
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "web_search", "google_search", "bing_search",
            "duckduckgo_search", "academic_search"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_analysis_tools_collection(self):
        """Test AnalysisTools collection."""
        tools = AnalysisTools.get_all_tools()
        assert len(tools) == 5
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "data_analysis", "csv_analysis", "chart_generation",
            "statistical_analysis", "report_generation"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_data_tools_collection(self):
        """Test DataTools collection."""
        tools = DataTools.get_all_tools()
        assert len(tools) == 5
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "data_cleaning", "data_transformation", "data_validation",
            "data_merge", "data_aggregation"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_file_tools_collection(self):
        """Test FileTools collection."""
        tools = FileTools.get_all_tools()
        assert len(tools) == 5
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "file_reader", "file_writer", "pdf_processor",
            "excel_processor", "image_processor"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_automation_tools_collection(self):
        """Test AutomationTools collection."""
        tools = AutomationTools.get_all_tools()
        assert len(tools) == 3
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "workflow_automation", "task_scheduler", "process_automation"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_communication_tools_collection(self):
        """Test CommunicationTools collection."""
        tools = CommunicationTools.get_all_tools()
        assert len(tools) == 5
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "email", "slack", "discord", "webhook", "notification"
        ]
        assert all(name in tool_names for name in expected_names)
    
    def test_system_tools_collection(self):
        """Test SystemTools collection."""
        tools = SystemTools.get_all_tools()
        assert len(tools) == 3
        
        tool_names = [tool._get_metadata().name for tool in tools]
        expected_names = [
            "system_monitor", "resource_manager", "process_manager"
        ]
        assert all(name in tool_names for name in expected_names)


if __name__ == "__main__":
    pytest.main([__file__])