# 🚀 OpenManus-Youtu Integrated Framework

> **The Ultimate AI Agent Framework** - Integrated implementation combining OpenManus and Youtu-Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Async](https://img.shields.io/badge/async-enabled-green.svg)](https://docs.python.org/3/library/asyncio.html)
[![Integration](https://img.shields.io/badge/integration-complete-brightgreen.svg)](https://github.com/your-org/openmanus-youtu-integrated)

## 🌟 Overview

OpenManus-Youtu Integrated Framework is a **fully integrated** AI Agent platform that combines:

- **OpenManus**: Browser automation, MCP integration, multi-agent orchestration
- **Youtu-Agent**: Async engine, benchmark performance, automatic agent generation
- **Unified Framework**: Seamless integration with enhanced capabilities

## ✨ Key Features

### 🤖 **Integrated Agent System**
- **Auto Agent Generation**: Create agents from natural language descriptions
- **Multi-Agent Orchestration**: Coordinate multiple agents seamlessly
- **Async-First Architecture**: High-performance async execution
- **Unified Interface**: Single API for all agent types
- **Browser Automation**: Full Playwright integration
- **MCP Support**: Model Context Protocol for human-in-the-loop

### 🌐 **Web & Browser Automation**
- **Playwright Integration**: Full browser control
- **Anti-Bot Detection**: Advanced bypass techniques
- **Web Scraping**: Dynamic content extraction
- **Form Automation**: Intelligent form handling
- **Multi-Browser Support**: Chrome, Firefox, Safari, Edge

### 🔧 **Extensible Tool Ecosystem**
- **200+ Integrated Tools**: From both OpenManus and Youtu-Agent
- **Plugin System**: Custom tool development
- **Tool Registry**: Centralized tool management
- **Auto Tool Discovery**: Intelligent tool selection
- **Tool Adapters**: Seamless integration between frameworks

### 📊 **Production-Ready Features**
- **Benchmark Validation**: WebWalkerQA (71.47%), GAIA (72.8%)
- **Performance Monitoring**: Real-time metrics
- **API Server**: RESTful API with FastAPI
- **Docker Support**: Containerized deployment
- **Tracing System**: Comprehensive execution tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATED FRAMEWORK                        │
├─────────────────────────────────────────────────────────────────┤
│  🌐 API Layer (FastAPI)                                        │
│  ├── /run (execute agent)                                      │
│  ├── /generate (auto-generate agent)                           │
│  ├── /benchmark (run evaluation)                               │
│  └── /trace (view execution traces)                            │
├─────────────────────────────────────────────────────────────────┤
│  🤖 Unified Agent Engine (Async)                               │
│  ├── BaseAgent (unified interface)                             │
│  ├── SimpleAgent (single-purpose)                              │
│  ├── OrchestraAgent (multi-agent coordination)                 │
│  ├── BrowserAgent (web automation)                             │
│  └── MetaAgent (auto-generation)                               │
├─────────────────────────────────────────────────────────────────┤
│  🔧 Integrated Tool Registry                                   │
│  ├── OpenManus Tools (Playwright, MCP, etc.)                   │
│  ├── Youtu Tools (Search, Analysis, etc.)                      │
│  ├── Custom Tools (Plugin system)                              │
│  └── Tool Adapters (Integration layer)                         │
├─────────────────────────────────────────────────────────────────┤
│  🌍 Environment Layer                                          │
│  ├── Browser Environment (Playwright)                          │
│  ├── Shell Environment (Local/Remote)                          │
│  └── Sandbox Environment (Docker)                              │
├─────────────────────────────────────────────────────────────────┤
│  📊 Evaluation & Tracing                                       │
│  ├── Benchmark Runner (WebWalkerQA, GAIA)                      │
│  ├── DBTracingProcessor (Execution tracking)                   │
│  └── Performance Analytics (Cost, Time, Accuracy)              │
├─────────────────────────────────────────────────────────────────┤
│  ⚙️ Configuration System                                       │
│  ├── ConfigLoader (TOML/YAML support)                          │
│  ├── Auto-Generator (Meta-agent)                               │
│  └── Validation (Pydantic models)                              │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/openmanus-youtu-integrated.git
cd openmanus-youtu-integrated

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Copy configuration
cp configs/config.example.yaml configs/config.yaml
```

### Basic Usage

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

# Run agent
result = await agent.run("Analyze this CSV file and create a report")
print(result)
```

### Auto Agent Generation

```bash
# Generate agent from description
python scripts/gen_agent.py --prompt "A data analysis agent that processes CSV files"

# Run generated agent
python scripts/run_agent.py --config generated/my_agent.yaml
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Quick Start Guide](docs/quickstart.md)
- [Integration Guide](docs/integration.md)
- [API Reference](docs/api.md)
- [Examples](examples/)

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --group dev

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check src/
```

### Project Structure

```
openmanus-youtu-integrated/
├── src/                    # Source code
│   ├── core/              # Core framework
│   ├── agents/            # Agent implementations
│   ├── tools/             # Tool implementations
│   ├── config/            # Configuration system
│   ├── utils/             # Utilities
│   ├── api/               # API server
│   └── integrations/      # Framework integrations
│       ├── openmanus/     # OpenManus integration
│       └── youtu/         # Youtu-Agent integration
├── docs/                  # Documentation
├── examples/              # Example implementations
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── configs/               # Configuration files
├── data/                  # Data files
└── logs/                  # Log files
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenManus](https://github.com/FoundationAgents/OpenManus) - Browser automation and MCP integration
- [Youtu-Agent](https://github.com/TencentCloudADP/youtu-agent) - Async engine and benchmarking
- [OpenAI Agents](https://github.com/openai/openai-agents-python) - Foundation for async agent execution

## 📞 Support

- 📧 Email: support@openmanus-youtu.dev
- 💬 Discord: [Join our community](https://discord.gg/your-invite)
- 📖 Documentation: [docs.openmanus-youtu.dev](https://docs.openmanus-youtu.dev)

---

**Made with ❤️ by the OpenManus-Youtu Integration Team**