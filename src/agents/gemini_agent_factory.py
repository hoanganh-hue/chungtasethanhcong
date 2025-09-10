"""
Gemini Agent Factory
Factory for creating various types of Gemini-powered agents
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from ..core.unified_agent import UnifiedAgent
from ..core.config import UnifiedConfig
from ..core.memory import UnifiedMemory
from ..core.state import AgentState
from ..core.tool_registry import ToolRegistry, BaseTool
from ..ai.unified_gemini_agent import UnifiedGeminiAgent, GeminiAgentConfig, create_unified_gemini_agent
from ..tools.gemini_tools import (
    create_gemini_chat_tool,
    create_gemini_function_calling_tool,
    create_gemini_code_generation_tool,
    create_gemini_data_analysis_tool,
    create_gemini_text_processing_tool
)
from ..utils.exceptions import AgentError
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GeminiAgentFactory:
    """Factory for creating Gemini-powered agents."""
    
    @staticmethod
    async def create_cccd_agent(
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create a CCCD-focused Gemini agent."""
        try:
            # Create agent with CCCD-specific configuration
            agent = await create_unified_gemini_agent(
                name="CCCD Agent",
                description="AI Agent chuyên xử lý các tác vụ liên quan đến CCCD (tạo, kiểm tra, phân tích)",
                gemini_api_key=api_key,
                config=config,
                model=kwargs.get("model", "gemini-1.5-flash"),
                temperature=kwargs.get("temperature", 0.3),  # Lower temperature for accuracy
                system_prompt="""
Bạn là CCCD Agent, một AI chuyên gia về xử lý CCCD (Căn cước công dân).

🔧 **Chức năng chính:**
- Tạo CCCD theo tỉnh, giới tính, năm sinh
- Kiểm tra thông tin CCCD
- Phân tích dữ liệu CCCD
- Xử lý các vấn đề liên quan đến CCCD

📋 **Hướng dẫn:**
1. Luôn đảm bảo tính chính xác khi xử lý CCCD
2. Tuân thủ quy định pháp luật về CCCD
3. Cung cấp thông tin rõ ràng và chi tiết
4. Xử lý lỗi một cách chuyên nghiệp

🎯 **Mục tiêu:** Hỗ trợ người dùng xử lý các tác vụ CCCD một cách chính xác và hiệu quả.
                """,
                **kwargs
            )
            
            logger.info("CCCD Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create CCCD Agent: {e}")
            raise AgentError(f"Failed to create CCCD Agent: {e}")
    
    @staticmethod
    async def create_tax_agent(
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create a tax-focused Gemini agent."""
        try:
            agent = await create_unified_gemini_agent(
                name="Tax Agent",
                description="AI Agent chuyên xử lý các tác vụ liên quan đến thuế (tra cứu, phân tích, báo cáo)",
                gemini_api_key=api_key,
                config=config,
                model=kwargs.get("model", "gemini-1.5-flash"),
                temperature=kwargs.get("temperature", 0.2),  # Very low temperature for accuracy
                system_prompt="""
Bạn là Tax Agent, một AI chuyên gia về thuế và tài chính.

🔧 **Chức năng chính:**
- Tra cứu mã số thuế
- Phân tích thông tin thuế
- Tạo báo cáo thuế
- Tư vấn về các vấn đề thuế

📋 **Hướng dẫn:**
1. Luôn đảm bảo tính chính xác khi xử lý thông tin thuế
2. Tuân thủ quy định pháp luật về thuế
3. Cung cấp thông tin rõ ràng và cập nhật
4. Xử lý dữ liệu nhạy cảm một cách bảo mật

🎯 **Mục tiêu:** Hỗ trợ người dùng xử lý các tác vụ thuế một cách chính xác và tuân thủ pháp luật.
                """,
                **kwargs
            )
            
            logger.info("Tax Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create Tax Agent: {e}")
            raise AgentError(f"Failed to create Tax Agent: {e}")
    
    @staticmethod
    async def create_data_analysis_agent(
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create a data analysis-focused Gemini agent."""
        try:
            agent = await create_unified_gemini_agent(
                name="Data Analysis Agent",
                description="AI Agent chuyên phân tích dữ liệu và tạo báo cáo",
                gemini_api_key=api_key,
                config=config,
                model=kwargs.get("model", "gemini-1.5-pro"),  # Use Pro model for complex analysis
                temperature=kwargs.get("temperature", 0.4),
                system_prompt="""
Bạn là Data Analysis Agent, một AI chuyên gia về phân tích dữ liệu.

🔧 **Chức năng chính:**
- Phân tích dữ liệu thống kê
- Tạo báo cáo phân tích
- Xác định xu hướng và mẫu
- Đưa ra khuyến nghị dựa trên dữ liệu

📋 **Hướng dẫn:**
1. Sử dụng phương pháp phân tích khoa học
2. Cung cấp kết quả có thể kiểm chứng
3. Giải thích rõ ràng các phát hiện
4. Đưa ra khuyến nghị thực tế

🎯 **Mục tiêu:** Hỗ trợ người dùng phân tích dữ liệu một cách chuyên nghiệp và hiệu quả.
                """,
                **kwargs
            )
            
            logger.info("Data Analysis Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create Data Analysis Agent: {e}")
            raise AgentError(f"Failed to create Data Analysis Agent: {e}")
    
    @staticmethod
    async def create_web_automation_agent(
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create a web automation-focused Gemini agent."""
        try:
            agent = await create_unified_gemini_agent(
                name="Web Automation Agent",
                description="AI Agent chuyên tự động hóa web và scraping dữ liệu",
                gemini_api_key=api_key,
                config=config,
                model=kwargs.get("model", "gemini-1.5-flash"),
                temperature=kwargs.get("temperature", 0.5),
                system_prompt="""
Bạn là Web Automation Agent, một AI chuyên gia về tự động hóa web.

🔧 **Chức năng chính:**
- Web scraping và thu thập dữ liệu
- Tự động hóa form và tương tác web
- Xử lý dữ liệu web
- Tối ưu hóa quy trình web

📋 **Hướng dẫn:**
1. Tuân thủ robots.txt và quy định website
2. Sử dụng rate limiting phù hợp
3. Xử lý lỗi và retry logic
4. Bảo vệ dữ liệu người dùng

🎯 **Mục tiêu:** Hỗ trợ người dùng tự động hóa các tác vụ web một cách hiệu quả và tuân thủ.
                """,
                **kwargs
            )
            
            logger.info("Web Automation Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create Web Automation Agent: {e}")
            raise AgentError(f"Failed to create Web Automation Agent: {e}")
    
    @staticmethod
    async def create_general_purpose_agent(
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create a general-purpose Gemini agent."""
        try:
            agent = await create_unified_gemini_agent(
                name="General Purpose Agent",
                description="AI Agent đa năng có thể xử lý nhiều loại tác vụ khác nhau",
                gemini_api_key=api_key,
                config=config,
                model=kwargs.get("model", "gemini-1.5-flash"),
                temperature=kwargs.get("temperature", 0.7),
                system_prompt="""
Bạn là General Purpose Agent, một AI đa năng và linh hoạt.

🔧 **Chức năng chính:**
- Xử lý ngôn ngữ tự nhiên
- Function calling cho các tác vụ cụ thể
- Tích hợp với các tools và modules
- Hỗ trợ đa dạng các loại yêu cầu

📋 **Hướng dẫn:**
1. Luôn cố gắng hiểu ý định của người dùng
2. Sử dụng function calling khi cần thiết
3. Cung cấp phản hồi hữu ích và chính xác
4. Học hỏi từ tương tác để cải thiện

🎯 **Mục tiêu:** Hỗ trợ người dùng hoàn thành các tác vụ một cách hiệu quả và thông minh.
                """,
                **kwargs
            )
            
            logger.info("General Purpose Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create General Purpose Agent: {e}")
            raise AgentError(f"Failed to create General Purpose Agent: {e}")
    
    @staticmethod
    async def create_custom_agent(
        name: str,
        description: str,
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create a custom Gemini agent with specified parameters."""
        try:
            agent = await create_unified_gemini_agent(
                name=name,
                description=description,
                gemini_api_key=api_key,
                config=config,
                **kwargs
            )
            
            logger.info(f"Custom Agent '{name}' created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create Custom Agent '{name}': {e}")
            raise AgentError(f"Failed to create Custom Agent '{name}': {e}")

class GeminiAgentManager:
    """Manager for multiple Gemini agents."""
    
    def __init__(self):
        self.agents: Dict[str, UnifiedGeminiAgent] = {}
        self.factory = GeminiAgentFactory()
    
    async def create_agent(
        self,
        agent_type: str,
        api_key: str,
        config: Optional[UnifiedConfig] = None,
        **kwargs
    ) -> UnifiedGeminiAgent:
        """Create an agent of specified type."""
        try:
            if agent_type == "cccd":
                agent = await self.factory.create_cccd_agent(api_key, config, **kwargs)
            elif agent_type == "tax":
                agent = await self.factory.create_tax_agent(api_key, config, **kwargs)
            elif agent_type == "data_analysis":
                agent = await self.factory.create_data_analysis_agent(api_key, config, **kwargs)
            elif agent_type == "web_automation":
                agent = await self.factory.create_web_automation_agent(api_key, config, **kwargs)
            elif agent_type == "general":
                agent = await self.factory.create_general_purpose_agent(api_key, config, **kwargs)
            else:
                raise AgentError(f"Unknown agent type: {agent_type}")
            
            # Store agent
            self.agents[agent.name] = agent
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent of type '{agent_type}': {e}")
            raise
    
    async def get_agent(self, name: str) -> Optional[UnifiedGeminiAgent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        agents_info = []
        for name, agent in self.agents.items():
            try:
                capabilities = await agent.get_capabilities()
                agents_info.append({
                    "name": name,
                    "capabilities": capabilities,
                    "status": "active" if agent._initialized else "inactive"
                })
            except Exception as e:
                agents_info.append({
                    "name": name,
                    "error": str(e),
                    "status": "error"
                })
        
        return agents_info
    
    async def close_all_agents(self):
        """Close all agents."""
        for agent in self.agents.values():
            try:
                await agent.close()
            except Exception as e:
                logger.error(f"Error closing agent {agent.name}: {e}")
        
        self.agents.clear()

# Global agent manager instance
gemini_agent_manager = GeminiAgentManager()