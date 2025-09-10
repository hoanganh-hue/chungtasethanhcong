# 📖 OpenManus-Youtu Framework - Tutorials

## 🎯 **Tutorial Collection**

This document provides step-by-step tutorials for common use cases with the OpenManus-Youtu Integrated Framework.

---

## 📋 **Tutorial List**

1. [Building Your First Agent](#building-your-first-agent)
2. [Creating Custom Tools](#creating-custom-tools)
3. [Web Scraping with BrowserAgent](#web-scraping-with-browseragent)
4. [Data Analysis Pipeline](#data-analysis-pipeline)
5. [Workflow Orchestration](#workflow-orchestration)
6. [API Integration](#api-integration)
7. [Performance Optimization](#performance-optimization)

---

## 🤖 **Building Your First Agent**

### **Tutorial: Simple Calculator Agent**

```python
import asyncio
from src.agents.simple_agent import SimpleAgent

async def main():
    # Create a calculator agent
    calculator = SimpleAgent(
        name="calculator_agent",
        config={"precision": 2}
    )
    
    # Define calculation tasks
    tasks = [
        ("Add 15 and 27", {"operation": "add", "a": 15, "b": 27}),
        ("Multiply 8 by 9", {"operation": "multiply", "a": 8, "b": 9}),
        ("Calculate 100 / 4", {"operation": "divide", "a": 100, "b": 4})
    ]
    
    # Execute tasks
    for task_name, params in tasks:
        result = await calculator.execute_task(task_name, params)
        print(f"{task_name}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🛠️ **Creating Custom Tools**

### **Tutorial: Weather Information Tool**

```python
import asyncio
import httpx
from src.tools.base_tool import BaseTool

class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="weather_tool",
            category="data",
            description="Get weather information for a location"
        )
    
    async def run(self, location: str, units: str = "metric"):
        """Get weather information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.openweathermap.org/data/2.5/weather",
                params={"q": location, "units": units, "appid": "YOUR_API_KEY"}
            )
            return response.json()

# Usage
async def main():
    weather = WeatherTool()
    result = await weather.run("London", "metric")
    print(f"Weather in London: {result['main']['temp']}°C")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🌐 **Web Scraping with BrowserAgent**

### **Tutorial: News Headlines Scraper**

```python
import asyncio
from src.agents.browser_agent import BrowserAgent

async def main():
    # Create browser agent
    browser = BrowserAgent(
        name="news_scraper",
        config={"headless": True, "timeout": 30}
    )
    
    # Scrape news headlines
    result = await browser.execute_task(
        task="Scrape news headlines from BBC",
        parameters={
            "url": "https://www.bbc.com/news",
            "selectors": {
                "headlines": "h3[data-testid='heading']",
                "summaries": "p[data-testid='summary']"
            }
        }
    )
    
    # Process results
    for headline, summary in zip(result["headlines"], result["summaries"]):
        print(f"Headline: {headline}")
        print(f"Summary: {summary}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 **Data Analysis Pipeline**

### **Tutorial: Sales Data Analysis**

```python
import asyncio
from src.tools.data_tools import DataCleaningTool, DataTransformationTool
from src.tools.analysis_tools import DataAnalysisTool, ChartGenerationTool

async def main():
    # Sample sales data
    sales_data = [
        {"date": "2024-01-01", "sales": 1000, "region": "North"},
        {"date": "2024-01-02", "sales": 1200, "region": "South"},
        {"date": "2024-01-03", "sales": None, "region": "East"},
        {"date": "2024-01-04", "sales": 1500, "region": "West"},
        {"date": "2024-01-05", "sales": 1100, "region": "North"}
    ]
    
    # Step 1: Clean data
    cleaner = DataCleaningTool()
    clean_data = await cleaner.run(
        data=sales_data,
        remove_nulls=True,
        remove_empty=True
    )
    
    # Step 2: Transform data
    transformer = DataTransformationTool()
    transformed_data = await transformer.run(
        data=clean_data,
        transformation="normalize"
    )
    
    # Step 3: Analyze data
    analyzer = DataAnalysisTool()
    analysis = await analyzer.run(
        data=transformed_data,
        analysis_type="descriptive"
    )
    
    # Step 4: Generate chart
    chart = ChartGenerationTool()
    chart_path = await chart.run(
        data=transformed_data,
        chart_type="bar",
        title="Sales Analysis"
    )
    
    print(f"Analysis: {analysis}")
    print(f"Chart saved to: {chart_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔄 **Workflow Orchestration**

### **Tutorial: Content Processing Pipeline**

```python
import asyncio
from httpx import AsyncClient
from src.api.server import create_app

async def main():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Define workflow
        workflow = {
            "name": "Content Processing Pipeline",
            "description": "Process web content through multiple steps",
            "steps": [
                {
                    "step_id": "fetch_content",
                    "tool_name": "web_scraping_tool",
                    "parameters": {
                        "url": "https://example.com/article",
                        "selectors": {"title": "h1", "content": "article"}
                    }
                },
                {
                    "step_id": "clean_content",
                    "tool_name": "data_cleaning_tool",
                    "parameters": {
                        "data": "{{fetch_content.result}}",
                        "remove_html": True,
                        "normalize_whitespace": True
                    },
                    "depends_on": ["fetch_content"]
                },
                {
                    "step_id": "analyze_sentiment",
                    "tool_name": "sentiment_analysis_tool",
                    "parameters": {
                        "text": "{{clean_content.result.content}}"
                    },
                    "depends_on": ["clean_content"]
                },
                {
                    "step_id": "generate_summary",
                    "tool_name": "text_summarization_tool",
                    "parameters": {
                        "text": "{{clean_content.result.content}}",
                        "max_length": 100
                    },
                    "depends_on": ["clean_content"]
                }
            ],
            "parallel": False
        }
        
        # Execute workflow
        response = await client.post("/api/v1/workflows/execute", json=workflow)
        workflow_id = response.json()["workflow_id"]
        
        # Monitor progress
        while True:
            status_response = await client.get(f"/api/v1/workflows/{workflow_id}")
            status = status_response.json()
            
            if status["status"] == "completed":
                print("Workflow completed successfully!")
                print(f"Results: {status['results']}")
                break
            elif status["status"] == "failed":
                print(f"Workflow failed: {status.get('error', 'Unknown error')}")
                break
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🌐 **API Integration**

### **Tutorial: Building a REST API Client**

```python
import asyncio
import httpx
from typing import Dict, Any

class OpenManusClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_agent(self, agent_type: str, name: str, config: Dict = None):
        """Create a new agent."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/agents/create",
            json={
                "agent_type": agent_type,
                "name": name,
                "config": config or {}
            }
        )
        return response.json()
    
    async def execute_agent(self, agent_id: str, task: str, parameters: Dict = None):
        """Execute a task with an agent."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/agents/{agent_id}/execute",
            json={
                "task": task,
                "parameters": parameters or {}
            }
        )
        return response.json()
    
    async def execute_tool(self, tool_name: str, parameters: Dict):
        """Execute a tool."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/tools/execute",
            json={
                "tool_name": tool_name,
                "parameters": parameters
            }
        )
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

# Usage
async def main():
    client = OpenManusClient()
    
    try:
        # Create agent
        agent_result = await client.create_agent("simple", "api_test_agent")
        agent_id = agent_result["agent_id"]
        
        # Execute task
        task_result = await client.execute_agent(
            agent_id,
            "Calculate 10 * 5",
            {"a": 10, "b": 5}
        )
        
        # Execute tool
        tool_result = await client.execute_tool(
            "data_analysis_tool",
            {"data": [1, 2, 3, 4, 5], "analysis_type": "descriptive"}
        )
        
        print(f"Agent result: {task_result}")
        print(f"Tool result: {tool_result}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚡ **Performance Optimization**

### **Tutorial: Optimizing Agent Performance**

```python
import asyncio
import time
from src.agents.simple_agent import SimpleAgent

async def benchmark_agents():
    """Benchmark agent performance."""
    num_agents = 100
    tasks_per_agent = 10
    
    # Create agents
    agents = []
    for i in range(num_agents):
        agent = SimpleAgent(name=f"perf_agent_{i}")
        agents.append(agent)
    
    # Execute tasks concurrently
    start_time = time.time()
    
    all_tasks = []
    for agent in agents:
        for j in range(tasks_per_agent):
            task = agent.execute_task(
                f"Calculate {i} * {j}",
                {"a": i, "b": j}
            )
            all_tasks.append(task)
    
    results = await asyncio.gather(*all_tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    total_tasks = num_agents * tasks_per_agent
    
    print(f"Executed {total_tasks} tasks in {total_time:.2f} seconds")
    print(f"Throughput: {total_tasks / total_time:.2f} tasks/second")
    
    return results

# Memory optimization
async def memory_efficient_processing():
    """Process data with memory optimization."""
    data_chunks = [list(range(i, i + 100)) for i in range(0, 1000, 100)]
    
    for chunk in data_chunks:
        # Process chunk
        agent = SimpleAgent(name="memory_agent")
        result = await agent.execute_task(
            "Process chunk",
            {"data": chunk}
        )
        
        # Clean up
        del agent
        
        print(f"Processed chunk: {len(chunk)} items")

if __name__ == "__main__":
    asyncio.run(benchmark_agents())
    asyncio.run(memory_efficient_processing())
```

---

## 🎯 **Next Steps**

1. **Explore More Examples**: Check the `examples/` directory
2. **Read Documentation**: Review the full documentation
3. **Join Community**: Connect with other developers
4. **Contribute**: Help improve the framework
5. **Build Projects**: Create your own AI applications

---

**🚀 Happy coding with OpenManus-Youtu Framework!**