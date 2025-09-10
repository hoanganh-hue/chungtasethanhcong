"""
End-to-End Tests for Tool Workflows
Complete workflow testing for all tool categories
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from httpx import AsyncClient

from src.api.server import create_app
from src.tools.web_tools import WebScrapingTool, PlaywrightBrowserTool
from src.tools.search_tools import WebSearchTool, GoogleSearchTool
from src.tools.analysis_tools import DataAnalysisTool, ChartGenerationTool
from src.tools.data_tools import DataCleaningTool, DataTransformationTool
from src.tools.file_tools import FileReaderTool, FileWriterTool


class TestToolWorkflows:
    """Test complete tool workflows end-to-end."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app(debug=True)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_web_tools_complete_workflow(self, client):
        """Test complete web tools workflow."""
        # Test web scraping
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "web_scraping_tool",
            "parameters": {
                "url": "https://httpbin.org/html",
                "selectors": {"title": "h1", "content": "p"}
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "title" in result["result"]

        # Test browser automation
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "playwright_browser_tool",
            "parameters": {
                "url": "https://httpbin.org/html",
                "action": "get_title"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "title" in result["result"]

    @pytest.mark.asyncio
    async def test_search_tools_complete_workflow(self, client):
        """Test complete search tools workflow."""
        # Test web search
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "web_search_tool",
            "parameters": {
                "query": "OpenManus AI framework",
                "max_results": 5
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["result"]["results"]) <= 5

        # Test Google search
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "google_search_tool",
            "parameters": {
                "query": "Python FastAPI",
                "max_results": 3
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["result"]["results"]) <= 3

    @pytest.mark.asyncio
    async def test_analysis_tools_complete_workflow(self, client):
        """Test complete analysis tools workflow."""
        # Test data analysis
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "data_analysis_tool",
            "parameters": {
                "data": test_data,
                "analysis_type": "descriptive"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "mean" in result["result"]
        assert "std" in result["result"]

        # Test chart generation
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "chart_generation_tool",
            "parameters": {
                "data": test_data,
                "chart_type": "line",
                "title": "Test Chart"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "chart_path" in result["result"]

    @pytest.mark.asyncio
    async def test_data_tools_complete_workflow(self, client):
        """Test complete data tools workflow."""
        # Test data cleaning
        dirty_data = [1, 2, None, 4, 5, "", 7, 8, 9, 10]
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "data_cleaning_tool",
            "parameters": {
                "data": dirty_data,
                "remove_nulls": True,
                "remove_empty": True
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert None not in result["result"]
        assert "" not in result["result"]

        # Test data transformation
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "data_transformation_tool",
            "parameters": {
                "data": [1, 2, 3, 4, 5],
                "transformation": "normalize"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["result"]) == 5

    @pytest.mark.asyncio
    async def test_file_tools_complete_workflow(self, client):
        """Test complete file tools workflow."""
        # Test file writing
        test_content = "Hello, World!\nThis is a test file."
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "file_writer_tool",
            "parameters": {
                "file_path": "/tmp/test_file.txt",
                "content": test_content,
                "file_type": "text"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

        # Test file reading
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "file_reader_tool",
            "parameters": {
                "file_path": "/tmp/test_file.txt",
                "file_type": "text"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["result"] == test_content

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, client):
        """Test tool error handling."""
        # Test invalid tool
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "invalid_tool",
            "parameters": {}
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "error" in result

        # Test invalid parameters
        response = await client.post("/api/v1/tools/execute", json={
            "tool_name": "web_search_tool",
            "parameters": {
                "invalid_param": "invalid_value"
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_tool_concurrent_execution(self, client):
        """Test concurrent tool execution."""
        # Execute multiple tools concurrently
        tasks = []
        for i in range(3):
            task = client.post("/api/v1/tools/execute", json={
                "tool_name": "data_analysis_tool",
                "parameters": {
                    "data": list(range(1, i + 6)),
                    "analysis_type": "descriptive"
                }
            })
            tasks.append(task)

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert "mean" in result["result"]

    @pytest.mark.asyncio
    async def test_tool_listing_and_discovery(self, client):
        """Test tool listing and discovery."""
        # List all tools
        response = await client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        assert "items" in tools
        assert len(tools["items"]) > 0

        # Get specific tool
        tool_name = tools["items"][0]["name"]
        response = await client.get(f"/api/v1/tools/{tool_name}")
        assert response.status_code == 200
        tool_info = response.json()
        assert tool_info["name"] == tool_name

        # Test pagination
        response = await client.get("/api/v1/tools?page=1&page_size=5")
        assert response.status_code == 200
        tools_page = response.json()
        assert len(tools_page["items"]) <= 5