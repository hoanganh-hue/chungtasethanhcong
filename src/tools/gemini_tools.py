"""
Gemini AI Tools for Unified Framework
Tools that integrate with Google Gemini AI capabilities
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..core.tool_registry import BaseTool, ToolMetadata, ToolCategory, ToolStatus
from ..utils.exceptions import ToolError
from ..utils.logger import get_logger
from ..ai.gemini_client import GeminiClient, GeminiConfig, GeminiMessage, GeminiModel

logger = get_logger(__name__)

class GeminiAITool(BaseTool):
    """Base class for Gemini AI tools."""
    
    def __init__(
        self,
        name: str,
        description: str,
        gemini_config: GeminiConfig,
        **kwargs
    ):
        super().__init__(name, description, **kwargs)
        self.gemini_config = gemini_config
        self.gemini_client: Optional[GeminiClient] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the Gemini client."""
        try:
            self.gemini_client = GeminiClient(self.gemini_config)
            self._initialized = await self.gemini_client.initialize()
            return self._initialized
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client for {self.name}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.gemini_client:
            await self.gemini_client.close()

class GeminiChatTool(GeminiAITool):
    """Tool for Gemini AI chat interactions."""
    
    def __init__(self, gemini_config: GeminiConfig, **kwargs):
        super().__init__(
            name="gemini_chat",
            description="Chat with Google Gemini AI for natural language processing",
            gemini_config=gemini_config,
            category=ToolCategory.COMMUNICATION,
            **kwargs
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat with Gemini AI."""
        try:
            if not self._initialized:
                if not await self.initialize():
                    raise ToolError("Failed to initialize Gemini client")
            
            message = input_data.get("message", "")
            if not message:
                raise ToolError("Message is required")
            
            # Create Gemini message
            gemini_message = GeminiMessage(
                role="user",
                parts=[{"text": message}],
                timestamp=datetime.now()
            )
            
            # Generate response
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                [gemini_message], stream=False
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            
            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_config.model
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class GeminiFunctionCallingTool(GeminiAITool):
    """Tool for Gemini AI function calling."""
    
    def __init__(self, gemini_config: GeminiConfig, **kwargs):
        super().__init__(
            name="gemini_function_calling",
            description="Execute function calls using Google Gemini AI",
            gemini_config=gemini_config,
            category=ToolCategory.AUTOMATION,
            **kwargs
        )
        self.function_handlers = {}
    
    def register_function(self, function_name: str, handler: callable):
        """Register a function handler."""
        self.function_handlers[function_name] = handler
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute function calling with Gemini AI."""
        try:
            if not self._initialized:
                if not await self.initialize():
                    raise ToolError("Failed to initialize Gemini client")
            
            message = input_data.get("message", "")
            if not message:
                raise ToolError("Message is required")
            
            # Create Gemini message
            gemini_message = GeminiMessage(
                role="user",
                parts=[{"text": message}],
                timestamp=datetime.now()
            )
            
            # Generate response with function calling
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                [gemini_message], stream=False
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            
            return {
                "success": True,
                "response": response,
                "function_calls": self._extract_function_calls(response),
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_config.model
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini function calling: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_function_calls(self, response: str) -> List[Dict[str, Any]]:
        """Extract function calls from response."""
        # This would parse the response for function calls
        # Implementation depends on Gemini's function calling format
        return []

class GeminiCodeGenerationTool(GeminiAITool):
    """Tool for code generation using Gemini AI."""
    
    def __init__(self, gemini_config: GeminiConfig, **kwargs):
        super().__init__(
            name="gemini_code_generation",
            description="Generate code using Google Gemini AI",
            gemini_config=gemini_config,
            category=ToolCategory.AUTOMATION,
            **kwargs
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation with Gemini AI."""
        try:
            if not self._initialized:
                if not await self.initialize():
                    raise ToolError("Failed to initialize Gemini client")
            
            prompt = input_data.get("prompt", "")
            language = input_data.get("language", "python")
            context = input_data.get("context", "")
            
            if not prompt:
                raise ToolError("Prompt is required")
            
            # Create enhanced prompt for code generation
            enhanced_prompt = f"""
Generate {language} code based on the following requirements:

Requirements: {prompt}

Context: {context}

Please provide:
1. Complete, working code
2. Brief explanation of the code
3. Usage examples if applicable

Format the response as:
```{language}
[code here]
```

Explanation: [explanation here]

Examples: [examples here]
            """
            
            # Create Gemini message
            gemini_message = GeminiMessage(
                role="user",
                parts=[{"text": enhanced_prompt}],
                timestamp=datetime.now()
            )
            
            # Generate response
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                [gemini_message], stream=False
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            
            return {
                "success": True,
                "code": self._extract_code(response, language),
                "explanation": self._extract_explanation(response),
                "examples": self._extract_examples(response),
                "full_response": response,
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_config.model
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini code generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_code(self, response: str, language: str) -> str:
        """Extract code from response."""
        import re
        pattern = f"```{language}\\n(.*?)\\n```"
        match = re.search(pattern, response, re.DOTALL)
        return match.group(1) if match else ""
    
    def _extract_explanation(self, response: str) -> str:
        """Extract explanation from response."""
        import re
        pattern = r"Explanation:\s*(.*?)(?=Examples:|$)"
        match = re.search(pattern, response, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_examples(self, response: str) -> str:
        """Extract examples from response."""
        import re
        pattern = r"Examples:\s*(.*?)$"
        match = re.search(pattern, response, re.DOTALL)
        return match.group(1).strip() if match else ""

class GeminiDataAnalysisTool(GeminiAITool):
    """Tool for data analysis using Gemini AI."""
    
    def __init__(self, gemini_config: GeminiConfig, **kwargs):
        super().__init__(
            name="gemini_data_analysis",
            description="Analyze data using Google Gemini AI",
            gemini_config=gemini_config,
            category=ToolCategory.ANALYSIS,
            **kwargs
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis with Gemini AI."""
        try:
            if not self._initialized:
                if not await self.initialize():
                    raise ToolError("Failed to initialize Gemini client")
            
            data = input_data.get("data", "")
            analysis_type = input_data.get("analysis_type", "general")
            context = input_data.get("context", "")
            
            if not data:
                raise ToolError("Data is required")
            
            # Create analysis prompt
            analysis_prompt = f"""
Analyze the following data:

Data: {data}

Analysis Type: {analysis_type}
Context: {context}

Please provide:
1. Data summary and key insights
2. Statistical analysis if applicable
3. Patterns and trends identified
4. Recommendations based on the analysis
5. Potential issues or anomalies

Format the response clearly with sections for each aspect.
            """
            
            # Create Gemini message
            gemini_message = GeminiMessage(
                role="user",
                parts=[{"text": analysis_prompt}],
                timestamp=datetime.now()
            )
            
            # Generate response
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                [gemini_message], stream=False
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            
            return {
                "success": True,
                "analysis": response,
                "data_size": len(str(data)),
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_config.model
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini data analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class GeminiTextProcessingTool(GeminiAITool):
    """Tool for text processing using Gemini AI."""
    
    def __init__(self, gemini_config: GeminiConfig, **kwargs):
        super().__init__(
            name="gemini_text_processing",
            description="Process text using Google Gemini AI (summarization, translation, etc.)",
            gemini_config=gemini_config,
            category=ToolCategory.DATA,
            **kwargs
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text processing with Gemini AI."""
        try:
            if not self._initialized:
                if not await self.initialize():
                    raise ToolError("Failed to initialize Gemini client")
            
            text = input_data.get("text", "")
            operation = input_data.get("operation", "summarize")
            language = input_data.get("language", "vi")
            
            if not text:
                raise ToolError("Text is required")
            
            # Create operation-specific prompt
            if operation == "summarize":
                prompt = f"Summarize the following text in {language}:\n\n{text}"
            elif operation == "translate":
                target_lang = input_data.get("target_language", "en")
                prompt = f"Translate the following text from {language} to {target_lang}:\n\n{text}"
            elif operation == "extract_keywords":
                prompt = f"Extract key keywords and phrases from the following text:\n\n{text}"
            elif operation == "sentiment_analysis":
                prompt = f"Analyze the sentiment of the following text:\n\n{text}"
            else:
                prompt = f"Process the following text with operation '{operation}':\n\n{text}"
            
            # Create Gemini message
            gemini_message = GeminiMessage(
                role="user",
                parts=[{"text": prompt}],
                timestamp=datetime.now()
            )
            
            # Generate response
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                [gemini_message], stream=False
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            
            return {
                "success": True,
                "result": response,
                "operation": operation,
                "input_length": len(text),
                "output_length": len(response),
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_config.model
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini text processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Factory functions for creating Gemini tools
def create_gemini_chat_tool(api_key: str, model: str = "gemini-1.5-flash") -> GeminiChatTool:
    """Create a Gemini chat tool."""
    config = GeminiConfig(api_key=api_key, model=model)
    return GeminiChatTool(config)

def create_gemini_function_calling_tool(api_key: str, model: str = "gemini-1.5-flash") -> GeminiFunctionCallingTool:
    """Create a Gemini function calling tool."""
    config = GeminiConfig(api_key=api_key, model=model)
    return GeminiFunctionCallingTool(config)

def create_gemini_code_generation_tool(api_key: str, model: str = "gemini-1.5-flash") -> GeminiCodeGenerationTool:
    """Create a Gemini code generation tool."""
    config = GeminiConfig(api_key=api_key, model=model)
    return GeminiCodeGenerationTool(config)

def create_gemini_data_analysis_tool(api_key: str, model: str = "gemini-1.5-flash") -> GeminiDataAnalysisTool:
    """Create a Gemini data analysis tool."""
    config = GeminiConfig(api_key=api_key, model=model)
    return GeminiDataAnalysisTool(config)

def create_gemini_text_processing_tool(api_key: str, model: str = "gemini-1.5-flash") -> GeminiTextProcessingTool:
    """Create a Gemini text processing tool."""
    config = GeminiConfig(api_key=api_key, model=model)
    return GeminiTextProcessingTool(config)

# Tool registry for Gemini tools
GEMINI_TOOLS = {
    "gemini_chat": create_gemini_chat_tool,
    "gemini_function_calling": create_gemini_function_calling_tool,
    "gemini_code_generation": create_gemini_code_generation_tool,
    "gemini_data_analysis": create_gemini_data_analysis_tool,
    "gemini_text_processing": create_gemini_text_processing_tool
}