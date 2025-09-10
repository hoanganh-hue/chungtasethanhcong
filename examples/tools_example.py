"""
Tools Example.

This example demonstrates how to use different tool categories
in the OpenManus-Youtu Integrated Framework.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.tools.base_tool import ToolRegistry
from src.tools.web_tools import WebTools
from src.tools.search_tools import SearchTools
from src.tools.analysis_tools import AnalysisTools
from src.tools.data_tools import DataTools
from src.tools.file_tools import FileTools
from src.tools.automation_tools import AutomationTools
from src.tools.communication_tools import CommunicationTools
from src.tools.system_tools import SystemTools
from src.utils.logger import setup_logging


async def main():
    """Main example function."""
    # Setup logging
    setup_logging(level="INFO")
    
    print("🔧 Tools Example")
    print("=" * 50)
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Register all tools
    print("📋 Registering tools...")
    
    # Web tools
    for tool in WebTools.get_all_tools():
        registry.register_tool(tool)
    
    # Search tools
    for tool in SearchTools.get_all_tools():
        registry.register_tool(tool)
    
    # Analysis tools
    for tool in AnalysisTools.get_all_tools():
        registry.register_tool(tool)
    
    # Data tools
    for tool in DataTools.get_all_tools():
        registry.register_tool(tool)
    
    # File tools
    for tool in FileTools.get_all_tools():
        registry.register_tool(tool)
    
    # Automation tools
    for tool in AutomationTools.get_all_tools():
        registry.register_tool(tool)
    
    # Communication tools
    for tool in CommunicationTools.get_all_tools():
        registry.register_tool(tool)
    
    # System tools
    for tool in SystemTools.get_all_tools():
        registry.register_tool(tool)
    
    print(f"✅ Registered {len(registry)} tools")
    print()
    
    # Show registry statistics
    stats = registry.get_registry_stats()
    print("📊 Tool Registry Statistics")
    print("-" * 30)
    print(f"Total tools: {stats['total_tools']}")
    print("Tools by category:")
    for category, count in stats['category_counts'].items():
        if count > 0:
            print(f"  {category}: {count}")
    print()
    
    # Example 1: Web Tools
    print("🌐 Example 1: Web Tools")
    print("-" * 30)
    
    # Web scraping
    web_scraping_tool = registry.get_tool("web_scraping")
    if web_scraping_tool:
        result = await web_scraping_tool.execute(
            url="https://example.com",
            selectors={"title": "h1", "links": "a", "content": "p"}
        )
        print(f"Web scraping result: {result['success']}")
        print(f"Scraped data keys: {list(result['scraped_data'].keys())}")
    
    # Browser automation
    browser_tool = registry.get_tool("playwright_browser")
    if browser_tool:
        result = await browser_tool.execute(
            action="navigate",
            url="https://example.com",
            headless=True
        )
        print(f"Browser automation result: {result['success']}")
        print(f"Action: {result['action']}")
    
    print()
    
    # Example 2: Search Tools
    print("🔍 Example 2: Search Tools")
    print("-" * 30)
    
    # Web search
    web_search_tool = registry.get_tool("web_search")
    if web_search_tool:
        result = await web_search_tool.execute(
            query="artificial intelligence machine learning",
            max_results=3
        )
        print(f"Web search result: {result['success']}")
        print(f"Found {len(result['results'])} results")
        for i, search_result in enumerate(result['results'][:2], 1):
            print(f"  {i}. {search_result['title']}")
    
    # Academic search
    academic_search_tool = registry.get_tool("academic_search")
    if academic_search_tool:
        result = await academic_search_tool.execute(
            query="deep learning neural networks",
            database="arxiv",
            max_results=2
        )
        print(f"Academic search result: {result['success']}")
        print(f"Found {len(result['results'])} academic papers")
        for i, paper in enumerate(result['results'][:2], 1):
            print(f"  {i}. {paper['title']}")
    
    print()
    
    # Example 3: Analysis Tools
    print("📊 Example 3: Analysis Tools")
    print("-" * 30)
    
    # Data analysis
    data_analysis_tool = registry.get_tool("data_analysis")
    if data_analysis_tool:
        result = await data_analysis_tool.execute(
            data='{"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}',
            analysis_type="descriptive"
        )
        print(f"Data analysis result: {result['success']}")
        print(f"Analysis type: {result['analysis_type']}")
        if 'analysis_results' in result:
            print(f"Mean: {result['analysis_results'].get('mean', 'N/A')}")
            print(f"Standard deviation: {result['analysis_results'].get('std', 'N/A')}")
    
    # Chart generation
    chart_tool = registry.get_tool("chart_generation")
    if chart_tool:
        result = await chart_tool.execute(
            data={"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]},
            chart_type="line",
            title="Sample Line Chart"
        )
        print(f"Chart generation result: {result['success']}")
        print(f"Chart type: {result['chart_type']}")
        print(f"Output path: {result['chart_metadata']['file_path']}")
    
    print()
    
    # Example 4: Data Tools
    print("🗄️ Example 4: Data Tools")
    print("-" * 30)
    
    # Data cleaning
    data_cleaning_tool = registry.get_tool("data_cleaning")
    if data_cleaning_tool:
        result = await data_cleaning_tool.execute(
            data='{"values": [1, 2, null, 4, 5, 6, 7, 8, 9, 10]}',
            cleaning_options=["handle_missing", "remove_outliers", "normalize"]
        )
        print(f"Data cleaning result: {result['success']}")
        print(f"Original count: {result['original_count']}")
        print(f"Cleaned count: {result['cleaned_count']}")
        print(f"Cleaning operations: {result['cleaning_options']}")
    
    # Data validation
    data_validation_tool = registry.get_tool("data_validation")
    if data_validation_tool:
        result = await data_validation_tool.execute(
            data='{"values": [1, 2, 3, 4, 5]}',
            validation_rules={"min_value": 0, "max_value": 10}
        )
        print(f"Data validation result: {result['success']}")
        print(f"Validation score: {result['validation_results']['validation_score']}")
        print(f"Valid records: {result['validation_results']['valid_records']}")
    
    print()
    
    # Example 5: File Tools
    print("📁 Example 5: File Tools")
    print("-" * 30)
    
    # File reading
    file_reader_tool = registry.get_tool("file_reader")
    if file_reader_tool:
        result = await file_reader_tool.execute(
            file_path="data/sample.csv",
            file_format="csv",
            encoding="utf-8"
        )
        print(f"File reading result: {result['success']}")
        print(f"File format: {result['file_format']}")
        print(f"File size: {result['file_metadata']['file_size']} bytes")
    
    # File writing
    file_writer_tool = registry.get_tool("file_writer")
    if file_writer_tool:
        result = await file_writer_tool.execute(
            data={"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]},
            file_path="output/users.json",
            file_format="json"
        )
        print(f"File writing result: {result['success']}")
        print(f"Output path: {result['file_path']}")
        print(f"File size: {result['file_metadata']['file_size']} bytes")
    
    print()
    
    # Example 6: Automation Tools
    print("🤖 Example 6: Automation Tools")
    print("-" * 30)
    
    # Workflow automation
    workflow_tool = registry.get_tool("workflow_automation")
    if workflow_tool:
        result = await workflow_tool.execute(
            workflow_definition={
                "steps": [
                    {"id": "step1", "action": "data_extraction"},
                    {"id": "step2", "action": "data_processing", "depends_on": ["step1"]},
                    {"id": "step3", "action": "report_generation", "depends_on": ["step2"]}
                ]
            },
            execution_mode="sequential"
        )
        print(f"Workflow automation result: {result['success']}")
        print(f"Execution mode: {result['execution_mode']}")
        print(f"Total steps: {result['execution_results']['total_steps']}")
        print(f"Completed steps: {result['execution_results']['completed_steps']}")
    
    # Task scheduling
    scheduler_tool = registry.get_tool("task_scheduler")
    if scheduler_tool:
        result = await scheduler_tool.execute(
            task_definition={
                "action": "data_backup",
                "parameters": {"source": "/data", "destination": "/backup"}
            },
            schedule="0 2 * * *"
        )
        print(f"Task scheduling result: {result['success']}")
        print(f"Schedule: {result['schedule']}")
        print(f"Next execution: {result['scheduling_results']['next_execution']}")
    
    print()
    
    # Example 7: Communication Tools
    print("📧 Example 7: Communication Tools")
    print("-" * 30)
    
    # Email
    email_tool = registry.get_tool("email")
    if email_tool:
        result = await email_tool.execute(
            to=["user@example.com"],
            subject="Test Email from AI Agent",
            body="This is a test email sent by the AI agent using the email tool.",
            html=False
        )
        print(f"Email sending result: {result['success']}")
        print(f"Recipients: {result['to']}")
        print(f"Subject: {result['subject']}")
    
    # Slack
    slack_tool = registry.get_tool("slack")
    if slack_tool:
        result = await slack_tool.execute(
            channel="#general",
            message="Hello from the AI agent! 🤖",
            username="AI Assistant"
        )
        print(f"Slack messaging result: {result['success']}")
        print(f"Channel: {result['channel']}")
        print(f"Message: {result['message']}")
    
    # Notification
    notification_tool = registry.get_tool("notification")
    if notification_tool:
        result = await notification_tool.execute(
            message="System maintenance completed successfully",
            notification_type="success",
            recipients=["admin@example.com", "team@example.com"],
            channels=["email", "slack"],
            priority="normal"
        )
        print(f"Notification result: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Channels: {result['channels']}")
    
    print()
    
    # Example 8: System Tools
    print("🖥️ Example 8: System Tools")
    print("-" * 30)
    
    # System monitoring
    system_monitor_tool = registry.get_tool("system_monitor")
    if system_monitor_tool:
        result = await system_monitor_tool.execute(
            monitoring_type="all",
            interval=5,
            duration=10
        )
        print(f"System monitoring result: {result['success']}")
        print(f"Monitoring type: {result['monitoring_type']}")
        print(f"System platform: {result['monitoring_results']['system_info']['platform']}")
        if 'alerts' in result['monitoring_results']:
            print(f"Alerts: {len(result['monitoring_results']['alerts'])}")
    
    # Resource management
    resource_manager_tool = registry.get_tool("resource_manager")
    if resource_manager_tool:
        result = await resource_manager_tool.execute(
            resource_type="memory",
            action="cleanup"
        )
        print(f"Resource management result: {result['success']}")
        print(f"Resource type: {result['resource_type']}")
        print(f"Action: {result['action']}")
        print(f"Changes made: {len(result['management_results']['changes_made'])}")
    
    print()
    
    # Example 9: Tool Search and Discovery
    print("🔍 Example 9: Tool Search and Discovery")
    print("-" * 30)
    
    # Search for tools
    search_results = registry.search_tools("web")
    print(f"Found {len(search_results)} tools matching 'web':")
    for tool in search_results:
        print(f"  - {tool._get_metadata().name}: {tool._get_metadata().description}")
    
    # Get tools by category
    from src.tools.base_tool import ToolCategory
    web_tools = registry.get_tools_by_category(ToolCategory.WEB)
    print(f"\nWeb tools ({len(web_tools)}):")
    for tool in web_tools:
        print(f"  - {tool._get_metadata().name}")
    
    analysis_tools = registry.get_tools_by_category(ToolCategory.ANALYSIS)
    print(f"\nAnalysis tools ({len(analysis_tools)}):")
    for tool in analysis_tools:
        print(f"  - {tool._get_metadata().name}")
    
    print()
    
    # Example 10: Tool Information and Metadata
    print("ℹ️ Example 10: Tool Information and Metadata")
    print("-" * 30)
    
    # Get detailed tool information
    web_search_tool = registry.get_tool("web_search")
    if web_search_tool:
        tool_info = web_search_tool.get_info()
        print(f"Tool: {tool_info['metadata']['name']}")
        print(f"Description: {tool_info['metadata']['description']}")
        print(f"Category: {tool_info['metadata']['category']}")
        print(f"Version: {tool_info['metadata']['version']}")
        print(f"Author: {tool_info['metadata']['author']}")
        print(f"Tags: {', '.join(tool_info['metadata']['tags'])}")
        print(f"Parameters: {len(tool_info['definition']['parameters'])}")
        print(f"Examples: {len(tool_info['definition']['examples'])}")
    
    print()
    
    # Show final statistics
    print("📈 Final Statistics")
    print("-" * 30)
    
    total_executions = 0
    total_errors = 0
    
    for tool in registry.get_all_tools():
        stats = tool.get_stats()
        total_executions += stats['execution_count']
        total_errors += stats['error_count']
    
    print(f"Total tool executions: {total_executions}")
    print(f"Total errors: {total_errors}")
    print(f"Success rate: {((total_executions - total_errors) / total_executions * 100):.1f}%" if total_executions > 0 else "N/A")
    
    print()
    print("🎉 Tools Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())