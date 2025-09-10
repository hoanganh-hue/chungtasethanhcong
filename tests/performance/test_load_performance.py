"""
Load Performance Tests for OpenManus-Youtu Integrated Framework
Comprehensive load testing and performance benchmarking
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from httpx import AsyncClient
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

from src.api.server import create_app


class TestLoadPerformance:
    """Test load performance and scalability."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app(debug=True)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_concurrent_agent_creation(self, client):
        """Test concurrent agent creation performance."""
        num_agents = 50
        start_time = time.time()
        
        # Create agents concurrently
        tasks = []
        for i in range(num_agents):
            task = client.post("/api/v1/agents/create", json={
                "agent_type": "simple",
                "name": f"load_test_agent_{i}"
            })
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all agents created successfully
        successful_creations = sum(1 for r in responses if r.status_code == 200 and r.json()["success"])
        assert successful_creations == num_agents
        
        # Performance metrics
        total_time = end_time - start_time
        agents_per_second = num_agents / total_time
        
        print(f"Created {num_agents} agents in {total_time:.2f}s ({agents_per_second:.2f} agents/s)")
        assert agents_per_second > 10  # Should create at least 10 agents per second
        
        # Clean up agents
        agent_ids = [r.json()["agent_id"] for r in responses if r.status_code == 200]
        cleanup_tasks = [client.delete(f"/api/v1/agents/{agent_id}") for agent_id in agent_ids]
        await asyncio.gather(*cleanup_tasks)

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self, client):
        """Test concurrent tool execution performance."""
        num_executions = 100
        start_time = time.time()
        
        # Execute tools concurrently
        tasks = []
        for i in range(num_executions):
            task = client.post("/api/v1/tools/execute", json={
                "tool_name": "data_analysis_tool",
                "parameters": {
                    "data": list(range(1, i + 6)),
                    "analysis_type": "descriptive"
                }
            })
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all executions successful
        successful_executions = sum(1 for r in responses if r.status_code == 200 and r.json()["success"])
        assert successful_executions == num_executions
        
        # Performance metrics
        total_time = end_time - start_time
        executions_per_second = num_executions / total_time
        
        print(f"Executed {num_executions} tools in {total_time:.2f}s ({executions_per_second:.2f} executions/s)")
        assert executions_per_second > 20  # Should execute at least 20 tools per second

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, client):
        """Test memory usage under load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and execute many agents
        num_agents = 100
        agent_ids = []
        
        for i in range(num_agents):
            response = await client.post("/api/v1/agents/create", json={
                "agent_type": "simple",
                "name": f"memory_test_agent_{i}"
            })
            if response.status_code == 200:
                agent_ids.append(response.json()["agent_id"])
        
        # Execute tasks on all agents
        execution_tasks = []
        for agent_id in agent_ids:
            task = client.post(f"/api/v1/agents/{agent_id}/execute", json={
                "agent_type": "simple",
                "task": f"Calculate {len(agent_ids)} * 2",
                "parameters": {"number": len(agent_ids), "multiplier": 2}
            })
            execution_tasks.append(task)
        
        await asyncio.gather(*execution_tasks)
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (+{memory_increase:.2f}MB)")
        assert memory_increase < 500  # Should not increase by more than 500MB
        
        # Clean up
        cleanup_tasks = [client.delete(f"/api/v1/agents/{agent_id}") for agent_id in agent_ids]
        await asyncio.gather(*cleanup_tasks)

    @pytest.mark.asyncio
    async def test_response_time_consistency(self, client):
        """Test response time consistency under load."""
        num_requests = 50
        response_times = []
        
        for i in range(num_requests):
            start_time = time.time()
            response = await client.get("/api/v1/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        mean_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        std_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
        p95_time = sorted(response_times)[int(0.95 * len(response_times))]
        
        print(f"Response time stats: mean={mean_time:.3f}s, median={median_time:.3f}s, std={std_time:.3f}s, p95={p95_time:.3f}s")
        
        # Performance assertions
        assert mean_time < 0.1  # Mean response time should be under 100ms
        assert p95_time < 0.2   # 95th percentile should be under 200ms
        assert std_time < 0.05  # Standard deviation should be low for consistency

    @pytest.mark.asyncio
    async def test_workflow_execution_performance(self, client):
        """Test workflow execution performance."""
        num_workflows = 20
        start_time = time.time()
        
        # Create and execute workflows
        workflow_tasks = []
        for i in range(num_workflows):
            workflow_request = {
                "name": f"Performance Workflow {i}",
                "description": "Performance test workflow",
                "steps": [
                    {
                        "step_id": "step1",
                        "tool_name": "data_analysis_tool",
                        "parameters": {
                            "data": list(range(1, i + 6)),
                            "analysis_type": "descriptive"
                        }
                    }
                ],
                "parallel": False
            }
            task = client.post("/api/v1/workflows/execute", json=workflow_request)
            workflow_tasks.append(task)
        
        responses = await asyncio.gather(*workflow_tasks)
        end_time = time.time()
        
        # Verify workflows started successfully
        successful_workflows = sum(1 for r in responses if r.status_code == 200 and r.json()["success"])
        assert successful_workflows == num_workflows
        
        # Performance metrics
        total_time = end_time - start_time
        workflows_per_second = num_workflows / total_time
        
        print(f"Started {num_workflows} workflows in {total_time:.2f}s ({workflows_per_second:.2f} workflows/s)")
        assert workflows_per_second > 5  # Should start at least 5 workflows per second

    @pytest.mark.asyncio
    async def test_database_connection_pool_performance(self, client):
        """Test database connection pool performance."""
        num_concurrent_requests = 100
        start_time = time.time()
        
        # Make concurrent requests that use database
        tasks = []
        for i in range(num_concurrent_requests):
            task = client.get("/api/v1/agents")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all requests successful
        successful_requests = sum(1 for r in responses if r.status_code == 200)
        assert successful_requests == num_concurrent_requests
        
        # Performance metrics
        total_time = end_time - start_time
        requests_per_second = num_concurrent_requests / total_time
        
        print(f"Handled {num_concurrent_requests} concurrent DB requests in {total_time:.2f}s ({requests_per_second:.2f} requests/s)")
        assert requests_per_second > 50  # Should handle at least 50 requests per second

    @pytest.mark.asyncio
    async def test_error_handling_under_load(self, client):
        """Test error handling performance under load."""
        num_requests = 50
        start_time = time.time()
        
        # Make requests that will fail
        tasks = []
        for i in range(num_requests):
            task = client.post("/api/v1/tools/execute", json={
                "tool_name": "invalid_tool",
                "parameters": {}
            })
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all requests handled (even if they failed)
        handled_requests = sum(1 for r in responses if r.status_code == 200)
        assert handled_requests == num_requests
        
        # Verify all returned error responses
        error_responses = sum(1 for r in responses if r.json()["success"] is False)
        assert error_responses == num_requests
        
        # Performance metrics
        total_time = end_time - start_time
        requests_per_second = num_requests / total_time
        
        print(f"Handled {num_requests} error requests in {total_time:.2f}s ({requests_per_second:.2f} requests/s)")
        assert requests_per_second > 20  # Should handle errors efficiently

    @pytest.mark.asyncio
    async def test_sustained_load_performance(self, client):
        """Test sustained load performance over time."""
        duration_seconds = 30
        requests_per_second = 10
        total_requests = duration_seconds * requests_per_second
        
        start_time = time.time()
        request_count = 0
        response_times = []
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Make a batch of requests
            tasks = []
            for _ in range(requests_per_second):
                task = client.get("/api/v1/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            batch_end = time.time()
            
            # Record metrics
            request_count += len(responses)
            response_times.extend([batch_end - batch_start] * len(responses))
            
            # Wait for next second
            elapsed = batch_end - batch_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
        
        total_time = time.time() - start_time
        actual_rps = request_count / total_time
        
        print(f"Sustained load: {request_count} requests in {total_time:.2f}s ({actual_rps:.2f} RPS)")
        assert actual_rps >= requests_per_second * 0.8  # Should maintain at least 80% of target RPS