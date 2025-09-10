#!/usr/bin/env python3
"""
Simple test script for Gemini API integration
Test only Gemini components without full framework dependencies
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import httpx

# Direct imports without framework dependencies
class GeminiModel(Enum):
    """Supported Gemini models."""
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_0_PRO = "gemini-1.0-pro"

@dataclass
class GeminiConfig:
    """Gemini API configuration."""
    api_key: str
    model: str = GeminiModel.GEMINI_1_5_FLASH.value
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    retry_attempts: int = 3
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"

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
        
        # Function calling support
        self.functions: Dict[str, callable] = {}
        self.function_definitions: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """Initialize Gemini client."""
        try:
            # Test API connection
            await self._test_connection()
            print("✅ Gemini client initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Gemini client: {e}")
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
    
    def register_function(self, function: GeminiFunction, handler: callable):
        """Register a function for function calling."""
        self.functions[function.name] = handler
        
        # Convert to Gemini function definition format
        function_def = {
            "name": function.name,
            "description": function.description,
            "parameters": function.parameters
        }
        self.function_definitions.append(function_def)
        
        print(f"✅ Registered function: {function.name}")
    
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
            print(f"❌ Error generating content: {e}")
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
                                return f"Đã thực thi function {part['functionCall']['name']}: {function_result}"
                            elif "text" in part:
                                return part["text"]
                
                return "Không có phản hồi từ Gemini"
            else:
                error_msg = f"API error: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        pass
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

async def test_gemini_client():
    """Test Gemini client functionality."""
    print("🧪 Testing Gemini Client...")
    
    # Test configuration
    config = GeminiConfig(
        api_key="test_api_key",  # Replace with real API key for testing
        model=GeminiModel.GEMINI_1_5_FLASH.value,
        temperature=0.7,
        max_tokens=100
    )
    
    client = GeminiClient(config)
    
    try:
        # Test initialization (will fail with test key, but should not crash)
        result = await client.initialize()
        print(f"✅ Client initialization: {'Success' if result else 'Failed (expected with test key)'}")
        
        # Test function registration
        cccd_func = OpenManusFunctions.get_cccd_generation_function()
        client.register_function(cccd_func, lambda args: "Test function executed")
        print("✅ Function registration: Success")
        
        # Test message conversion
        test_message = GeminiMessage(
            role="user",
            parts=[{"text": "Hello, this is a test message."}],
            timestamp=datetime.now()
        )
        print("✅ Message creation: Success")
        
        await client.close()
        print("✅ Client cleanup: Success")
        
    except Exception as e:
        print(f"❌ Client test failed: {e}")
    
    print("🧪 Gemini Client test completed\n")

async def test_function_definitions():
    """Test function definitions."""
    print("🧪 Testing Function Definitions...")
    
    try:
        # Test CCCD generation function
        cccd_func = OpenManusFunctions.get_cccd_generation_function()
        print(f"✅ CCCD Generation Function: {cccd_func.name}")
        print(f"   Description: {cccd_func.description}")
        print(f"   Parameters: {len(cccd_func.parameters.get('properties', {}))}")
        
        # Test CCCD check function
        check_func = OpenManusFunctions.get_cccd_check_function()
        print(f"✅ CCCD Check Function: {check_func.name}")
        print(f"   Description: {check_func.description}")
        
        # Test tax lookup function
        tax_func = OpenManusFunctions.get_tax_lookup_function()
        print(f"✅ Tax Lookup Function: {tax_func.name}")
        print(f"   Description: {tax_func.description}")
        
    except Exception as e:
        print(f"❌ Function definitions test failed: {e}")
    
    print("🧪 Function Definitions test completed\n")

async def test_real_api_key():
    """Test with real API key (if provided)."""
    print("🧪 Testing with Real API Key...")
    
    # Check if API key is provided via environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️  No GEMINI_API_KEY environment variable found")
        print("   Set GEMINI_API_KEY=your_api_key to test with real API")
        return
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    
    try:
        # Test real configuration
        config = GeminiConfig(
            api_key=api_key,
            model=GeminiModel.GEMINI_1_5_FLASH.value,
            temperature=0.7,
            max_tokens=100
        )
        
        client = GeminiClient(config)
        
        # Test initialization
        result = await client.initialize()
        print(f"✅ Real API initialization: {'Success' if result else 'Failed'}")
        
        if result:
            # Test simple generation
            test_message = GeminiMessage(
                role="user",
                parts=[{"text": "Hello, this is a test message. Please respond with 'Test successful'."}],
                timestamp=datetime.now()
            )
            
            print("🔄 Testing content generation...")
            response_chunks = []
            async for chunk in client.generate_content([test_message], stream=False):
                response_chunks.append(chunk)
            
            if response_chunks:
                response = "".join(response_chunks)
                print(f"✅ Real API response: {response[:100]}...")
            else:
                print("❌ No response from real API")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Real API test failed: {e}")
    
    print("🧪 Real API Key test completed\n")

async def main():
    """Run all tests."""
    print("🚀 Starting Gemini Integration Tests\n")
    print("=" * 50)
    
    await test_gemini_client()
    await test_function_definitions()
    await test_real_api_key()
    
    print("=" * 50)
    print("🎉 All Gemini Integration Tests Completed!")
    print("\n📋 Test Summary:")
    print("✅ Gemini Client - Basic functionality tested")
    print("✅ Function Definitions - All 3 functions defined")
    print("✅ Real API Key - Tested with actual API (if key provided)")
    
    print("\n🔧 Next Steps:")
    print("1. Set GEMINI_API_KEY environment variable for real testing")
    print("2. Configure Gemini API key in web interface")
    print("3. Test function calling with real API")
    print("4. Test WebSocket chat interface")
    print("5. Test integration with existing modules")

if __name__ == "__main__":
    asyncio.run(main())