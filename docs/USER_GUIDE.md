# 📚 OpenManus-Youtu Integrated Framework - User Guide

## 🎯 **Getting Started**

Welcome to the OpenManus-Youtu Integrated Framework! This comprehensive guide will help you get started with the most powerful AI Agent platform available.

---

## 📋 **Table of Contents**

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Agent Types](#agent-types)
5. [Tool Categories](#tool-categories)
6. [API Usage](#api-usage)
7. [Workflow Orchestration](#workflow-orchestration)
8. [Advanced Features](#advanced-features)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 **Installation**

### **Prerequisites**
- Python 3.11+
- Docker (optional, for containerized deployment)
- Git

### **Installation Methods**

#### **Method 1: Direct Installation**
```bash
# Clone the repository
git clone https://github.com/openmanus-youtu/framework.git
cd framework

# Install dependencies
pip install -r requirements.txt

# Install the framework
pip install -e .
```

#### **Method 2: Docker Installation**
```bash
# Clone the repository
git clone https://github.com/openmanus-youtu/framework.git
cd framework

# Build and run with Docker Compose
docker-compose up -d
```

#### **Method 3: Development Installation**
```bash
# Clone the repository
git clone https://github.com/openmanus-youtu/framework.git
cd framework

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest tests/
```

---

## ⚡ **Quick Start**

### **1. Start the API Server**
```bash
# Start the FastAPI server
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

### **2. Create Your First Agent**
```python
import asyncio
from src.agents.simple_agent import SimpleAgent

async def main():
    # Create a simple agent
    agent = SimpleAgent(
        name="my_first_agent",
        config={"max_iterations": 10}
    )
    
    # Execute a task
    result = await agent.execute_task(
        task="Calculate the sum of numbers 1 to 100",
        parameters={"numbers": list(range(1, 101))}
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **3. Use Tools Directly**
```python
import asyncio
from src.tools.analysis_tools import DataAnalysisTool

async def main():
    # Create a data analysis tool
    tool = DataAnalysisTool()
    
    # Analyze data
    result = await tool.run(
        data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        analysis_type="descriptive"
    )
    
    print(f"Analysis result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **4. API Usage**
```bash
# Health check
curl http://localhost:8000/health

# Create an agent
curl -X POST http://localhost:8000/api/v1/agents/create \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "simple", "name": "api_agent"}'

# Execute a tool
curl -X POST http://localhost:8000/api/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "data_analysis_tool", "parameters": {"data": [1,2,3,4,5], "analysis_type": "descriptive"}}'
```

---

## 🧠 **Core Concepts**

### **Agents**
Agents are intelligent entities that can execute tasks, make decisions, and interact with tools. They are the core building blocks of the framework.

### **Tools**
Tools are specialized functions that perform specific operations like data analysis, web scraping, or file processing.

### **Workflows**
Workflows orchestrate multiple agents and tools to accomplish complex tasks through step-by-step processes.

### **API**
The REST API provides programmatic access to all framework capabilities.

---

## 🤖 **Agent Types**

### **1. SimpleAgent**
Basic single-purpose agent for straightforward tasks.

```python
from src.agents.simple_agent import SimpleAgent

agent = SimpleAgent(
    name="calculator_agent",
    config={"precision": 2}
)

result = await agent.execute_task(
    task="Calculate 15 * 23",
    parameters={"a": 15, "b": 23}
)
```

### **2. BrowserAgent**
Agent for web automation and browser interactions.

```python
from src.agents.browser_agent import BrowserAgent

agent = BrowserAgent(
    name="web_agent",
    config={"headless": True, "timeout": 30}
)

result = await agent.execute_task(
    task="Navigate to Google and search for 'OpenManus'",
    parameters={"url": "https://www.google.com", "search_term": "OpenManus"}
)
```

### **3. OrchestraAgent**
Agent for coordinating multiple agents and managing complex workflows.

```python
from src.agents.orchestra_agent import OrchestraAgent

agent = OrchestraAgent(
    name="orchestrator",
    config={"max_agents": 5}
)

result = await agent.execute_task(
    task="Coordinate multiple agents to process data",
    parameters={
        "agents": [
            {"type": "simple", "task": "Calculate sum", "data": [1, 2, 3]},
            {"type": "simple", "task": "Calculate product", "data": [4, 5, 6]}
        ]
    }
)
```

### **4. MetaAgent**
Agent for auto-generation and dynamic agent creation.

```python
from src.agents.meta_agent import MetaAgent

agent = MetaAgent(
    name="meta_agent",
    config={"auto_generate": True}
)

result = await agent.execute_task(
    task="Generate a data processing agent configuration",
    parameters={"agent_type": "simple", "capabilities": ["data_processing"]}
)
```

---

## 🛠️ **Tool Categories**

### **1. Web Tools**
Tools for web interaction and browser automation.

```python
from src.tools.web_tools import WebScrapingTool, PlaywrightBrowserTool

# Web scraping
scraper = WebScrapingTool()
data = await scraper.run(
    url="https://example.com",
    selectors={"title": "h1", "content": "p"}
)

# Browser automation
browser = PlaywrightBrowserTool()
result = await browser.run(
    url="https://example.com",
    action="get_title"
)
```

### **2. Search Tools**
Tools for information retrieval and search operations.

```python
from src.tools.search_tools import WebSearchTool, GoogleSearchTool

# Web search
searcher = WebSearchTool()
results = await searcher.run(
    query="OpenManus AI framework",
    max_results=10
)

# Google search
google = GoogleSearchTool()
results = await google.run(
    query="Python FastAPI",
    max_results=5
)
```

### **3. Analysis Tools**
Tools for data analysis and statistical operations.

```python
from src.tools.analysis_tools import DataAnalysisTool, ChartGenerationTool

# Data analysis
analyzer = DataAnalysisTool()
stats = await analyzer.run(
    data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    analysis_type="descriptive"
)

# Chart generation
chart = ChartGenerationTool()
chart_path = await chart.run(
    data=[1, 2, 3, 4, 5],
    chart_type="line",
    title="Sample Chart"
)
```

### **4. Data Tools**
Tools for data processing and manipulation.

```python
from src.tools.data_tools import DataCleaningTool, DataTransformationTool

# Data cleaning
cleaner = DataCleaningTool()
clean_data = await cleaner.run(
    data=[1, 2, None, 4, 5, "", 7, 8, 9, 10],
    remove_nulls=True,
    remove_empty=True
)

# Data transformation
transformer = DataTransformationTool()
transformed = await transformer.run(
    data=[1, 2, 3, 4, 5],
    transformation="normalize"
)
```

### **5. File Tools**
Tools for file operations and document processing.

```python
from src.tools.file_tools import FileReaderTool, FileWriterTool, PDFProcessorTool

# File reading
reader = FileReaderTool()
content = await reader.run(
    file_path="data.txt",
    file_type="text"
)

# File writing
writer = FileWriterTool()
await writer.run(
    file_path="output.txt",
    content="Hello, World!",
    file_type="text"
)

# PDF processing
pdf_processor = PDFProcessorTool()
text = await pdf_processor.run(
    file_path="document.pdf",
    operation="extract_text"
)
```

### **6. Communication Tools**
Tools for messaging and notification systems.

```python
from src.tools.communication_tools import EmailTool, SlackTool, DiscordTool

# Email
email = EmailTool()
await email.run(
    to="user@example.com",
    subject="Test Email",
    body="This is a test email from OpenManus-Youtu"
)

# Slack
slack = SlackTool()
await slack.run(
    channel="#general",
    message="Hello from OpenManus-Youtu!"
)

# Discord
discord = DiscordTool()
await discord.run(
    channel_id="123456789",
    message="Hello from OpenManus-Youtu!"
)
```

### **7. System Tools**
Tools for system monitoring and resource management.

```python
from src.tools.system_tools import SystemMonitorTool, ResourceManagerTool

# System monitoring
monitor = SystemMonitorTool()
stats = await monitor.run(
    metrics=["cpu", "memory", "disk", "network"]
)

# Resource management
manager = ResourceManagerTool()
await manager.run(
    action="cleanup_memory",
    threshold=80
)
```

### **8. Automation Tools**
Tools for workflow automation and task scheduling.

```python
from src.tools.automation_tools import WorkflowAutomationTool, TaskSchedulerTool

# Workflow automation
workflow = WorkflowAutomationTool()
await workflow.run(
    steps=[
        {"tool": "data_cleaning_tool", "params": {"data": [1, 2, None, 4]}},
        {"tool": "data_analysis_tool", "params": {"data": [1, 2, 4], "type": "descriptive"}}
    ]
)

# Task scheduling
scheduler = TaskSchedulerTool()
await scheduler.run(
    task="daily_report",
    schedule="0 9 * * *",  # Every day at 9 AM
    action="generate_report"
)
```

---

## 🌐 **API Usage**

### **Base URL**
```
http://localhost:8000/api/v1
```

### **Authentication**
Currently, the API is open for development. Production deployments should implement authentication.

### **Common Endpoints**

#### **Health Check**
```bash
GET /health
```

#### **List Tools**
```bash
GET /tools?category=web&page=1&page_size=10
```

#### **Execute Tool**
```bash
POST /tools/execute
Content-Type: application/json

{
  "tool_name": "data_analysis_tool",
  "parameters": {
    "data": [1, 2, 3, 4, 5],
    "analysis_type": "descriptive"
  }
}
```

#### **Create Agent**
```bash
POST /agents/create
Content-Type: application/json

{
  "agent_type": "simple",
  "name": "my_agent",
  "config": {"max_iterations": 10}
}
```

#### **Execute Agent**
```bash
POST /agents/{agent_id}/execute
Content-Type: application/json

{
  "agent_type": "simple",
  "task": "Calculate 10 * 5",
  "parameters": {"a": 10, "b": 5}
}
```

#### **Execute Workflow**
```bash
POST /workflows/execute
Content-Type: application/json

{
  "name": "Data Processing Workflow",
  "description": "Process data through multiple steps",
  "steps": [
    {
      "step_id": "step1",
      "tool_name": "data_cleaning_tool",
      "parameters": {"data": [1, 2, None, 4, 5], "remove_nulls": true}
    },
    {
      "step_id": "step2",
      "tool_name": "data_analysis_tool",
      "parameters": {"data": [1, 2, 4, 5], "analysis_type": "descriptive"},
      "depends_on": ["step1"]
    }
  ],
  "parallel": false
}
```

---

## 🔄 **Workflow Orchestration**

### **Creating Workflows**
Workflows allow you to chain multiple agents and tools together to accomplish complex tasks.

```python
from src.api.server import create_app
from httpx import AsyncClient

async def create_workflow():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        workflow_request = {
            "name": "Data Processing Pipeline",
            "description": "Complete data processing workflow",
            "steps": [
                {
                    "step_id": "data_collection",
                    "tool_name": "web_scraping_tool",
                    "parameters": {
                        "url": "https://api.example.com/data",
                        "selectors": {"items": ".data-item"}
                    }
                },
                {
                    "step_id": "data_cleaning",
                    "tool_name": "data_cleaning_tool",
                    "parameters": {
                        "data": "{{data_collection.result}}",
                        "remove_nulls": True
                    },
                    "depends_on": ["data_collection"]
                },
                {
                    "step_id": "data_analysis",
                    "tool_name": "data_analysis_tool",
                    "parameters": {
                        "data": "{{data_cleaning.result}}",
                        "analysis_type": "descriptive"
                    },
                    "depends_on": ["data_cleaning"]
                },
                {
                    "step_id": "report_generation",
                    "tool_name": "report_generation_tool",
                    "parameters": {
                        "data": "{{data_analysis.result}}",
                        "format": "html"
                    },
                    "depends_on": ["data_analysis"]
                }
            ],
            "parallel": False
        }
        
        response = await client.post("/api/v1/workflows/execute", json=workflow_request)
        return response.json()
```

### **Parallel vs Sequential Execution**
- **Sequential**: Steps execute one after another (default)
- **Parallel**: Independent steps execute simultaneously

```python
# Sequential workflow
workflow = {
    "steps": [...],
    "parallel": False  # Steps execute in order
}

# Parallel workflow
workflow = {
    "steps": [...],
    "parallel": True   # Independent steps run simultaneously
}
```

### **Step Dependencies**
Use `depends_on` to specify step dependencies:

```python
{
    "step_id": "step2",
    "tool_name": "data_analysis_tool",
    "parameters": {...},
    "depends_on": ["step1"]  # Wait for step1 to complete
}
```

---

## 🚀 **Advanced Features**

### **Custom Agent Development**
Create custom agents by extending the base `UnifiedAgent` class:

```python
from src.core.unified_agent import UnifiedAgent

class CustomAgent(UnifiedAgent):
    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config or {})
        self.custom_property = "custom_value"
    
    async def execute_task(self, task: str, parameters: dict = None):
        # Custom task execution logic
        if task == "custom_task":
            return await self._handle_custom_task(parameters)
        else:
            return await super().execute_task(task, parameters)
    
    async def _handle_custom_task(self, parameters: dict):
        # Implement custom task logic
        return {"result": "custom_task_completed"}
```

### **Custom Tool Development**
Create custom tools by extending the base `BaseTool` class:

```python
from src.tools.base_tool import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            category="custom",
            description="A custom tool for specific operations"
        )
    
    async def run(self, **kwargs):
        # Implement custom tool logic
        input_data = kwargs.get("input_data")
        operation = kwargs.get("operation", "default")
        
        if operation == "process":
            return await self._process_data(input_data)
        else:
            return await self._default_operation(input_data)
    
    async def _process_data(self, data):
        # Custom processing logic
        return {"processed": data, "status": "success"}
```

### **Configuration Management**
Use environment variables and configuration files:

```python
# .env file
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info

# config.yaml
agents:
  simple:
    max_iterations: 10
    timeout: 30
  browser:
    headless: true
    timeout: 60

tools:
  web:
    timeout: 30
    retry_attempts: 3
  analysis:
    precision: 2
```

### **Monitoring and Logging**
Enable comprehensive monitoring:

```python
import logging
from src.utils.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Use in your code
logger.info("Agent created successfully")
logger.error("Task execution failed", exc_info=True)
```

---

## 📋 **Best Practices**

### **1. Agent Design**
- Keep agents focused on specific tasks
- Use appropriate agent types for different use cases
- Implement proper error handling
- Set reasonable timeouts and limits

### **2. Tool Usage**
- Choose the right tool for the job
- Validate input parameters
- Handle errors gracefully
- Use async operations for better performance

### **3. Workflow Design**
- Design workflows with clear dependencies
- Use parallel execution when possible
- Implement proper error handling
- Monitor workflow execution

### **4. Performance Optimization**
- Use async/await for I/O operations
- Implement connection pooling
- Cache frequently used data
- Monitor resource usage

### **5. Security**
- Validate all inputs
- Use environment variables for secrets
- Implement proper authentication
- Regular security updates

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Agent Creation Fails**
```python
# Check agent configuration
agent = SimpleAgent(
    name="test_agent",
    config={"max_iterations": 10}  # Ensure valid config
)

# Verify agent type
valid_types = ["simple", "browser", "orchestra", "meta"]
assert agent_type in valid_types
```

#### **2. Tool Execution Errors**
```python
# Check tool parameters
result = await tool.run(
    data=[1, 2, 3],  # Ensure data is valid
    analysis_type="descriptive"  # Use valid analysis type
)

# Handle errors
try:
    result = await tool.run(**parameters)
except Exception as e:
    logger.error(f"Tool execution failed: {e}")
```

#### **3. Workflow Dependencies**
```python
# Ensure proper step dependencies
{
    "step_id": "step2",
    "depends_on": ["step1"],  # step1 must exist
    "parameters": {
        "data": "{{step1.result}}"  # Reference step1 result
    }
}
```

#### **4. API Connection Issues**
```bash
# Check server status
curl http://localhost:8000/health

# Verify port availability
netstat -tulpn | grep 8000

# Check logs
tail -f logs/app.log
```

### **Debugging Tips**

1. **Enable Debug Mode**
   ```bash
   export LOG_LEVEL=debug
   python -m uvicorn src.api.server:app --reload
   ```

2. **Use Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug("Debug information")
   ```

3. **Test Components Individually**
   ```python
   # Test agent separately
   agent = SimpleAgent("test")
   result = await agent.execute_task("test_task")
   
   # Test tool separately
   tool = DataAnalysisTool()
   result = await tool.run(data=[1, 2, 3])
   ```

4. **Monitor Resources**
   ```python
   import psutil
   print(f"Memory: {psutil.virtual_memory().percent}%")
   print(f"CPU: {psutil.cpu_percent()}%")
   ```

---

## 📞 **Support**

### **Documentation**
- [API Reference](TOOLS_API_REFERENCE.md)
- [Architecture Guide](architecture.md)
- [Quick Start Guide](quickstart.md)

### **Community**
- GitHub Issues: [Report bugs and request features](https://github.com/openmanus-youtu/framework/issues)
- Discussions: [Community discussions](https://github.com/openmanus-youtu/framework/discussions)

### **Professional Support**
For enterprise support and consulting services, contact our team at support@openmanus-youtu.com

---

**🎉 Congratulations! You're now ready to build amazing AI-powered applications with the OpenManus-Youtu Integrated Framework!**