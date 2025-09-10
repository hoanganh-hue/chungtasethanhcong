"""
Unified Gemini AI Agent Integration
Integrates Google Gemini AI into the UnifiedAgent framework
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime
from dataclasses import dataclass

from ..core.unified_agent import UnifiedAgent
from ..core.config import UnifiedConfig
from ..core.memory import UnifiedMemory
from ..core.state import AgentState
from ..core.tool_registry import BaseTool
from ..utils.exceptions import AgentError
from ..utils.logger import get_logger

from .gemini_client import GeminiClient, GeminiConfig, GeminiMessage, GeminiModel, OpenManusFunctions
from .context_manager import ContextManager, InputStandardizer, StandardizedInput, ChatContext

logger = get_logger(__name__)

@dataclass
class GeminiAgentConfig:
    """Configuration for Gemini integration in UnifiedAgent."""
    api_key: str
    model: str = GeminiModel.GEMINI_1_5_FLASH.value
    temperature: float = 0.7
    max_tokens: int = 2048
    enable_function_calling: bool = True
    enable_streaming: bool = True
    system_prompt: Optional[str] = None
    context_window_size: int = 10
    max_context_tokens: int = 8000

class UnifiedGeminiAgent(UnifiedAgent):
    """
    Unified Agent with Google Gemini AI integration.
    
    This agent combines the power of the UnifiedAgent framework with
    Google Gemini's advanced language capabilities and function calling.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: UnifiedConfig,
        gemini_config: GeminiAgentConfig,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[UnifiedMemory] = None,
        state: Optional[AgentState] = None
    ):
        """
        Initialize the Unified Gemini Agent.
        
        Args:
            name: Agent name
            description: Agent description
            config: Unified framework configuration
            gemini_config: Gemini-specific configuration
            tools: List of available tools
            memory: Memory management system
            state: Agent state
        """
        super().__init__(name, description, config, tools, memory, state)
        
        self.gemini_config = gemini_config
        self.gemini_client: Optional[GeminiClient] = None
        self.context_manager = ContextManager()
        self.standardizer = InputStandardizer()
        
        # Function calling integration
        self.function_handlers = {}
        self._setup_function_handlers()
        
        # Agent capabilities
        self.capabilities = {
            "natural_language_processing": True,
            "function_calling": True,
            "streaming_responses": True,
            "context_management": True,
            "tool_integration": True,
            "memory_management": True,
            "state_tracking": True
        }
    
    async def initialize(self) -> bool:
        """Initialize the Unified Gemini Agent."""
        try:
            # Initialize parent agent
            if not await super().initialize():
                return False
            
            # Initialize Gemini client
            gemini_client_config = GeminiConfig(
                api_key=self.gemini_config.api_key,
                model=self.gemini_config.model,
                temperature=self.gemini_config.temperature,
                max_tokens=self.gemini_config.max_tokens
            )
            
            self.gemini_client = GeminiClient(gemini_client_config)
            
            if not await self.gemini_client.initialize():
                logger.error("Failed to initialize Gemini client")
                return False
            
            # Register functions if enabled
            if self.gemini_config.enable_function_calling:
                await self._register_functions()
            
            # Set system prompt
            if self.gemini_config.system_prompt:
                await self._set_system_prompt()
            
            logger.info(f"Unified Gemini Agent '{self.name}' initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Unified Gemini Agent: {e}")
            return False
    
    async def _register_functions(self):
        """Register all available functions with Gemini."""
        try:
            # Register CCCD generation function
            cccd_gen_func = OpenManusFunctions.get_cccd_generation_function()
            self.gemini_client.register_function(cccd_gen_func, self._handle_cccd_generation)
            
            # Register CCCD check function
            cccd_check_func = OpenManusFunctions.get_cccd_check_function()
            self.gemini_client.register_function(cccd_check_func, self._handle_cccd_check)
            
            # Register tax lookup function
            tax_lookup_func = OpenManusFunctions.get_tax_lookup_function()
            self.gemini_client.register_function(tax_lookup_func, self._handle_tax_lookup)
            
            # Register data analysis function
            data_analysis_func = OpenManusFunctions.get_data_analysis_function()
            self.gemini_client.register_function(data_analysis_func, self._handle_data_analysis)
            
            # Register web scraping function
            web_scraping_func = OpenManusFunctions.get_web_scraping_function()
            self.gemini_client.register_function(web_scraping_func, self._handle_web_scraping)
            
            # Register form automation function
            form_automation_func = OpenManusFunctions.get_form_automation_function()
            self.gemini_client.register_function(form_automation_func, self._handle_form_automation)
            
            # Register report generation function
            report_generation_func = OpenManusFunctions.get_report_generation_function()
            self.gemini_client.register_function(report_generation_func, self._handle_report_generation)
            
            # Register Excel export function
            excel_export_func = OpenManusFunctions.get_excel_export_function()
            self.gemini_client.register_function(excel_export_func, self._handle_excel_export)
            
            logger.info("All functions registered with Gemini successfully")
            
        except Exception as e:
            logger.error(f"Failed to register functions: {e}")
    
    async def _set_system_prompt(self):
        """Set system prompt for the agent."""
        try:
            system_message = GeminiMessage(
                role="user",
                parts=[{"text": f"System: {self.gemini_config.system_prompt}"}],
                timestamp=datetime.now()
            )
            
            # Store system prompt in context
            await self.context_manager.add_message(
                "system", "system", "system", self.gemini_config.system_prompt
            )
            
            logger.info("System prompt set successfully")
            
        except Exception as e:
            logger.error(f"Failed to set system prompt: {e}")
    
    def _setup_function_handlers(self):
        """Setup function handlers for tool integration."""
        self.function_handlers = {
            "generate_cccd": self._handle_cccd_generation,
            "check_cccd": self._handle_cccd_check,
            "lookup_tax": self._handle_tax_lookup,
            "analyze_data": self._handle_data_analysis,
            "scrape_web": self._handle_web_scraping,
            "automate_form": self._handle_form_automation,
            "generate_report": self._handle_report_generation,
            "export_excel": self._handle_excel_export
        }
    
    async def process_message(
        self, 
        user_input: str, 
        user_id: str = "default",
        session_id: str = "default",
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Process user message using Gemini AI with tool integration.
        
        Args:
            user_input: User's input message
            user_id: User identifier
            session_id: Session identifier
            stream: Whether to stream the response
            
        Yields:
            Response chunks from Gemini AI
        """
        try:
            # Standardize input
            standardized_input = self.standardizer.standardize_input(
                user_input, user_id, session_id
            )
            
            # Add user message to context
            await self.context_manager.add_message(
                user_id, session_id, "user", user_input
            )
            
            # Get or create context
            context = await self.context_manager.get_or_create_context(
                user_id, session_id, self._get_system_prompt()
            )
            
            # Convert context to Gemini messages
            gemini_messages = self._convert_to_gemini_messages(context.messages)
            
            # Process with Gemini
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                gemini_messages, stream=stream
            ):
                if stream:
                    yield chunk
                else:
                    response_chunks.append(chunk)
            
            # Add assistant response to context
            if not stream:
                complete_response = "".join(response_chunks)
                await self.context_manager.add_message(
                    user_id, session_id, "assistant", complete_response
                )
            
            # Update agent state
            await self._update_state("message_processed", {
                "user_input": user_input,
                "response_length": len("".join(response_chunks)) if response_chunks else 0,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            yield f"Lỗi khi xử lý tin nhắn: {str(e)}"
    
    def _convert_to_gemini_messages(self, messages: List) -> List[GeminiMessage]:
        """Convert context messages to Gemini format."""
        gemini_messages = []
        
        for msg in messages:
            if msg.role == "system":
                gemini_msg = GeminiMessage(
                    role="user",
                    parts=[{"text": f"System: {msg.content}"}],
                    timestamp=msg.timestamp
                )
            elif msg.role == "user":
                gemini_msg = GeminiMessage(
                    role="user",
                    parts=[{"text": msg.content}],
                    timestamp=msg.timestamp
                )
            elif msg.role == "assistant":
                gemini_msg = GeminiMessage(
                    role="model",
                    parts=[{"text": msg.content}],
                    timestamp=msg.timestamp
                )
            else:
                continue
            
            gemini_messages.append(gemini_msg)
        
        return gemini_messages
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        if self.gemini_config.system_prompt:
            return self.gemini_config.system_prompt
        
        return f"""
Bạn là {self.name}, một AI Agent thông minh được tích hợp với Google Gemini và OpenManus-Youtu Framework.

🔧 **Thông tin Agent:**
- Tên: {self.name}
- Mô tả: {self.description}
- Khả năng: {', '.join(self.capabilities.keys())}

🛠️ **Công cụ có sẵn:**
{self._get_available_tools_info()}

📋 **Hướng dẫn:**
1. Luôn trả lời bằng tiếng Việt
2. Sử dụng function calling khi cần thực hiện tác vụ cụ thể
3. Tích hợp với các tools và modules có sẵn
4. Quản lý context và memory hiệu quả
5. Cung cấp thông tin chính xác và hữu ích

🎯 **Mục tiêu:** Hỗ trợ người dùng hoàn thành các tác vụ phức tạp thông qua natural language processing, function calling, và tool integration.
        """
    
    def _get_available_tools_info(self) -> str:
        """Get information about available tools."""
        if not self.tools:
            return "Không có tools nào được cấu hình"
        
        tools_info = []
        for tool in self.tools:
            tools_info.append(f"• {tool.name}: {tool.description}")
        
        return "\n".join(tools_info)
    
    async def _update_state(self, event: str, data: Dict[str, Any]):
        """Update agent state."""
        try:
            if self.state:
                await self.state.update_state(event, data)
        except Exception as e:
            logger.error(f"Failed to update state: {e}")
    
    # Function handlers for tool integration
    async def _handle_cccd_generation(self, args: Dict[str, Any]) -> str:
        """Handle CCCD generation function call."""
        try:
            # Use tool registry to find CCCD generation tool
            cccd_tool = self.tool_registry.get_tool("cccd_generation")
            if cccd_tool:
                result = await cccd_tool.execute(args)
                return str(result)
            else:
                return "CCCD generation tool not available"
        except Exception as e:
            return f"Error in CCCD generation: {str(e)}"
    
    async def _handle_cccd_check(self, args: Dict[str, Any]) -> str:
        """Handle CCCD check function call."""
        try:
            cccd_tool = self.tool_registry.get_tool("cccd_check")
            if cccd_tool:
                result = await cccd_tool.execute(args)
                return str(result)
            else:
                return "CCCD check tool not available"
        except Exception as e:
            return f"Error in CCCD check: {str(e)}"
    
    async def _handle_tax_lookup(self, args: Dict[str, Any]) -> str:
        """Handle tax lookup function call."""
        try:
            tax_tool = self.tool_registry.get_tool("tax_lookup")
            if tax_tool:
                result = await tax_tool.execute(args)
                return str(result)
            else:
                return "Tax lookup tool not available"
        except Exception as e:
            return f"Error in tax lookup: {str(e)}"
    
    async def _handle_data_analysis(self, args: Dict[str, Any]) -> str:
        """Handle data analysis function call."""
        try:
            analysis_tool = self.tool_registry.get_tool("data_analysis")
            if analysis_tool:
                result = await analysis_tool.execute(args)
                return str(result)
            else:
                return "Data analysis tool not available"
        except Exception as e:
            return f"Error in data analysis: {str(e)}"
    
    async def _handle_web_scraping(self, args: Dict[str, Any]) -> str:
        """Handle web scraping function call."""
        try:
            scraping_tool = self.tool_registry.get_tool("web_scraping")
            if scraping_tool:
                result = await scraping_tool.execute(args)
                return str(result)
            else:
                return "Web scraping tool not available"
        except Exception as e:
            return f"Error in web scraping: {str(e)}"
    
    async def _handle_form_automation(self, args: Dict[str, Any]) -> str:
        """Handle form automation function call."""
        try:
            form_tool = self.tool_registry.get_tool("form_automation")
            if form_tool:
                result = await form_tool.execute(args)
                return str(result)
            else:
                return "Form automation tool not available"
        except Exception as e:
            return f"Error in form automation: {str(e)}"
    
    async def _handle_report_generation(self, args: Dict[str, Any]) -> str:
        """Handle report generation function call."""
        try:
            report_tool = self.tool_registry.get_tool("report_generation")
            if report_tool:
                result = await report_tool.execute(args)
                return str(result)
            else:
                return "Report generation tool not available"
        except Exception as e:
            return f"Error in report generation: {str(e)}"
    
    async def _handle_excel_export(self, args: Dict[str, Any]) -> str:
        """Handle Excel export function call."""
        try:
            excel_tool = self.tool_registry.get_tool("excel_export")
            if excel_tool:
                result = await excel_tool.execute(args)
                return str(result)
            else:
                return "Excel export tool not available"
        except Exception as e:
            return f"Error in Excel export: {str(e)}"
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "agent_type": "UnifiedGeminiAgent",
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "gemini_model": self.gemini_config.model,
            "function_calling_enabled": self.gemini_config.enable_function_calling,
            "streaming_enabled": self.gemini_config.enable_streaming,
            "available_tools": [tool.name for tool in self.tools] if self.tools else [],
            "memory_enabled": self.memory is not None,
            "state_tracking_enabled": self.state is not None
        }
    
    async def close(self):
        """Close the agent and cleanup resources."""
        try:
            if self.gemini_client:
                await self.gemini_client.close()
            
            await super().close()
            logger.info(f"Unified Gemini Agent '{self.name}' closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing Unified Gemini Agent: {e}")

# Factory function for creating Unified Gemini Agents
async def create_unified_gemini_agent(
    name: str,
    description: str,
    gemini_api_key: str,
    config: Optional[UnifiedConfig] = None,
    tools: Optional[List[BaseTool]] = None,
    memory: Optional[UnifiedMemory] = None,
    **kwargs
) -> UnifiedGeminiAgent:
    """
    Factory function to create a Unified Gemini Agent.
    
    Args:
        name: Agent name
        description: Agent description
        gemini_api_key: Google Gemini API key
        config: Unified framework configuration
        tools: List of available tools
        memory: Memory management system
        **kwargs: Additional configuration options
        
    Returns:
        Initialized UnifiedGeminiAgent instance
    """
    # Create default config if not provided
    if config is None:
        config = UnifiedConfig()
    
    # Create Gemini configuration
    gemini_config = GeminiAgentConfig(
        api_key=gemini_api_key,
        model=kwargs.get("model", GeminiModel.GEMINI_1_5_FLASH.value),
        temperature=kwargs.get("temperature", 0.7),
        max_tokens=kwargs.get("max_tokens", 2048),
        enable_function_calling=kwargs.get("enable_function_calling", True),
        enable_streaming=kwargs.get("enable_streaming", True),
        system_prompt=kwargs.get("system_prompt"),
        context_window_size=kwargs.get("context_window_size", 10),
        max_context_tokens=kwargs.get("max_context_tokens", 8000)
    )
    
    # Create agent
    agent = UnifiedGeminiAgent(
        name=name,
        description=description,
        config=config,
        gemini_config=gemini_config,
        tools=tools,
        memory=memory
    )
    
    # Initialize agent
    if not await agent.initialize():
        raise AgentError(f"Failed to initialize Unified Gemini Agent '{name}'")
    
    return agent