"""
End-to-End Tests for Agent Workflows
Complete workflow testing for all agent types
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.api.server import create_app
from src.agents.simple_agent import SimpleAgent
from src.agents.browser_agent import BrowserAgent
from src.agents.orchestra_agent import OrchestraAgent
from src.agents.meta_agent import MetaAgent


class TestAgentWorkflows:
    """Test complete agent workflows end-to-end."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app(debug=True)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_simple_agent_complete_workflow(self, client):
        """Test complete SimpleAgent workflow."""
        # Create agent
        response = await client.post("/api/v1/agents/create", json={
            "agent_type": "simple",
            "name": "test_simple_agent",
            "config": {"max_iterations": 5}
        })
        assert response.status_code == 200
        agent_data = response.json()
        agent_id = agent_data["agent_id"]
        assert agent_data["success"] is True

        # Execute task
        response = await client.post(f"/api/v1/agents/{agent_id}/execute", json={
            "agent_type": "simple",
            "task": "Calculate the sum of numbers 1 to 10",
            "parameters": {"numbers": list(range(1, 11))}
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["result"] == 55

        # List agents
        response = await client.get("/api/v1/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents["items"]) >= 1

        # Delete agent
        response = await client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_browser_agent_complete_workflow(self, client):
        """Test complete BrowserAgent workflow."""
        # Create agent
        response = await client.post("/api/v1/agents/create", json={
            "agent_type": "browser",
            "name": "test_browser_agent",
            "config": {"headless": True, "timeout": 30}
        })
        assert response.status_code == 200
        agent_data = response.json()
        agent_id = agent_data["agent_id"]
        assert agent_data["success"] is True

        # Execute browser task
        response = await client.post(f"/api/v1/agents/{agent_id}/execute", json={
            "agent_type": "browser",
            "task": "Navigate to Google and get page title",
            "parameters": {"url": "https://www.google.com"}
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "Google" in result["result"]

        # Delete agent
        response = await client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_orchestra_agent_complete_workflow(self, client):
        """Test complete OrchestraAgent workflow."""
        # Create agent
        response = await client.post("/api/v1/agents/create", json={
            "agent_type": "orchestra",
            "name": "test_orchestra_agent",
            "config": {"max_agents": 3}
        })
        assert response.status_code == 200
        agent_data = response.json()
        agent_id = agent_data["agent_id"]
        assert agent_data["success"] is True

        # Execute orchestration task
        response = await client.post(f"/api/v1/agents/{agent_id}/execute", json={
            "agent_type": "orchestra",
            "task": "Coordinate multiple simple agents to calculate different sums",
            "parameters": {
                "tasks": [
                    {"task": "Calculate sum of 1 to 5", "numbers": list(range(1, 6))},
                    {"task": "Calculate sum of 6 to 10", "numbers": list(range(6, 11))},
                    {"task": "Calculate sum of 11 to 15", "numbers": list(range(11, 16))}
                ]
            }
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["result"]) == 3

        # Delete agent
        response = await client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_meta_agent_complete_workflow(self, client):
        """Test complete MetaAgent workflow."""
        # Create agent
        response = await client.post("/api/v1/agents/create", json={
            "agent_type": "meta",
            "name": "test_meta_agent",
            "config": {"auto_generate": True}
        })
        assert response.status_code == 200
        agent_data = response.json()
        agent_id = agent_data["agent_id"]
        assert agent_data["success"] is True

        # Execute meta task
        response = await client.post(f"/api/v1/agents/{agent_id}/execute", json={
            "agent_type": "meta",
            "task": "Generate a simple calculator agent configuration",
            "parameters": {"agent_type": "simple", "capabilities": ["arithmetic"]}
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "config" in result["result"]

        # Delete agent
        response = await client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_error_handling(self, client):
        """Test agent error handling."""
        # Create agent
        response = await client.post("/api/v1/agents/create", json={
            "agent_type": "simple",
            "name": "test_error_agent"
        })
        assert response.status_code == 200
        agent_id = response.json()["agent_id"]

        # Execute invalid task
        response = await client.post(f"/api/v1/agents/{agent_id}/execute", json={
            "agent_type": "simple",
            "task": "Invalid task that should fail",
            "parameters": {"invalid": "data"}
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "error" in result

        # Delete agent
        response = await client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_concurrent_execution(self, client):
        """Test concurrent agent execution."""
        # Create multiple agents
        agent_ids = []
        for i in range(3):
            response = await client.post("/api/v1/agents/create", json={
                "agent_type": "simple",
                "name": f"concurrent_agent_{i}"
            })
            assert response.status_code == 200
            agent_ids.append(response.json()["agent_id"])

        # Execute tasks concurrently
        tasks = []
        for i, agent_id in enumerate(agent_ids):
            task = client.post(f"/api/v1/agents/{agent_id}/execute", json={
                "agent_type": "simple",
                "task": f"Calculate {i + 1} * 10",
                "parameters": {"number": i + 1, "multiplier": 10}
            })
            tasks.append(task)

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True

        # Clean up agents
        for agent_id in agent_ids:
            response = await client.delete(f"/api/v1/agents/{agent_id}")
            assert response.status_code == 200