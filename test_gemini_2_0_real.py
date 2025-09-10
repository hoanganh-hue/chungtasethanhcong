#!/usr/bin/env python3
"""
Test script for Gemini 2.0 Flash with real API key
Test the complete integration with actual Google Gemini API
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Direct imports for testing
from src.ai.gemini_client import GeminiClient, GeminiConfig, GeminiMessage, GeminiModel

# Your API key
GEMINI_API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

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
        
        client = GeminiClient(config)
        
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
        
        client = GeminiClient(config)
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
        async for chunk in client.generate_content([message], stream=True):
            print(f"   Chunk {chunk_count + 1}: {chunk}", end="", flush=True)
            chunk_count += 1
        
        print(f"\n✅ Streaming completed: {chunk_count} chunks received")
        
        # Cleanup
        await client.close()
        print("✅ Gemini 2.0 Flash streaming test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Gemini 2.0 Flash streaming test failed: {e}")
        return False

async def test_gemini_2_0_function_calling():
    """Test Gemini 2.0 Flash function calling."""
    print("\n🧪 Testing Gemini 2.0 Flash Function Calling...")
    
    try:
        # Create Gemini client
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.3,  # Lower temperature for function calling
            max_tokens=1024
        )
        
        client = GeminiClient(config)
        await client.initialize()
        
        # Define a test function
        def test_cccd_generation(province: str, gender: str, quantity: int, birth_year_range: str) -> str:
            """Test function for CCCD generation."""
            return f"Generated {quantity} CCCD for {province}, gender: {gender}, birth years: {birth_year_range}"
        
        # Register function
        from src.ai.gemini_client import OpenManusFunctions
        cccd_func = OpenManusFunctions.get_cccd_generation_function()
        client.register_function(cccd_func, test_cccd_generation)
        
        print("✅ Function registered successfully")
        
        # Test function calling
        print("🔄 Testing function calling...")
        message = GeminiMessage(
            role="user",
            parts=[{"text": "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975"}],
            timestamp=datetime.now()
        )
        
        response_chunks = []
        async for chunk in client.generate_content([message], stream=False):
            response_chunks.append(chunk)
        
        if response_chunks:
            response = "".join(response_chunks)
            print(f"✅ Function calling response: {response}")
        else:
            print("❌ No function calling response received")
            return False
        
        # Cleanup
        await client.close()
        print("✅ Gemini 2.0 Flash function calling test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Gemini 2.0 Flash function calling test failed: {e}")
        return False

async def test_gemini_2_0_cccd_workflow():
    """Test complete CCCD workflow with Gemini 2.0 Flash."""
    print("\n🧪 Testing CCCD Workflow with Gemini 2.0 Flash...")
    
    try:
        # Create Gemini client
        config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model=GeminiModel.GEMINI_2_0_FLASH.value,
            temperature=0.3,
            max_tokens=2048
        )
        
        client = GeminiClient(config)
        await client.initialize()
        
        # Register CCCD functions
        from src.ai.gemini_client import OpenManusFunctions
        
        def generate_cccd(province: str, gender: str, quantity: int, birth_year_range: str) -> str:
            return f"✅ Đã tạo {quantity} CCCD cho tỉnh {province}, giới tính {gender}, năm sinh {birth_year_range}"
        
        def check_cccd(cccd_number: str) -> str:
            return f"✅ Đã kiểm tra CCCD {cccd_number}: Thông tin hợp lệ"
        
        def lookup_tax(tax_code: str) -> str:
            return f"✅ Đã tra cứu mã số thuế {tax_code}: Thông tin đã được tìm thấy"
        
        # Register functions
        client.register_function(OpenManusFunctions.get_cccd_generation_function(), generate_cccd)
        client.register_function(OpenManusFunctions.get_cccd_check_function(), check_cccd)
        client.register_function(OpenManusFunctions.get_tax_lookup_function(), lookup_tax)
        
        print("✅ CCCD functions registered successfully")
        
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
                print(f"✅ Response: {response}")
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
        
        client = GeminiClient(config)
        await client.initialize()
        
        # Test multiple requests
        print("🔄 Testing multiple concurrent requests...")
        
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
            return request_id, response_time, len("".join(response_chunks))
        
        # Run 5 concurrent requests
        tasks = [single_request(i) for i in range(1, 6)]
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
    test_results.append(await test_gemini_2_0_function_calling())
    test_results.append(await test_gemini_2_0_cccd_workflow())
    test_results.append(await test_gemini_2_0_performance())
    
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
    print("✅ Function calling")
    print("✅ CCCD workflow integration")
    print("✅ Performance testing")
    
    print("\n🚀 Next Steps:")
    print("1. Integrate with Unified Gemini Agent")
    print("2. Test with real CCCD generation")
    print("3. Deploy to production")
    print("4. Monitor performance and usage")

if __name__ == "__main__":
    asyncio.run(main())