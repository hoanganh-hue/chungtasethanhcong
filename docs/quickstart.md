# 🚀 Quick Start Guide

Welcome to the OpenManus-Youtu Unified Framework! This guide will help you get started quickly.

## 📋 Prerequisites

- Python 3.12 or higher
- Git
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/openmanus-youtu-unified.git
cd openmanus-youtu-unified
```

### 2. Install Dependencies

#### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

#### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Install Browser Dependencies (Optional)

If you plan to use browser automation features:

```bash
playwright install
```

## ⚙️ Configuration

### 1. Copy Configuration Template

```bash
cp configs/config.example.yaml configs/config.yaml
```

### 2. Edit Configuration

Open `configs/config.yaml` and update the following:

```yaml
# Model configuration
model:
  provider: "openai"  # or "deepseek", "anthropic", etc.
  model_name: "gpt-4o"
  api_key: "your-api-key-here"  # Set via environment variable

# Enable tools you need
tools:
  - "web_search"
  - "file_operations"
  - "data_analysis"
  - "browser_automation"
```

### 3. Set Environment Variables

```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Or for DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-key"
```

## 🎯 Basic Usage

### 1. Simple Agent Execution

```python
from src.core.unified_agent import UnifiedAgent
from src.core.config import UnifiedConfig

# Load configuration
config = UnifiedConfig.load_from_file("configs/config.yaml")

# Create agent
agent = UnifiedAgent(
    name="my-agent",
    description="A helpful assistant",
    config=config
)

# Setup agent
await agent.setup()

# Run agent
result = await agent.run("Analyze this CSV file and create a report")
print(result)

# Cleanup
await agent.cleanup()
```

### 2. Auto Agent Generation

```bash
# Generate agent from description
python scripts/gen_agent.py --prompt "A data analysis agent that processes CSV files"

# Run generated agent
python scripts/run_agent.py --config generated/my_agent.yaml
```

### 3. Using the API Server

```bash
# Start API server
python -m src.api.server

# In another terminal, make requests
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze this data", "config": "default"}'
```

## 📚 Examples

### Web Scraping

```python
from src.agents.browser_agent import BrowserAgent

agent = BrowserAgent(
    name="scraper",
    description="Web scraping agent",
    config=config
)

await agent.setup()
result = await agent.run({
    "url": "https://example.com",
    "action": "scrape",
    "selectors": {
        "title": "h1",
        "content": ".content"
    }
})
```

### Data Analysis

```python
from src.agents.simple_agent import SimpleAgent

agent = SimpleAgent(
    name="analyst",
    description="Data analysis agent",
    config=config
)

await agent.setup()
result = await agent.run({
    "file_path": "data.csv",
    "analysis_type": "descriptive",
    "output_format": "html"
})
```

### Multi-Agent Orchestration

```python
from src.agents.orchestra_agent import OrchestraAgent

agent = OrchestraAgent(
    name="orchestrator",
    description="Multi-agent coordinator",
    config=config
)

await agent.setup()
result = await agent.run({
    "task": "Research and analyze a topic",
    "agents": ["researcher", "analyst", "reporter"],
    "workflow": "sequential"
})
```

## 🔧 Tool Development

### Creating a Custom Tool

```python
from src.core.tool_registry import BaseTool, ToolMetadata, ToolDefinition, ToolCategory

class MyCustomTool(BaseTool):
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_custom_tool",
            description="A custom tool for specific tasks",
            category=ToolCategory.CUSTOM,
            version="1.0.0"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "input": ToolParameter(
                    name="input",
                    type=str,
                    description="Input data",
                    required=True
                )
            },
            return_type=str
        )
    
    async def execute(self, input: str) -> str:
        # Your tool logic here
        return f"Processed: {input}"

# Register the tool
from src.core.tool_registry import tool_registry
tool_registry.register_tool(MyCustomTool)
```

### Using Tools in Agents

```python
# Tools are automatically available to agents based on configuration
result = await agent.run("Use the my_custom_tool to process this data")
```

## 📊 Benchmarking

### Running Benchmarks

```bash
# Run WebWalkerQA benchmark
python scripts/run_benchmark.py --dataset webwalkerqa --config configs/config.yaml

# Run GAIA benchmark
python scripts/run_benchmark.py --dataset gaia --config configs/config.yaml
```

### Custom Benchmarks

```python
from src.eval.benchmark_runner import BenchmarkRunner

runner = BenchmarkRunner(config)
results = await runner.run_benchmark(
    dataset="my_custom_dataset",
    agent=agent,
    metrics=["accuracy", "execution_time"]
)
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t openmanus-youtu-unified .
```

### Run with Docker

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  openmanus-youtu-unified
```

### Docker Compose

```bash
# Create docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache

# Run
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the project directory
   cd openmanus-youtu-unified
   
   # Activate virtual environment
   source .venv/bin/activate
   
   # Install in development mode
   pip install -e .
   ```

2. **API Key Issues**
   ```bash
   # Check environment variables
   echo $OPENAI_API_KEY
   
   # Or set in configuration file
   # configs/config.yaml
   model:
     api_key: "your-key-here"
   ```

3. **Browser Automation Issues**
   ```bash
   # Install browser dependencies
   playwright install
   
   # Check browser installation
   playwright --version
   ```

4. **Memory Issues**
   ```yaml
   # Reduce memory usage in config
   environment:
     resource_limits:
       memory_mb: 4096  # Reduce from 8192
   ```

### Getting Help

- 📖 [Documentation](https://docs.openmanus-youtu.dev)
- 💬 [Discord Community](https://discord.gg/your-invite)
- 🐛 [Issue Tracker](https://github.com/your-org/openmanus-youtu-unified/issues)
- 📧 [Email Support](mailto:support@openmanus-youtu.dev)

## 🎉 Next Steps

Now that you have the framework running, explore these advanced topics:

1. [Agent Development](agent-development.md)
2. [Tool Development](tool-development.md)
3. [Configuration Guide](configuration.md)
4. [API Reference](api-reference.md)
5. [Deployment Guide](deployment.md)

Happy coding! 🚀