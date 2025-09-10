"""
Web Tools Implementation.

This module provides web-related tools including browser automation,
web scraping, and web interaction capabilities from OpenManus.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from .base_tool import BaseTool, ToolMetadata, ToolDefinition, ToolParameter, ToolCategory
from ..utils.exceptions import ToolError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PlaywrightBrowserTool(BaseTool):
    """Tool for browser automation using Playwright."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="playwright_browser",
            description="Browser automation tool using Playwright",
            category=ToolCategory.WEB,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["browser", "automation", "playwright", "web"],
            dependencies=["playwright"],
            requirements={
                "browser": "chromium, firefox, or webkit",
                "headless": "boolean"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "action": ToolParameter(
                    name="action",
                    type=str,
                    description="Browser action to perform",
                    required=True,
                    choices=["navigate", "click", "type", "screenshot", "evaluate", "wait"]
                ),
                "url": ToolParameter(
                    name="url",
                    type=str,
                    description="URL to navigate to",
                    required=False,
                    pattern=r"^https?://.*"
                ),
                "selector": ToolParameter(
                    name="selector",
                    type=str,
                    description="CSS selector for element",
                    required=False
                ),
                "text": ToolParameter(
                    name="text",
                    type=str,
                    description="Text to type or search for",
                    required=False
                ),
                "timeout": ToolParameter(
                    name="timeout",
                    type=int,
                    description="Timeout in milliseconds",
                    required=False,
                    default=30000,
                    min_value=1000,
                    max_value=300000
                ),
                "headless": ToolParameter(
                    name="headless",
                    type=bool,
                    description="Run browser in headless mode",
                    required=False,
                    default=True
                )
            },
            return_type=dict,
            examples=[
                {
                    "action": "navigate",
                    "url": "https://example.com",
                    "headless": True
                },
                {
                    "action": "click",
                    "selector": "button.submit",
                    "timeout": 10000
                },
                {
                    "action": "type",
                    "selector": "input[name='email']",
                    "text": "user@example.com"
                }
            ],
            error_codes={
                "BROWSER_ERROR": "Browser operation failed",
                "SELECTOR_ERROR": "Element selector not found",
                "TIMEOUT_ERROR": "Operation timed out",
                "NAVIGATION_ERROR": "Navigation failed"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute browser automation."""
        try:
            action = kwargs.get("action")
            url = kwargs.get("url")
            selector = kwargs.get("selector")
            text = kwargs.get("text")
            timeout = kwargs.get("timeout", 30000)
            headless = kwargs.get("headless", True)
            
            # Simulate Playwright browser automation
            await asyncio.sleep(0.2)  # Simulate browser operation time
            
            result = {
                "action": action,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            if action == "navigate":
                result.update({
                    "url": url,
                    "title": f"Page at {url}",
                    "status": "navigated"
                })
            elif action == "click":
                result.update({
                    "selector": selector,
                    "status": "clicked"
                })
            elif action == "type":
                result.update({
                    "selector": selector,
                    "text": text,
                    "status": "typed"
                })
            elif action == "screenshot":
                result.update({
                    "screenshot_path": f"screenshots/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    "status": "captured"
                })
            elif action == "evaluate":
                result.update({
                    "selector": selector,
                    "result": "evaluation_result",
                    "status": "evaluated"
                })
            elif action == "wait":
                result.update({
                    "selector": selector,
                    "timeout": timeout,
                    "status": "waited"
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Playwright browser operation failed: {e}")
            raise ToolError(f"Browser operation failed: {e}") from e


class WebScrapingTool(BaseTool):
    """Tool for web scraping and data extraction."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="web_scraping",
            description="Web scraping and data extraction tool",
            category=ToolCategory.WEB,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["scraping", "extraction", "web", "data"],
            dependencies=["beautifulsoup4", "requests"],
            requirements={
                "url": "valid HTTP/HTTPS URL",
                "selectors": "CSS selectors for data extraction"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "url": ToolParameter(
                    name="url",
                    type=str,
                    description="URL to scrape",
                    required=True,
                    pattern=r"^https?://.*"
                ),
                "selectors": ToolParameter(
                    name="selectors",
                    type=dict,
                    description="CSS selectors for data extraction",
                    required=True
                ),
                "wait_time": ToolParameter(
                    name="wait_time",
                    type=int,
                    description="Wait time in seconds before scraping",
                    required=False,
                    default=2,
                    min_value=0,
                    max_value=30
                ),
                "headers": ToolParameter(
                    name="headers",
                    type=dict,
                    description="HTTP headers to send",
                    required=False
                ),
                "follow_redirects": ToolParameter(
                    name="follow_redirects",
                    type=bool,
                    description="Follow HTTP redirects",
                    required=False,
                    default=True
                )
            },
            return_type=dict,
            examples=[
                {
                    "url": "https://example.com",
                    "selectors": {
                        "title": "h1",
                        "links": "a",
                        "content": "p"
                    }
                }
            ],
            error_codes={
                "SCRAPING_ERROR": "Web scraping failed",
                "SELECTOR_ERROR": "CSS selector not found",
                "NETWORK_ERROR": "Network request failed",
                "PARSING_ERROR": "HTML parsing failed"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute web scraping."""
        try:
            url = kwargs.get("url")
            selectors = kwargs.get("selectors", {})
            wait_time = kwargs.get("wait_time", 2)
            headers = kwargs.get("headers", {})
            follow_redirects = kwargs.get("follow_redirects", True)
            
            # Simulate web scraping
            await asyncio.sleep(wait_time + 0.1)  # Simulate scraping time
            
            # Generate mock scraped data
            scraped_data = {}
            for key, selector in selectors.items():
                if key == "title":
                    scraped_data[key] = f"Sample Title from {url}"
                elif key == "links":
                    scraped_data[key] = [
                        {"text": "Home", "url": f"{url}/home"},
                        {"text": "About", "url": f"{url}/about"},
                        {"text": "Contact", "url": f"{url}/contact"}
                    ]
                elif key == "content":
                    scraped_data[key] = [
                        "This is sample content from the scraped page.",
                        "Another paragraph with useful information.",
                        "Final paragraph with additional details."
                    ]
                else:
                    scraped_data[key] = f"Sample data for {key} using selector {selector}"
            
            return {
                "url": url,
                "selectors": selectors,
                "scraped_data": scraped_data,
                "wait_time": wait_time,
                "headers": headers,
                "follow_redirects": follow_redirects,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            raise ToolError(f"Web scraping failed: {e}") from e


class FormAutomationTool(BaseTool):
    """Tool for form automation and submission."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="form_automation",
            description="Form automation and submission tool",
            category=ToolCategory.WEB,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["form", "automation", "submission", "web"],
            dependencies=["playwright"],
            requirements={
                "form_data": "form field data",
                "submit": "whether to submit the form"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "form_data": ToolParameter(
                    name="form_data",
                    type=dict,
                    description="Form field data to fill",
                    required=True
                ),
                "submit": ToolParameter(
                    name="submit",
                    type=bool,
                    description="Whether to submit the form",
                    required=False,
                    default=True
                ),
                "submit_selector": ToolParameter(
                    name="submit_selector",
                    type=str,
                    description="CSS selector for submit button",
                    required=False,
                    default="input[type='submit'], button[type='submit']"
                ),
                "validation": ToolParameter(
                    name="validation",
                    type=bool,
                    description="Validate form before submission",
                    required=False,
                    default=True
                ),
                "timeout": ToolParameter(
                    name="timeout",
                    type=int,
                    description="Timeout in milliseconds",
                    required=False,
                    default=10000,
                    min_value=1000,
                    max_value=60000
                )
            },
            return_type=dict,
            examples=[
                {
                    "form_data": {
                        "name": "John Doe",
                        "email": "john@example.com",
                        "message": "Hello world"
                    },
                    "submit": True
                }
            ],
            error_codes={
                "FORM_ERROR": "Form automation failed",
                "FIELD_ERROR": "Form field not found",
                "VALIDATION_ERROR": "Form validation failed",
                "SUBMISSION_ERROR": "Form submission failed"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute form automation."""
        try:
            form_data = kwargs.get("form_data", {})
            submit = kwargs.get("submit", True)
            submit_selector = kwargs.get("submit_selector", "input[type='submit'], button[type='submit']")
            validation = kwargs.get("validation", True)
            timeout = kwargs.get("timeout", 10000)
            
            # Simulate form automation
            await asyncio.sleep(0.3)  # Simulate form filling time
            
            # Validate form data
            validation_result = {}
            if validation:
                for field, value in form_data.items():
                    if not value or (isinstance(value, str) and len(value.strip()) == 0):
                        validation_result[field] = "required"
                    else:
                        validation_result[field] = "valid"
            
            result = {
                "form_data": form_data,
                "submit": submit,
                "submit_selector": submit_selector,
                "validation": validation,
                "validation_result": validation_result,
                "timeout": timeout,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            if submit:
                result["submission_result"] = {
                    "status": "submitted",
                    "response_url": "https://example.com/thank-you",
                    "response_status": 200
                }
            else:
                result["submission_result"] = {
                    "status": "filled_not_submitted"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Form automation failed: {e}")
            raise ToolError(f"Form automation failed: {e}") from e


class ScreenshotCaptureTool(BaseTool):
    """Tool for capturing screenshots of web pages."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="screenshot_capture",
            description="Screenshot capture tool for web pages",
            category=ToolCategory.WEB,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["screenshot", "capture", "image", "web"],
            dependencies=["playwright"],
            requirements={
                "url": "URL to capture",
                "filename": "screenshot filename"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "url": ToolParameter(
                    name="url",
                    type=str,
                    description="URL to capture",
                    required=True,
                    pattern=r"^https?://.*"
                ),
                "filename": ToolParameter(
                    name="filename",
                    type=str,
                    description="Screenshot filename",
                    required=False
                ),
                "full_page": ToolParameter(
                    name="full_page",
                    type=bool,
                    description="Capture full page",
                    required=False,
                    default=False
                ),
                "viewport": ToolParameter(
                    name="viewport",
                    type=dict,
                    description="Viewport dimensions",
                    required=False,
                    default={"width": 1920, "height": 1080}
                ),
                "quality": ToolParameter(
                    name="quality",
                    type=int,
                    description="Image quality (0-100)",
                    required=False,
                    default=90,
                    min_value=0,
                    max_value=100
                )
            },
            return_type=dict,
            examples=[
                {
                    "url": "https://example.com",
                    "filename": "example_page.png",
                    "full_page": True
                }
            ],
            error_codes={
                "CAPTURE_ERROR": "Screenshot capture failed",
                "NAVIGATION_ERROR": "Page navigation failed",
                "VIEWPORT_ERROR": "Viewport configuration failed",
                "SAVE_ERROR": "Screenshot save failed"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute screenshot capture."""
        try:
            url = kwargs.get("url")
            filename = kwargs.get("filename")
            full_page = kwargs.get("full_page", False)
            viewport = kwargs.get("viewport", {"width": 1920, "height": 1080})
            quality = kwargs.get("quality", 90)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Simulate screenshot capture
            await asyncio.sleep(0.2)  # Simulate capture time
            
            return {
                "url": url,
                "filename": filename,
                "full_page": full_page,
                "viewport": viewport,
                "quality": quality,
                "screenshot_path": f"screenshots/{filename}",
                "file_size": 245760,  # bytes
                "dimensions": viewport,
                "format": "PNG",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            raise ToolError(f"Screenshot capture failed: {e}") from e


class ElementInteractionTool(BaseTool):
    """Tool for interacting with web page elements."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="element_interaction",
            description="Web page element interaction tool",
            category=ToolCategory.WEB,
            version="1.0.0",
            author="OpenManus Integration",
            tags=["element", "interaction", "web", "automation"],
            dependencies=["playwright"],
            requirements={
                "selector": "CSS selector for element",
                "action": "interaction action"
            }
        )
    
    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            metadata=self._get_metadata(),
            parameters={
                "selector": ToolParameter(
                    name="selector",
                    type=str,
                    description="CSS selector for element",
                    required=True
                ),
                "action": ToolParameter(
                    name="action",
                    type=str,
                    description="Interaction action",
                    required=True,
                    choices=["click", "hover", "double_click", "right_click", "focus", "blur", "scroll"]
                ),
                "text": ToolParameter(
                    name="text",
                    type=str,
                    description="Text to type (for input elements)",
                    required=False
                ),
                "wait_for": ToolParameter(
                    name="wait_for",
                    type=str,
                    description="Wait for element state",
                    required=False,
                    choices=["visible", "hidden", "attached", "detached"]
                ),
                "timeout": ToolParameter(
                    name="timeout",
                    type=int,
                    description="Timeout in milliseconds",
                    required=False,
                    default=5000,
                    min_value=1000,
                    max_value=30000
                )
            },
            return_type=dict,
            examples=[
                {
                    "selector": "button.submit",
                    "action": "click",
                    "timeout": 10000
                },
                {
                    "selector": "input[name='email']",
                    "action": "focus",
                    "text": "user@example.com"
                }
            ],
            error_codes={
                "INTERACTION_ERROR": "Element interaction failed",
                "SELECTOR_ERROR": "Element selector not found",
                "ACTION_ERROR": "Invalid interaction action",
                "TIMEOUT_ERROR": "Interaction timed out"
            }
        )
    
    async def _execute(self, **kwargs) -> dict:
        """Execute element interaction."""
        try:
            selector = kwargs.get("selector")
            action = kwargs.get("action")
            text = kwargs.get("text")
            wait_for = kwargs.get("wait_for")
            timeout = kwargs.get("timeout", 5000)
            
            # Simulate element interaction
            await asyncio.sleep(0.1)  # Simulate interaction time
            
            result = {
                "selector": selector,
                "action": action,
                "text": text,
                "wait_for": wait_for,
                "timeout": timeout,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add action-specific results
            if action == "click":
                result["result"] = "element_clicked"
            elif action == "hover":
                result["result"] = "element_hovered"
            elif action == "double_click":
                result["result"] = "element_double_clicked"
            elif action == "right_click":
                result["result"] = "element_right_clicked"
            elif action == "focus":
                result["result"] = "element_focused"
            elif action == "blur":
                result["result"] = "element_blurred"
            elif action == "scroll":
                result["result"] = "element_scrolled"
            
            if text:
                result["typed_text"] = text
            
            return result
            
        except Exception as e:
            logger.error(f"Element interaction failed: {e}")
            raise ToolError(f"Element interaction failed: {e}") from e


class WebTools:
    """Collection of web-related tools."""
    
    @staticmethod
    def get_all_tools() -> List[BaseTool]:
        """Get all web tools."""
        return [
            PlaywrightBrowserTool(),
            WebScrapingTool(),
            FormAutomationTool(),
            ScreenshotCaptureTool(),
            ElementInteractionTool()
        ]
    
    @staticmethod
    def get_tool_by_name(name: str) -> Optional[BaseTool]:
        """Get a specific web tool by name."""
        tools = {tool._get_metadata().name: tool for tool in WebTools.get_all_tools()}
        return tools.get(name)
    
    @staticmethod
    def get_tools_by_tag(tag: str) -> List[BaseTool]:
        """Get web tools by tag."""
        return [
            tool for tool in WebTools.get_all_tools()
            if tag in tool._get_metadata().tags
        ]