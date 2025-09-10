"""
End-to-End Tests for Workflow Orchestration
Complete workflow testing for complex multi-step processes
"""

import pytest
import asyncio
import json
from typing import Dict, Any, List
from httpx import AsyncClient

from src.api.server import create_app


class TestWorkflowOrchestration:
    """Test complete workflow orchestration end-to-end."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app(debug=True)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self, client):
        """Test simple workflow execution."""
        workflow_request = {
            "name": "Simple Data Processing Workflow",
            "description": "Process data through multiple steps",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "data_cleaning_tool",
                    "parameters": {
                        "data": [1, 2, None, 4, 5],
                        "remove_nulls": True
                    }
                },
                {
                    "step_id": "step2",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [1, 2, 4, 5],  # Result from step1
                        "analysis_type": "descriptive"
                    },
                    "depends_on": ["step1"]
                }
            ],
            "parallel": False
        }

        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        workflow_id = result["workflow_id"]

        # Wait for workflow completion
        await asyncio.sleep(2)

        # Check workflow status
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] in ["completed", "running"]

    @pytest.mark.asyncio
    async def test_parallel_workflow_execution(self, client):
        """Test parallel workflow execution."""
        workflow_request = {
            "name": "Parallel Data Processing Workflow",
            "description": "Process multiple data sets in parallel",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [1, 2, 3, 4, 5],
                        "analysis_type": "descriptive"
                    }
                },
                {
                    "step_id": "step2",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [6, 7, 8, 9, 10],
                        "analysis_type": "descriptive"
                    }
                },
                {
                    "step_id": "step3",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [11, 12, 13, 14, 15],
                        "analysis_type": "descriptive"
                    }
                }
            ],
            "parallel": True
        }

        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        workflow_id = result["workflow_id"]

        # Wait for workflow completion
        await asyncio.sleep(3)

        # Check workflow status
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] in ["completed", "running"]

    @pytest.mark.asyncio
    async def test_agent_workflow_execution(self, client):
        """Test workflow with agent execution."""
        workflow_request = {
            "name": "Agent-Based Workflow",
            "description": "Use agents in workflow steps",
            "steps": [
                {
                    "step_id": "step1",
                    "agent_type": "simple",
                    "parameters": {
                        "task": "Calculate sum of 1 to 5",
                        "numbers": [1, 2, 3, 4, 5]
                    }
                },
                {
                    "step_id": "step2",
                    "agent_type": "simple",
                    "parameters": {
                        "task": "Calculate sum of 6 to 10",
                        "numbers": [6, 7, 8, 9, 10]
                    }
                },
                {
                    "step_id": "step3",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [15, 40],  # Results from step1 and step2
                        "analysis_type": "descriptive"
                    },
                    "depends_on": ["step1", "step2"]
                }
            ],
            "parallel": False
        }

        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        workflow_id = result["workflow_id"]

        # Wait for workflow completion
        await asyncio.sleep(5)

        # Check workflow status
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] in ["completed", "running"]

    @pytest.mark.asyncio
    async def test_complex_workflow_with_dependencies(self, client):
        """Test complex workflow with multiple dependencies."""
        workflow_request = {
            "name": "Complex Dependency Workflow",
            "description": "Workflow with complex step dependencies",
            "steps": [
                {
                    "step_id": "data_collection",
                    "tool_name": "data_cleaning_tool",
                    "parameters": {
                        "data": [1, 2, None, 4, 5, 6, 7, 8, 9, 10],
                        "remove_nulls": True
                    }
                },
                {
                    "step_id": "data_analysis",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [1, 2, 4, 5, 6, 7, 8, 9, 10],
                        "analysis_type": "descriptive"
                    },
                    "depends_on": ["data_collection"]
                },
                {
                    "step_id": "chart_generation",
                    "tool_name": "chart_generation_tool",
                    "parameters": {
                        "data": [1, 2, 4, 5, 6, 7, 8, 9, 10],
                        "chart_type": "line",
                        "title": "Processed Data Chart"
                    },
                    "depends_on": ["data_collection"]
                },
                {
                    "step_id": "report_generation",
                    "tool_name": "report_generation_tool",
                    "parameters": {
                        "data": {
                            "analysis": "placeholder",  # Will be replaced with step2 result
                            "chart": "placeholder"      # Will be replaced with step3 result
                        },
                        "format": "html"
                    },
                    "depends_on": ["data_analysis", "chart_generation"]
                }
            ],
            "parallel": False
        }

        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        workflow_id = result["workflow_id"]

        # Wait for workflow completion
        await asyncio.sleep(8)

        # Check workflow status
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] in ["completed", "running"]

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, client):
        """Test workflow error handling."""
        workflow_request = {
            "name": "Error Handling Workflow",
            "description": "Workflow that should fail",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "invalid_tool",
                    "parameters": {}
                },
                {
                    "step_id": "step2",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [1, 2, 3],
                        "analysis_type": "descriptive"
                    },
                    "depends_on": ["step1"]
                }
            ],
            "parallel": False
        }

        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        workflow_id = result["workflow_id"]

        # Wait for workflow completion
        await asyncio.sleep(3)

        # Check workflow status
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] in ["failed", "running"]

    @pytest.mark.asyncio
    async def test_workflow_listing_and_management(self, client):
        """Test workflow listing and management."""
        # List workflows
        response = await client.get("/api/v1/workflows")
        assert response.status_code == 200
        workflows = response.json()
        assert "items" in workflows

        # Create a simple workflow
        workflow_request = {
            "name": "Test Management Workflow",
            "description": "Workflow for testing management",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": [1, 2, 3],
                        "analysis_type": "descriptive"
                    }
                }
            ],
            "parallel": False
        }

        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        workflow_id = response.json()["workflow_id"]

        # List workflows again
        response = await client.get("/api/v1/workflows")
        assert response.status_code == 200
        workflows = response.json()
        assert len(workflows["items"]) >= 1

        # Get specific workflow
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        workflow = response.json()
        assert workflow["name"] == "Test Management Workflow"

    @pytest.mark.asyncio
    async def test_workflow_timeout_handling(self, client):
        """Test workflow timeout handling."""
        workflow_request = {
            "name": "Timeout Test Workflow",
            "description": "Workflow that should timeout",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": list(range(1000)),
                        "analysis_type": "descriptive"
                    }
                }
            ],
            "parallel": False,
            "timeout": 1  # 1 second timeout
        }

        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        workflow_id = result["workflow_id"]

        # Wait for timeout
        await asyncio.sleep(3)

        # Check workflow status
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] in ["failed", "timeout", "running"]