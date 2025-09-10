"""
Google Gemini API Client for OpenManus-Youtu Integrated Framework
Advanced integration with function calling and streaming support
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from enum import Enum

logger = logging.getLogger(__name__)

class GeminiModel(Enum):
    """Supported Gemini models."""
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_0_PRO = "gemini-1.0-pro"

@dataclass
class GeminiConfig:
    """Gemini API configuration."""
    api_key: str
    model: str = GeminiModel.GEMINI_2_0_FLASH.value
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    retry_attempts: int = 3
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    enable_function_calling: bool = True
    enable_streaming: bool = True

@dataclass
class GeminiMessage:
    """Gemini message structure."""
    role: str  # "user" or "model"
    parts: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class GeminiFunction:
    """Gemini function definition."""
    name: str
    description: str
    parameters: Dict[str, Any]

class GeminiClient:
    """Google Gemini API client with advanced features."""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": config.api_key
            }
        )
        self.logger = logging.getLogger(f"{__name__}.GeminiClient")
        
        # Function calling support
        self.functions: Dict[str, Callable] = {}
        self.function_definitions: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """Initialize Gemini client."""
        try:
            # Test API connection
            await self._test_connection()
            self.logger.info("Gemini client initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            return False
    
    async def _test_connection(self):
        """Test API connection."""
        try:
            response = await self.client.get(
                f"{self.config.base_url}/models/{self.config.model}"
            )
            if response.status_code != 200:
                raise Exception(f"API test failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"Connection test failed: {e}")
    
    def register_function(self, function: GeminiFunction, handler: Callable):
        """Register a function for function calling."""
        self.functions[function.name] = handler
        
        # Convert to Gemini function definition format
        function_def = {
            "name": function.name,
            "description": function.description,
            "parameters": function.parameters
        }
        self.function_definitions.append(function_def)
        
        self.logger.info(f"Registered function: {function.name}")
    
    async def generate_content(
        self, 
        messages: List[GeminiMessage],
        stream: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate content using Gemini API."""
        try:
            # Prepare request payload
            payload = self._prepare_request_payload(messages, stream, **kwargs)
            
            if stream:
                async for chunk in self._stream_generate_content(payload):
                    yield chunk
            else:
                response = await self._generate_content(payload)
                yield response
                
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            yield f"Lỗi khi tạo nội dung: {str(e)}"
    
    def _prepare_request_payload(
        self, 
        messages: List[GeminiMessage], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare request payload for Gemini API."""
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            content = {
                "role": msg.role,
                "parts": msg.parts
            }
            contents.append(content)
        
        # Prepare generation config
        generation_config = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
            "topP": kwargs.get("top_p", 0.95),
            "topK": kwargs.get("top_k", 40)
        }
        
        # Prepare tools if functions are registered
        tools = []
        if self.function_definitions:
            tools.append({
                "functionDeclarations": self.function_definitions
            })
        
        payload = {
            "contents": contents,
            "generationConfig": generation_config
        }
        
        if tools:
            payload["tools"] = tools
        
        return payload
    
    async def _generate_content(self, payload: Dict[str, Any]) -> str:
        """Generate content (non-streaming)."""
        try:
            response = await self.client.post(
                f"{self.config.base_url}/models/{self.config.model}:generateContent",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for function calls
                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        
                        # Check for function calls
                        for part in parts:
                            if "functionCall" in part:
                                # Execute function call
                                function_result = await self._execute_function_call(part["functionCall"])
                                
                                # Generate follow-up response
                                follow_up_messages = [
                                    GeminiMessage(
                                        role="user",
                                        parts=[{"text": f"Function {part['functionCall']['name']} executed with result: {function_result}"}],
                                        timestamp=datetime.now()
                                    )
                                ]
                                
                                follow_up_payload = self._prepare_request_payload(follow_up_messages)
                                follow_up_response = await self.client.post(
                                    f"{self.config.base_url}/models/{self.config.model}:generateContent",
                                    json=follow_up_payload
                                )
                                
                                if follow_up_response.status_code == 200:
                                    follow_up_result = follow_up_response.json()
                                    if "candidates" in follow_up_result and follow_up_result["candidates"]:
                                        return follow_up_result["candidates"][0]["content"]["parts"][0]["text"]
                                
                                return f"Đã thực thi function {part['functionCall']['name']}: {function_result}"
                            elif "text" in part:
                                return part["text"]
                
                return "Không có phản hồi từ Gemini"
            else:
                error_msg = f"API error: {response.status_code}"
                if response.text:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                raise Exception(error_msg)
                
        except Exception as e:
            raise Exception(f"Content generation failed: {e}")
    
    async def _stream_generate_content(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream generate content."""
        try:
            # Add streaming parameter
            payload["stream"] = True
            
            async with self.client.stream(
                "POST",
                f"{self.config.base_url}/models/{self.config.model}:streamGenerateContent",
                json=payload
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "candidates" in chunk and chunk["candidates"]:
                                    candidate = chunk["candidates"][0]
                                    if "content" in candidate and "parts" in candidate["content"]:
                                        parts = candidate["content"]["parts"]
                                        for part in parts:
                                            if "text" in part:
                                                yield part["text"]
                            except json.JSONDecodeError:
                                continue
                else:
                    raise Exception(f"Streaming error: {response.status_code}")
                    
        except Exception as e:
            raise Exception(f"Streaming failed: {e}")
    
    async def _execute_function_call(self, function_call: Dict[str, Any]) -> str:
        """Execute function call."""
        try:
            function_name = function_call["name"]
            function_args = function_call.get("args", {})
            
            if function_name in self.functions:
                handler = self.functions[function_name]
                result = await handler(function_args)
                return str(result)
            else:
                return f"Function {function_name} not found"
                
        except Exception as e:
            return f"Error executing function: {str(e)}"
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

# Predefined functions for OpenManus-Youtu framework
class OpenManusFunctions:
    """Predefined functions for OpenManus-Youtu framework."""
    
    @staticmethod
    def get_cccd_generation_function() -> GeminiFunction:
        """Get CCCD generation function definition."""
        return GeminiFunction(
            name="generate_cccd",
            description="Tạo CCCD theo tỉnh, giới tính, năm sinh và số lượng",
            parameters={
                "type": "object",
                "properties": {
                    "province": {
                        "type": "string",
                        "description": "Tỉnh thành (ví dụ: Hưng Yên, Hà Nội, TP. Hồ Chí Minh)"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["nam", "nữ"],
                        "description": "Giới tính"
                    },
                    "birth_year_range": {
                        "type": "string",
                        "description": "Khoảng năm sinh (ví dụ: 1965-1975)"
                    },
                    "quantity": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "description": "Số lượng CCCD cần tạo"
                    }
                },
                "required": ["province", "gender", "quantity"]
            }
        )
    
    @staticmethod
    def get_cccd_check_function() -> GeminiFunction:
        """Get CCCD check function definition."""
        return GeminiFunction(
            name="check_cccd",
            description="Kiểm tra thông tin CCCD",
            parameters={
                "type": "object",
                "properties": {
                    "cccd_number": {
                        "type": "string",
                        "description": "Số CCCD cần kiểm tra"
                    }
                },
                "required": ["cccd_number"]
            }
        )
    
    @staticmethod
    def get_tax_lookup_function() -> GeminiFunction:
        """Get tax lookup function definition."""
        return GeminiFunction(
            name="lookup_tax",
            description="Tra cứu mã số thuế",
            parameters={
                "type": "object",
                "properties": {
                    "tax_code": {
                        "type": "string",
                        "description": "Mã số thuế cần tra cứu"
                    }
                },
                "required": ["tax_code"]
            }
        )
    
    @staticmethod
    def get_data_analysis_function() -> GeminiFunction:
        """Get data analysis function definition."""
        return GeminiFunction(
            name="analyze_data",
            description="Phân tích dữ liệu",
            parameters={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "description": "Loại phân tích (ví dụ: statistical, trend, correlation)"
                    },
                    "input_data": {
                        "type": "string",
                        "description": "Dữ liệu đầu vào hoặc đường dẫn file"
                    }
                },
                "required": ["analysis_type", "input_data"]
            }
        )
    
    @staticmethod
    def get_web_scraping_function() -> GeminiFunction:
        """Get web scraping function definition."""
        return GeminiFunction(
            name="scrape_web",
            description="Thu thập dữ liệu từ website",
            parameters={
                "type": "object",
                "properties": {
                    "target_url": {
                        "type": "string",
                        "description": "URL cần scraping"
                    },
                    "scraping_config": {
                        "type": "object",
                        "description": "Cấu hình scraping (selectors, pagination, etc.)"
                    }
                },
                "required": ["target_url"]
            }
        )
    
    @staticmethod
    def get_form_automation_function() -> GeminiFunction:
        """Get form automation function definition."""
        return GeminiFunction(
            name="automate_form",
            description="Tự động điền và submit form",
            parameters={
                "type": "object",
                "properties": {
                    "form_url": {
                        "type": "string",
                        "description": "URL của form"
                    },
                    "form_data": {
                        "type": "object",
                        "description": "Dữ liệu cần điền vào form"
                    }
                },
                "required": ["form_url", "form_data"]
            }
        )
    
    @staticmethod
    def get_report_generation_function() -> GeminiFunction:
        """Get report generation function definition."""
        return GeminiFunction(
            name="generate_report",
            description="Tạo báo cáo từ dữ liệu",
            parameters={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "description": "Loại báo cáo (ví dụ: summary, detailed, chart)"
                    },
                    "report_data": {
                        "type": "object",
                        "description": "Dữ liệu để tạo báo cáo"
                    }
                },
                "required": ["report_type", "report_data"]
            }
        )
    
    @staticmethod
    def get_excel_export_function() -> GeminiFunction:
        """Get Excel export function definition."""
        return GeminiFunction(
            name="export_excel",
            description="Xuất dữ liệu ra file Excel",
            parameters={
                "type": "object",
                "properties": {
                    "export_data": {
                        "type": "object",
                        "description": "Dữ liệu cần xuất"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Tên file Excel"
                    }
                },
                "required": ["export_data"]
            }
        )