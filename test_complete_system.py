#!/usr/bin/env python3
"""
Complete System Test Suite for OpenManus-Youtu Integrated Framework
Test all components and integrations
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Your API key
GEMINI_API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

class SystemTester:
    """Complete system tester."""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        log_message = f"{status} {test_name}{duration_str}"
        if message:
            log_message += f": {message}"
        
        print(log_message)
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_environment_setup(self) -> bool:
        """Test environment setup."""
        start_time = time.time()
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                self.log_test("Environment Setup", False, "Python 3.8+ required", time.time() - start_time)
                return False
            
            # Check required packages
            required_packages = ["fastapi", "uvicorn", "httpx", "pydantic", "asyncio"]
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    self.log_test("Environment Setup", False, f"{package} not installed", time.time() - start_time)
                    return False
            
            # Check API key
            if not GEMINI_API_KEY:
                self.log_test("Environment Setup", False, "GEMINI_API_KEY not configured", time.time() - start_time)
                return False
            
            self.log_test("Environment Setup", True, f"Python {python_version.major}.{python_version.minor}.{python_version.micro}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Environment Setup", False, str(e), time.time() - start_time)
            return False
    
    async def test_gemini_integration(self) -> bool:
        """Test Gemini 2.0 Flash integration."""
        start_time = time.time()
        
        try:
            # Import and test Gemini client
            from src.ai.gemini_client import GeminiClient, GeminiConfig, GeminiModel, GeminiMessage
            
            config = GeminiConfig(
                api_key=GEMINI_API_KEY,
                model=GeminiModel.GEMINI_2_0_FLASH.value,
                temperature=0.7,
                max_tokens=1024
            )
            
            client = GeminiClient(config)
            
            # Test initialization
            if not await client.initialize():
                self.log_test("Gemini Integration", False, "Failed to initialize client", time.time() - start_time)
                return False
            
            # Test basic message
            message = GeminiMessage(
                role="user",
                parts=[{"text": "Hello, please respond with 'Gemini 2.0 Flash is working!' in Vietnamese."}],
                timestamp=datetime.now()
            )
            
            response_chunks = []
            async for chunk in client.generate_content([message], stream=False):
                response_chunks.append(chunk)
            
            if not response_chunks:
                self.log_test("Gemini Integration", False, "No response received", time.time() - start_time)
                return False
            
            response = "".join(response_chunks)
            if len(response) < 10:
                self.log_test("Gemini Integration", False, "Response too short", time.time() - start_time)
                return False
            
            await client.close()
            self.log_test("Gemini Integration", True, f"Response: {response[:50]}...", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Gemini Integration", False, str(e), time.time() - start_time)
            return False
    
    async def test_unified_agent(self) -> bool:
        """Test Unified Gemini Agent."""
        start_time = time.time()
        
        try:
            # Import and test unified agent
            from src.ai.unified_gemini_agent import UnifiedGeminiAgent, GeminiAgentConfig
            
            config = GeminiAgentConfig(
                api_key=GEMINI_API_KEY,
                model="gemini-2.0-flash",
                temperature=0.7,
                max_tokens=1024
            )
            
            agent = UnifiedGeminiAgent(
                name="Test Agent",
                description="Test agent for system testing",
                gemini_config=config
            )
            
            # Test initialization
            if not await agent.initialize():
                self.log_test("Unified Agent", False, "Failed to initialize agent", time.time() - start_time)
                return False
            
            # Test capabilities
            capabilities = await agent.get_capabilities()
            if not capabilities:
                self.log_test("Unified Agent", False, "No capabilities returned", time.time() - start_time)
                return False
            
            # Test message processing
            response_chunks = []
            async for chunk in agent.process_message(
                "Xin chào! Bạn có thể giúp tôi gì?",
                "test_user",
                "test_session",
                stream=False
            ):
                response_chunks.append(chunk)
            
            if not response_chunks:
                self.log_test("Unified Agent", False, "No response from agent", time.time() - start_time)
                return False
            
            await agent.close()
            self.log_test("Unified Agent", True, f"Agent: {agent.name}, Tools: {len(capabilities.get('available_tools', []))}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Unified Agent", False, str(e), time.time() - start_time)
            return False
    
    async def test_agent_factory(self) -> bool:
        """Test Agent Factory."""
        start_time = time.time()
        
        try:
            # Import and test agent factory
            from src.agents.gemini_agent_factory import GeminiAgentFactory
            
            factory = GeminiAgentFactory()
            
            # Test CCCD agent creation
            cccd_agent = await factory.create_cccd_agent(
                api_key=GEMINI_API_KEY,
                model="gemini-2.0-flash",
                temperature=0.3
            )
            
            if not cccd_agent:
                self.log_test("Agent Factory", False, "Failed to create CCCD agent", time.time() - start_time)
                return False
            
            # Test general agent creation
            general_agent = await factory.create_general_purpose_agent(
                api_key=GEMINI_API_KEY,
                model="gemini-2.0-flash",
                temperature=0.7
            )
            
            if not general_agent:
                self.log_test("Agent Factory", False, "Failed to create general agent", time.time() - start_time)
                return False
            
            # Cleanup
            await cccd_agent.close()
            await general_agent.close()
            
            self.log_test("Agent Factory", True, f"Created: {cccd_agent.name}, {general_agent.name}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Agent Factory", False, str(e), time.time() - start_time)
            return False
    
    async def test_api_server(self) -> bool:
        """Test API server creation."""
        start_time = time.time()
        
        try:
            # Import and test API server
            from src.api.server import create_app
            
            app = create_app(
                title="Test App",
                description="Test application",
                version="1.0.0",
                debug=False
            )
            
            if not app:
                self.log_test("API Server", False, "Failed to create app", time.time() - start_time)
                return False
            
            # Check if routes are registered
            routes = [route.path for route in app.routes]
            if not routes:
                self.log_test("API Server", False, "No routes registered", time.time() - start_time)
                return False
            
            self.log_test("API Server", True, f"Routes: {len(routes)}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("API Server", False, str(e), time.time() - start_time)
            return False
    
    async def test_gemini_tools(self) -> bool:
        """Test Gemini tools."""
        start_time = time.time()
        
        try:
            # Import and test Gemini tools
            from src.tools.gemini_tools import (
                create_gemini_chat_tool,
                create_gemini_function_calling_tool,
                create_gemini_code_generation_tool
            )
            
            # Test tool creation
            chat_tool = create_gemini_chat_tool(GEMINI_API_KEY, "gemini-2.0-flash")
            function_tool = create_gemini_function_calling_tool(GEMINI_API_KEY, "gemini-2.0-flash")
            code_tool = create_gemini_code_generation_tool(GEMINI_API_KEY, "gemini-2.0-flash")
            
            if not all([chat_tool, function_tool, code_tool]):
                self.log_test("Gemini Tools", False, "Failed to create tools", time.time() - start_time)
                return False
            
            # Test tool initialization
            tools = [chat_tool, function_tool, code_tool]
            for tool in tools:
                if not await tool.initialize():
                    self.log_test("Gemini Tools", False, f"Failed to initialize {tool.name}", time.time() - start_time)
                    return False
            
            # Cleanup
            for tool in tools:
                await tool.cleanup()
            
            self.log_test("Gemini Tools", True, f"Tools: {len(tools)}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Gemini Tools", False, str(e), time.time() - start_time)
            return False
    
    async def test_cccd_workflow(self) -> bool:
        """Test CCCD workflow."""
        start_time = time.time()
        
        try:
            # Import and test CCCD workflow
            from src.agents.gemini_agent_factory import GeminiAgentFactory
            
            factory = GeminiAgentFactory()
            agent = await factory.create_cccd_agent(
                api_key=GEMINI_API_KEY,
                model="gemini-2.0-flash",
                temperature=0.3
            )
            
            # Test CCCD generation request
            response_chunks = []
            async for chunk in agent.process_message(
                "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975",
                "test_user",
                "test_session",
                stream=False
            ):
                response_chunks.append(chunk)
            
            if not response_chunks:
                self.log_test("CCCD Workflow", False, "No response from CCCD agent", time.time() - start_time)
                return False
            
            response = "".join(response_chunks)
            if "CCCD" not in response and "tạo" not in response.lower():
                self.log_test("CCCD Workflow", False, "Response doesn't contain CCCD context", time.time() - start_time)
                return False
            
            await agent.close()
            self.log_test("CCCD Workflow", True, f"Response: {response[:50]}...", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("CCCD Workflow", False, str(e), time.time() - start_time)
            return False
    
    async def test_performance(self) -> bool:
        """Test system performance."""
        start_time = time.time()
        
        try:
            # Import and test performance
            from src.agents.gemini_agent_factory import GeminiAgentFactory
            
            factory = GeminiAgentFactory()
            agent = await factory.create_general_purpose_agent(
                api_key=GEMINI_API_KEY,
                model="gemini-2.0-flash",
                temperature=0.7
            )
            
            # Test multiple requests
            async def single_request(request_id: int):
                req_start = time.time()
                response_chunks = []
                async for chunk in agent.process_message(
                    f"Request {request_id}: Hãy trả lời ngắn gọn về AI",
                    "test_user",
                    "test_session",
                    stream=False
                ):
                    response_chunks.append(chunk)
                req_end = time.time()
                return request_id, req_end - req_start, len("".join(response_chunks))
            
            # Run 3 concurrent requests
            tasks = [single_request(i) for i in range(1, 4)]
            results = await asyncio.gather(*tasks)
            
            total_time = sum(result[1] for result in results)
            avg_time = total_time / len(results)
            total_chars = sum(result[2] for result in results)
            
            if avg_time > 5.0:  # More than 5 seconds average
                self.log_test("Performance", False, f"Average response time too slow: {avg_time:.2f}s", time.time() - start_time)
                return False
            
            await agent.close()
            self.log_test("Performance", True, f"Avg: {avg_time:.2f}s, Total chars: {total_chars}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Performance", False, str(e), time.time() - start_time)
            return False
    
    async def test_vietnamese_support(self) -> bool:
        """Test Vietnamese language support."""
        start_time = time.time()
        
        try:
            # Import and test Vietnamese support
            from src.agents.gemini_agent_factory import GeminiAgentFactory
            
            factory = GeminiAgentFactory()
            agent = await factory.create_general_purpose_agent(
                api_key=GEMINI_API_KEY,
                model="gemini-2.0-flash",
                temperature=0.7
            )
            
            # Test Vietnamese conversation
            vietnamese_requests = [
                "Xin chào! Bạn có thể giúp tôi gì?",
                "Tôi cần tạo 100 CCCD cho tỉnh Hưng Yên",
                "Hãy giải thích cách AI hoạt động bằng tiếng Việt"
            ]
            
            for i, request in enumerate(vietnamese_requests):
                response_chunks = []
                async for chunk in agent.process_message(
                    request,
                    "test_user",
                    "test_session",
                    stream=False
                ):
                    response_chunks.append(chunk)
                
                if not response_chunks:
                    self.log_test("Vietnamese Support", False, f"No response for request {i+1}", time.time() - start_time)
                    return False
                
                response = "".join(response_chunks)
                if len(response) < 10:
                    self.log_test("Vietnamese Support", False, f"Response too short for request {i+1}", time.time() - start_time)
                    return False
            
            await agent.close()
            self.log_test("Vietnamese Support", True, f"Tested {len(vietnamese_requests)} Vietnamese requests", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Vietnamese Support", False, str(e), time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        print("🧪 Starting Complete System Tests")
        print("=" * 60)
        
        test_methods = [
            ("Environment Setup", self.test_environment_setup),
            ("Gemini Integration", self.test_gemini_integration),
            ("Unified Agent", self.test_unified_agent),
            ("Agent Factory", self.test_agent_factory),
            ("API Server", self.test_api_server),
            ("Gemini Tools", self.test_gemini_tools),
            ("CCCD Workflow", self.test_cccd_workflow),
            ("Performance", self.test_performance),
            ("Vietnamese Support", self.test_vietnamese_support)
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            try:
                success = await test_method()
                if success:
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        total_time = time.time() - self.start_time
        
        # Generate report
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "total_time": total_time,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        return report

async def main():
    """Main test function."""
    print("🚀 OpenManus-Youtu Integrated Framework - Complete System Tests")
    print("=" * 70)
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...")
    print(f"🤖 Model: Gemini 2.0 Flash")
    print("=" * 70)
    
    tester = SystemTester()
    
    try:
        report = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎉 Complete System Tests Completed!")
        
        summary = report["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Time: {summary['total_time']:.2f}s")
        
        if summary['success_rate'] == 100:
            print("\n🎉 All tests passed! System is fully functional!")
        elif summary['success_rate'] >= 80:
            print("\n✅ Most tests passed! System is mostly functional!")
        else:
            print("\n⚠️  Some tests failed. Please check the issues above.")
        
        # Save report
        report_file = Path(__file__).parent / "test_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📊 Test report saved to: {report_file}")
        
        return summary['success_rate'] == 100
        
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)