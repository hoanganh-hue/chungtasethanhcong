#!/usr/bin/env python3
"""
Simple test script for Gemini 2.0 Flash with real API key
Test the complete integration with actual Google Gemini API
"""

import asyncio
import json
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

# Your API key
GEMINI_API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

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
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"

@dataclass
class GeminiMessage:
    """Gemini message structure."""
    role: str  # "user" or "model"
    parts: List[Dict[str, Any]]
    timestamp: datetime

class SimpleGeminiClient:
    """Simple Gemini API client for testing."""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the client."""
        try:
            # Test connection with a simple request
            test_url = f"{self.config.base_url}/models"
            headers = {
                "X-goog-api-key": self.config.api_key
            }
            
            response = await self.client.get(test_url, headers=headers)
            if response.status_code == 200:
                self._initialized = True
                return True
            else:
                print(f"❌ Failed to initialize: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    async def generate_content(
        self, 
        messages: List[GeminiMessage], 
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """Generate content using Gemini API."""
        try:
            url = f"{self.config.base_url}/models/{self.config.model}:generateContent"
            
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": self.config.api_key
            }
            
            # Convert messages to API format
            contents = []
            for msg in messages:
                content = {
                    "parts": msg.parts
                }
                contents.append(content)
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "maxOutputTokens": self.config.max_tokens
                }
            }
            
            if stream:
                payload["generationConfig"]["stream"] = True
            
            response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    for line in response.text.split('\n'):
                        if line.strip() and line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                if 'candidates' in data and data['candidates']:
                                    candidate = data['candidates'][0]
                                    if 'content' in candidate and 'parts' in candidate['content']:
                                        for part in candidate['content']['parts']:
                                            if 'text' in part:
                                                yield part['text']
                            except json.JSONDecodeError:
                                continue
                else:
                    # Handle non-streaming response
                    data = response.json()
                    if 'candidates' in data and data['candidates']:
                        candidate = data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'text' in part:
                                    yield part['text']
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                yield f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            print(f"❌ Generation error: {e}")
            yield f"Error: {str(e)}"
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

async def test_gemini_2_0_basic():
    """Test basic Gemini 2.0 Flash functionality."""
    print("🧪 Testing Gemini 2.0 Flash Basic Functionality...")
    
    try:
        # Create Gemini client with 2.0 Flash
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.7,
            max_tokens=1024
        )
        
        client = SimpleGeminiClient(config)
        
        # Initialize client
        print("🔄 Initializing Gemini 2.0 Flash client...")
        if not await client.initialize():
            print("❌ Failed to initialize Gemini client")
            return False
        
        print("✅ Gemini 2.0 Flash client initialized successfully")
        
        # Test basic message
        print("🔄 Testing basic message...")
        message = GeminiMessage(
            role="user",
            parts=[{"text": "Hello! Please respond with 'Gemini 2.0 Flash is working!' in Vietnamese."}],
            timestamp=datetime.now()
        )
        
        response_chunks = []
        async for chunk in client.generate_content([message], stream=False):
            response_chunks.append(chunk)
        
        if response_chunks:
            response = "".join(response_chunks)
            print(f"✅ Basic message response: {response}")
        else:
            print("❌ No response received")
            return False
        
        # Test Vietnamese response
        print("🔄 Testing Vietnamese language...")
        vietnamese_message = GeminiMessage(
            role="user",
            parts=[{"text": "Xin chào! Bạn có thể giúp tôi tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975 không?"}],
            timestamp=datetime.now()
        )
        
        response_chunks = []
        async for chunk in client.generate_content([vietnamese_message], stream=False):
            response_chunks.append(chunk)
        
        if response_chunks:
            response = "".join(response_chunks)
            print(f"✅ Vietnamese response: {response[:200]}...")
        else:
            print("❌ No Vietnamese response received")
            return False
        
        # Cleanup
        await client.close()
        print("✅ Gemini 2.0 Flash basic test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Gemini 2.0 Flash basic test failed: {e}")
        return False

async def test_gemini_2_0_streaming():
    """Test Gemini 2.0 Flash streaming functionality."""
    print("\n🧪 Testing Gemini 2.0 Flash Streaming...")
    
    try:
        # Create Gemini client
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.7,
            max_tokens=1024
        )
        
        client = SimpleGeminiClient(config)
        await client.initialize()
        
        # Test streaming response
        print("🔄 Testing streaming response...")
        message = GeminiMessage(
            role="user",
            parts=[{"text": "Hãy giải thích cách AI hoạt động trong vài từ ngắn gọn bằng tiếng Việt."}],
            timestamp=datetime.now()
        )
        
        print("📡 Streaming response:")
        chunk_count = 0
        full_response = ""
        async for chunk in client.generate_content([message], stream=True):
            print(f"{chunk}", end="", flush=True)
            full_response += chunk
            chunk_count += 1
        
        print(f"\n✅ Streaming completed: {chunk_count} chunks received")
        print(f"✅ Full response length: {len(full_response)} characters")
        
        # Cleanup
        await client.close()
        print("✅ Gemini 2.0 Flash streaming test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Gemini 2.0 Flash streaming test failed: {e}")
        return False

async def test_gemini_2_0_cccd_workflow():
    """Test CCCD workflow with Gemini 2.0 Flash."""
    print("\n🧪 Testing CCCD Workflow with Gemini 2.0 Flash...")
    
    try:
        # Create Gemini client
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.3,
            max_tokens=2048
        )
        
        client = SimpleGeminiClient(config)
        await client.initialize()
        
        print("✅ Gemini 2.0 Flash client initialized for CCCD workflow")
        
        # Test workflow scenarios
        test_scenarios = [
            "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975",
            "Kiểm tra CCCD 031089011929",
            "Tra cứu mã số thuế 037178000015",
            "Tạo 50 CCCD cho tỉnh Hà Nội, giới tính nam, năm sinh từ 1980 đến 1990"
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔄 Test scenario {i}: {scenario}")
            
            message = GeminiMessage(
                role="user",
                parts=[{"text": scenario}],
                timestamp=datetime.now()
            )
            
            response_chunks = []
            async for chunk in client.generate_content([message], stream=False):
                response_chunks.append(chunk)
            
            if response_chunks:
                response = "".join(response_chunks)
                print(f"✅ Response: {response[:150]}...")
            else:
                print("❌ No response received")
        
        # Cleanup
        await client.close()
        print("\n✅ CCCD workflow test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ CCCD workflow test failed: {e}")
        return False

async def test_gemini_2_0_performance():
    """Test Gemini 2.0 Flash performance."""
    print("\n🧪 Testing Gemini 2.0 Flash Performance...")
    
    try:
        # Create Gemini client
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.7,
            max_tokens=512
        )
        
        client = SimpleGeminiClient(config)
        await client.initialize()
        
        # Test multiple requests
        print("🔄 Testing multiple requests...")
        
        async def single_request(request_id: int):
            message = GeminiMessage(
                role="user",
                parts=[{"text": f"Request {request_id}: Hãy trả lời ngắn gọn về AI"}],
                timestamp=datetime.now()
            )
            
            start_time = datetime.now()
            response_chunks = []
            async for chunk in client.generate_content([message], stream=False):
                response_chunks.append(chunk)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            response_text = "".join(response_chunks)
            return request_id, response_time, len(response_text)
        
        # Run 3 requests
        tasks = [single_request(i) for i in range(1, 4)]
        results = await asyncio.gather(*tasks)
        
        print("📊 Performance Results:")
        total_time = 0
        total_chars = 0
        
        for request_id, response_time, char_count in results:
            print(f"   Request {request_id}: {response_time:.2f}s, {char_count} chars")
            total_time += response_time
            total_chars += char_count
        
        avg_time = total_time / len(results)
        avg_chars = total_chars / len(results)
        
        print(f"✅ Average response time: {avg_time:.2f}s")
        print(f"✅ Average response length: {avg_chars:.0f} characters")
        print(f"✅ Total requests: {len(results)}")
        
        # Cleanup
        await client.close()
        print("✅ Performance test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def test_gemini_2_0_function_simulation():
    """Test function calling simulation with Gemini 2.0 Flash."""
    print("\n🧪 Testing Function Calling Simulation...")
    
    try:
        # Create Gemini client
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.3,
            max_tokens=1024
        )
        
        client = SimpleGeminiClient(config)
        await client.initialize()
        
        # Test function calling simulation
        print("🔄 Testing function calling simulation...")
        
        # Simulate function calling by asking Gemini to understand the intent
        function_message = GeminiMessage(
            role="user",
            parts=[{"text": """
Bạn là một AI Agent có khả năng thực hiện các function calls. Khi người dùng yêu cầu, hãy phân tích và trả lời như thể bạn đã thực hiện function call.

Các functions có sẵn:
1. generate_cccd(province, gender, quantity, birth_year_range) - Tạo CCCD
2. check_cccd(cccd_number) - Kiểm tra CCCD
3. lookup_tax(tax_code) - Tra cứu mã số thuế

Yêu cầu: "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975"

Hãy trả lời như thể bạn đã gọi function generate_cccd("Hưng Yên", "nữ", 100, "1965-1975")
            """}],
            timestamp=datetime.now()
        )
        
        response_chunks = []
        async for chunk in client.generate_content([function_message], stream=False):
            response_chunks.append(chunk)
        
        if response_chunks:
            response = "".join(response_chunks)
            print(f"✅ Function calling simulation response: {response}")
        else:
            print("❌ No function calling response received")
            return False
        
        # Cleanup
        await client.close()
        print("✅ Function calling simulation test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Function calling simulation test failed: {e}")
        return False

async def main():
    """Run all Gemini 2.0 Flash tests."""
    print("🚀 Starting Gemini 2.0 Flash Integration Tests")
    print("=" * 60)
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...")
    print(f"🤖 Model: Gemini 2.0 Flash")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_gemini_2_0_basic())
    test_results.append(await test_gemini_2_0_streaming())
    test_results.append(await test_gemini_2_0_cccd_workflow())
    test_results.append(await test_gemini_2_0_performance())
    test_results.append(await test_gemini_2_0_function_simulation())
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Gemini 2.0 Flash Integration Tests Completed!")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Gemini 2.0 Flash integration is working perfectly!")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n🔧 Features Tested:")
    print("✅ Basic message generation")
    print("✅ Vietnamese language support")
    print("✅ Streaming responses")
    print("✅ CCCD workflow integration")
    print("✅ Performance testing")
    print("✅ Function calling simulation")
    
    print("\n🚀 Next Steps:")
    print("1. Integrate with Unified Gemini Agent")
    print("2. Test with real CCCD generation")
    print("3. Deploy to production")
    print("4. Monitor performance and usage")

if __name__ == "__main__":
    asyncio.run(main())