"""
Browser Agent Example.

This example demonstrates how to use the BrowserAgent for web automation,
scraping, form filling, and browser-based interactions.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.agents.browser_agent import BrowserAgent
from src.core.config import UnifiedConfig
from src.core.tool_registry import BaseTool, ToolMetadata, ToolDefinition, ToolCategory
from src.utils.logger import setup_logging


class WebScrapingTool(BaseTool):
    """Example web scraping tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="web_scraping",
            description="Scrape data from web pages",
            category=ToolCategory.AUTOMATION,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "url": {"type": "str", "description": "URL to scrape"},
                "selectors": {"type": "list", "description": "CSS selectors to extract"}
            },
            return_type=dict
        )
    
    async def execute(self, url: str, selectors: list = None, **kwargs) -> dict:
        """Execute web scraping."""
        # Simulate web scraping
        await asyncio.sleep(0.3)  # Simulate network delay
        
        return {
            "url": url,
            "selectors": selectors or ["title", "h1", "p"],
            "scraped_data": {
                "title": "Sample Web Page Title",
                "headings": ["Main Heading", "Sub Heading 1", "Sub Heading 2"],
                "paragraphs": [
                    "This is a sample paragraph from the web page.",
                    "Another paragraph with useful information.",
                    "Final paragraph with additional details."
                ],
                "links": [
                    {"text": "Home", "url": "https://example.com/"},
                    {"text": "About", "url": "https://example.com/about"},
                    {"text": "Contact", "url": "https://example.com/contact"}
                ]
            },
            "status": "success"
        }


class FormAutomationTool(BaseTool):
    """Example form automation tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="form_automation",
            description="Automate form filling and submission",
            category=ToolCategory.AUTOMATION,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "form_data": {"type": "dict", "description": "Form data to fill"},
                "submit": {"type": "bool", "description": "Whether to submit the form"}
            },
            return_type=dict
        )
    
    async def execute(self, form_data: dict, submit: bool = True, **kwargs) -> dict:
        """Execute form automation."""
        # Simulate form automation
        await asyncio.sleep(0.2)  # Simulate form filling time
        
        return {
            "form_data": form_data,
            "submit": submit,
            "result": {
                "fields_filled": len(form_data),
                "submission_status": "success" if submit else "not_submitted",
                "response": "Form submitted successfully" if submit else "Form filled but not submitted"
            },
            "status": "success"
        }


class ScreenshotTool(BaseTool):
    """Example screenshot tool."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="screenshot_capture",
            description="Capture screenshots of web pages",
            category=ToolCategory.AUTOMATION,
            version="1.0.0",
            author="Example"
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "filename": {"type": "str", "description": "Screenshot filename"},
                "full_page": {"type": "bool", "description": "Capture full page"}
            },
            return_type=dict
        )
    
    async def execute(self, filename: str = None, full_page: bool = False, **kwargs) -> dict:
        """Execute screenshot capture."""
        # Simulate screenshot capture
        await asyncio.sleep(0.1)  # Simulate capture time
        
        filename = filename or f"screenshot_{asyncio.get_event_loop().time()}.png"
        
        return {
            "filename": filename,
            "full_page": full_page,
            "result": {
                "screenshot_path": f"/screenshots/{filename}",
                "dimensions": {"width": 1920, "height": 1080},
                "file_size": 245760,  # bytes
                "format": "PNG"
            },
            "status": "success"
        }


async def main():
    """Main example function."""
    # Setup logging
    setup_logging(level="INFO")
    
    print("🌐 Browser Agent Example")
    print("=" * 50)
    
    # Create configuration
    config = UnifiedConfig(
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.7
    )
    
    # Create tools
    tools = [
        WebScrapingTool(),
        FormAutomationTool(),
        ScreenshotTool()
    ]
    
    # Create Browser Agent
    agent = BrowserAgent(
        name="example_browser_agent",
        description="An example browser agent for web automation",
        config=config,
        tools=tools,
        headless=True,
        browser_type="chromium",
        viewport={"width": 1920, "height": 1080}
    )
    
    print(f"Created agent: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Browser type: {agent.browser_type}")
    print(f"Headless mode: {agent.headless}")
    print(f"Viewport: {agent.viewport}")
    print(f"Tools available: {[tool._get_metadata().name for tool in tools]}")
    print()
    
    # Setup agent
    print("Setting up agent...")
    await agent.setup()
    print("✅ Agent setup completed")
    print()
    
    # Example 1: Web Scraping Task
    print("🕷️ Example 1: Web Scraping Task")
    print("-" * 30)
    
    scraping_task = "Scrape data from https://example.com and extract title, headings, and links"
    
    result1 = await agent.run(
        scraping_task,
        url="https://example.com",
        selectors=["title", "h1", "h2", "a"]
    )
    
    print(f"Task: {result1['task']}")
    print(f"Success: {result1['success']}")
    print(f"Execution time: {result1['execution_time']:.2f}s")
    
    if result1['success']:
        print("Results:")
        for key, value in result1['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for result_key, result_value in value.items():
                    if isinstance(result_value, list):
                        print(f"    {result_key}:")
                        for item in result_value:
                            if isinstance(item, dict):
                                print(f"      - {item}")
                            else:
                                print(f"      - {item}")
                    else:
                        print(f"    {result_key}: {result_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 2: Form Automation Task
    print("📝 Example 2: Form Automation Task")
    print("-" * 30)
    
    form_task = "Fill out the contact form with sample data and submit it"
    
    form_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "message": "This is a test message from the browser agent."
    }
    
    result2 = await agent.run(
        form_task,
        url="https://example.com/contact",
        form_data=form_data,
        submit=True
    )
    
    print(f"Task: {result2['task']}")
    print(f"Success: {result2['success']}")
    print(f"Execution time: {result2['execution_time']:.2f}s")
    
    if result2['success']:
        print("Results:")
        for key, value in result2['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for result_key, result_value in value.items():
                    print(f"    {result_key}: {result_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 3: Screenshot Task
    print("📸 Example 3: Screenshot Task")
    print("-" * 30)
    
    screenshot_task = "Take a screenshot of the current page"
    
    result3 = await agent.run(
        screenshot_task,
        url="https://example.com",
        filename="example_page.png",
        full_page=True
    )
    
    print(f"Task: {result3['task']}")
    print(f"Success: {result3['success']}")
    print(f"Execution time: {result3['execution_time']:.2f}s")
    
    if result3['success']:
        print("Results:")
        for key, value in result3['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for result_key, result_value in value.items():
                    print(f"    {result_key}: {result_value}")
            else:
                print(f"  {key}: {value}")
    
    print()
    
    # Example 4: Complex Web Automation Task
    print("🔄 Example 4: Complex Web Automation Task")
    print("-" * 30)
    
    complex_task = "Navigate to a website, scrape data, fill a form, and take a screenshot"
    
    result4 = await agent.run(
        complex_task,
        url="https://example.com",
        form_data={"name": "Test User", "email": "test@example.com"},
        screenshot_filename="complex_automation.png"
    )
    
    print(f"Task: {result4['task']}")
    print(f"Success: {result4['success']}")
    print(f"Execution time: {result4['execution_time']:.2f}s")
    
    if result4['success']:
        print("Results:")
        for key, value in result4['result'].items():
            if key == 'results':
                print(f"  {key}:")
                for result_key, result_value in value.items():
                    print(f"    {result_key}: {result_value}")
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
    print("🎉 Browser Agent Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())