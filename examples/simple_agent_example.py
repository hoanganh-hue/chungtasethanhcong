"""
Simple Agent Example.

This example demonstrates how to use the SimpleAgent for basic tasks
like data analysis, file processing, and simple automation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.agents.simple_agent import SimpleAgent
from src.core.config import UnifiedConfig
from src.core.tool_registry import BaseTool, ToolMetadata, ToolDefinition, ToolCategory
from src.utils.logger import setup_logging


class DataAnalysisTool(BaseTool):
    """Example data analysis tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="data_analysis",
            description="Analyze data and generate insights",
            category=ToolCategory.ANALYSIS,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "data": {"type": "str", "description": "Data to analyze"},
                "analysis_type": {"type": "str", "description": "Type of analysis"}
            },
            return_type=dict
        )
    
    async def execute(self, data: str, analysis_type: str = "basic", **kwargs) -> dict:
        """Execute data analysis."""
        # Simulate data analysis
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "data": data,
            "analysis_type": analysis_type,
            "insights": [
                f"Found {len(data.split())} words in the data",
                f"Data length: {len(data)} characters",
                f"Analysis completed using {analysis_type} method"
            ],
            "summary": f"Successfully analyzed {len(data)} characters of data"
        }


class FileProcessingTool(BaseTool):
    """Example file processing tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_processor",
            description="Process files and extract information",
            category=ToolCategory.FILE,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "file_path": {"type": "str", "description": "Path to the file"},
                "operation": {"type": "str", "description": "Operation to perform"}
            },
            return_type=dict
        )
    
    async def execute(self, file_path: str, operation: str = "read", **kwargs) -> dict:
        """Execute file processing."""
        # Simulate file processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "file_path": file_path,
            "operation": operation,
            "result": f"Successfully performed {operation} on {file_path}",
            "file_info": {
                "exists": True,
                "size": 1024,
                "type": "text"
            }
        }


class WebSearchTool(BaseTool):
    """Example web search tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="web_search",
            description="Search the web for information",
            category=ToolCategory.RESEARCH,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "query": {"type": "str", "description": "Search query"},
                "max_results": {"type": "int", "description": "Maximum number of results"}
            },
            return_type=dict
        )
    
    async def execute(self, query: str, max_results: int = 5, **kwargs) -> dict:
        """Execute web search."""
        # Simulate web search
        await asyncio.sleep(0.2)  # Simulate network delay
        
        return {
            "query": query,
            "max_results": max_results,
            "results": [
                {"title": f"Result 1 for {query}", "url": "https://example.com/1", "snippet": "Sample snippet 1"},
                {"title": f"Result 2 for {query}", "url": "https://example.com/2", "snippet": "Sample snippet 2"},
                {"title": f"Result 3 for {query}", "url": "https://example.com/3", "snippet": "Sample snippet 3"}
            ],
            "total_results": 3
        }


async def main():
    """Main example function."""
    # Setup logging
    setup_logging(level="INFO")
    
    print("🚀 Simple Agent Example")
    print("=" * 50)
    
    # Create configuration
    config = UnifiedConfig(
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.7
    )
    
    # Create tools
    tools = [
        DataAnalysisTool(),
        FileProcessingTool(),
        WebSearchTool()
    ]
    
    # Create Simple Agent
    agent = SimpleAgent(
        name="example_simple_agent",
        description="An example simple agent for demonstration",
        config=config,
        tools=tools,
        max_iterations=3,
        timeout=60
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Tools available: {[tool._get_metadata().name for tool in tools]}")
    print()
    
    # Setup agent
    print("Setting up agent...")
    await agent.setup()
    print("✅ Agent setup completed")
    print()
    
    # Example 1: Data Analysis Task
    print("📊 Example 1: Data Analysis Task")
    print("-" * 30)
    
    data_task = "Analyze the following data: 'The quick brown fox jumps over the lazy dog. This is a sample text for analysis.'"
    
    result1 = await agent.run(data_task)
    
    print(f"Task: {result1['task']}")
    print(f"Success: {result1['success']}")
    print(f"Execution time: {result1['execution_time']:.2f}s")
    
    if result1['success']:
        print("Results:")
        for key, value in result1['result'].items():
            if key == 'results':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 2: File Processing Task
    print("📁 Example 2: File Processing Task")
    print("-" * 30)
    
    file_task = "Process the file at /path/to/sample.txt and extract information"
    
    result2 = await agent.run(file_task, file_path="/path/to/sample.txt", operation="read")
    
    print(f"Task: {result2['task']}")
    print(f"Success: {result2['success']}")
    print(f"Execution time: {result2['execution_time']:.2f}s")
    
    if result2['success']:
        print("Results:")
        for key, value in result2['result'].items():
            print(f"  {key}: {value}")
    
    print()
    
    # Example 3: Web Search Task
    print("🔍 Example 3: Web Search Task")
    print("-" * 30)
    
    search_task = "Search for information about artificial intelligence and machine learning"
    
    result3 = await agent.run(search_task, query="artificial intelligence machine learning", max_results=3)
    
    print(f"Task: {result3['task']}")
    print(f"Success: {result3['success']}")
    print(f"Execution time: {result3['execution_time']:.2f}s")
    
    if result3['success']:
        print("Results:")
        for key, value in result3['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for i, result in enumerate(value, 1):
                    print(f"    {i}. {result['title']}")
                    print(f"       URL: {result['url']}")
                    print(f"       Snippet: {result['snippet']}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 4: Complex Task
    print("🔄 Example 4: Complex Task")
    print("-" * 30)
    
    complex_task = "Search for data analysis techniques, then analyze the results and create a summary report"
    
    result4 = await agent.run(complex_task, query="data analysis techniques", max_results=2)
    
    print(f"Task: {result4['task']}")
    print(f"Success: {result4['success']}")
    print(f"Execution time: {result4['execution_time']:.2f}s")
    
    if result4['success']:
        print("Results:")
        for key, value in result4['result'].items():
            if key == 'results':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Show agent statistics
    print("📈 Agent Statistics")
    print("-" * 30)
    
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print()
    
    # Cleanup
    print("🧹 Cleaning up agent...")
    await agent.cleanup()
    print("✅ Agent cleanup completed")
    
    print()
    print("🎉 Simple Agent Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())