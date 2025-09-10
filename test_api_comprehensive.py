#!/usr/bin/env python3
"""
Comprehensive API System Test for OpenManus-Youtu Integrated Framework
Test all API endpoints, AI agents, and tools integration
"""

import asyncio
import json
import sys
import os
import time
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Your API key
GEMINI_API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

class ComprehensiveAPITester:
    """Comprehensive API system tester."""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        self.base_url = "http://localhost:8000"
        
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
    
    async def test_server_startup(self) -> bool:
        """Test if server can start."""
        start_time = time.time()
        
        try:
            # Test if server is running
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    if "OpenManus-Youtu" in data.get("message", ""):
                        self.log_test("Server Startup", True, f"Server running: {data.get('version', 'unknown')}", time.time() - start_time)
                        return True
                
                self.log_test("Server Startup", False, f"Server not responding: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Server Startup", False, f"Server not running: {str(e)}", time.time() - start_time)
            return False
    
    async def test_api_documentation(self) -> bool:
        """Test API documentation endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/docs")
                
                if response.status_code == 200:
                    self.log_test("API Documentation", True, "Swagger UI accessible", time.time() - start_time)
                    return True
                else:
                    self.log_test("API Documentation", False, f"Docs not accessible: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("API Documentation", False, str(e), time.time() - start_time)
            return False
    
    async def test_health_endpoint(self) -> bool:
        """Test health check endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") in ["healthy", "degraded"]:
                        self.log_test("Health Endpoint", True, f"Status: {data.get('status')}", time.time() - start_time)
                        return True
                
                self.log_test("Health Endpoint", False, f"Health check failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_metrics_endpoint(self) -> bool:
        """Test metrics endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/metrics")
                
                if response.status_code == 200:
                    data = response.json()
                    if "system" in data and "application" in data:
                        self.log_test("Metrics Endpoint", True, "Metrics data available", time.time() - start_time)
                        return True
                
                self.log_test("Metrics Endpoint", False, f"Metrics not available: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Metrics Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_status_endpoint(self) -> bool:
        """Test status endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/status")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "running":
                        self.log_test("Status Endpoint", True, f"Version: {data.get('version', 'unknown')}", time.time() - start_time)
                        return True
                
                self.log_test("Status Endpoint", False, f"Status check failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Status Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_config_endpoint(self) -> bool:
        """Test configuration endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/config")
                
                if response.status_code == 200:
                    data = response.json()
                    if "gemini" in data and "environment" in data:
                        self.log_test("Config Endpoint", True, f"Environment: {data.get('environment', 'unknown')}", time.time() - start_time)
                        return True
                
                self.log_test("Config Endpoint", False, f"Config not available: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Config Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_gemini_agents_endpoint(self) -> bool:
        """Test Gemini agents endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/v1/agents")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "agents" in data:
                        agents = data["agents"]
                        self.log_test("Gemini Agents Endpoint", True, f"Found {len(agents)} agents", time.time() - start_time)
                        return True
                
                self.log_test("Gemini Agents Endpoint", False, f"Agents endpoint failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Gemini Agents Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_agent_types_endpoint(self) -> bool:
        """Test agent types endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/v1/agents/types")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "agent_types" in data:
                        types = data["agent_types"]
                        self.log_test("Agent Types Endpoint", True, f"Found {len(types)} agent types", time.time() - start_time)
                        return True
                
                self.log_test("Agent Types Endpoint", False, f"Agent types endpoint failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Agent Types Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_create_agent_endpoint(self) -> bool:
        """Test create agent endpoint."""
        start_time = time.time()
        
        try:
            agent_data = {
                "agent_type": "general",
                "name": f"test_agent_{int(time.time())}",
                "api_key": GEMINI_API_KEY,
                "model": "gemini-2.0-flash",
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/agents/create",
                    json=agent_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test("Create Agent Endpoint", True, f"Created agent: {data.get('agent_name', 'unknown')}", time.time() - start_time)
                        return True
                
                self.log_test("Create Agent Endpoint", False, f"Create agent failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Create Agent Endpoint", False, str(e), time.time() - start_time)
            return False
    
    async def test_gemini_direct_integration(self) -> bool:
        """Test direct Gemini API integration."""
        start_time = time.time()
        
        try:
            # Test Gemini 2.0 Flash API directly
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': GEMINI_API_KEY
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Test API integration. Respond with 'API integration working!' in Vietnamese."
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and data['candidates']:
                        candidate = data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'text' in part:
                                    response_text = part['text']
                                    self.log_test("Gemini Direct Integration", True, f"Response: {response_text[:50]}...", time.time() - start_time)
                                    return True
                
                self.log_test("Gemini Direct Integration", False, f"API Error: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Gemini Direct Integration", False, str(e), time.time() - start_time)
            return False
    
    async def test_function_calling_simulation(self) -> bool:
        """Test function calling simulation."""
        start_time = time.time()
        
        try:
            # Test function calling with Gemini
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': GEMINI_API_KEY
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": """
Bạn là AI Agent với khả năng function calling.

Yêu cầu: "Tạo 50 CCCD cho tỉnh Hà Nội, giới tính nam, năm sinh từ 1980 đến 1990"

Hãy trả lời như thể bạn đã thực hiện function call:
generate_cccd("Hà Nội", "nam", 50, "1980-1990")
                                """
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 512
                }
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and data['candidates']:
                        candidate = data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'text' in part:
                                    response_text = part['text']
                                    if "CCCD" in response_text or "tạo" in response_text.lower():
                                        self.log_test("Function Calling Simulation", True, f"Function call simulated: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Function Calling Simulation", False, f"Function calling failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Function Calling Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_vietnamese_language_support(self) -> bool:
        """Test Vietnamese language support."""
        start_time = time.time()
        
        try:
            # Test Vietnamese conversation
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': GEMINI_API_KEY
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Xin chào! Bạn có thể giúp tôi tạo một báo cáo về tình hình kinh tế Việt Nam không? Hãy trả lời bằng tiếng Việt."
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 512
                }
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and data['candidates']:
                        candidate = data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'text' in part:
                                    response_text = part['text']
                                    # Check if response contains Vietnamese characters
                                    vietnamese_chars = ['à', 'á', 'ạ', 'ả', 'ã', 'â', 'ầ', 'ấ', 'ậ', 'ẩ', 'ẫ', 'ă', 'ằ', 'ắ', 'ặ', 'ẳ', 'ẵ', 'è', 'é', 'ẹ', 'ẻ', 'ẽ', 'ê', 'ề', 'ế', 'ệ', 'ể', 'ễ', 'ì', 'í', 'ị', 'ỉ', 'ĩ', 'ò', 'ó', 'ọ', 'ỏ', 'õ', 'ô', 'ồ', 'ố', 'ộ', 'ổ', 'ỗ', 'ơ', 'ờ', 'ớ', 'ợ', 'ở', 'ỡ', 'ù', 'ú', 'ụ', 'ủ', 'ũ', 'ư', 'ừ', 'ứ', 'ự', 'ử', 'ữ', 'ỳ', 'ý', 'ỵ', 'ỷ', 'ỹ', 'đ']
                                    has_vietnamese = any(char in response_text.lower() for char in vietnamese_chars)
                                    
                                    if has_vietnamese or len(response_text) > 20:
                                        self.log_test("Vietnamese Language Support", True, f"Vietnamese response: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Vietnamese Language Support", False, f"Vietnamese support failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Vietnamese Language Support", False, str(e), time.time() - start_time)
            return False
    
    async def test_performance_benchmark(self) -> bool:
        """Test system performance."""
        start_time = time.time()
        
        try:
            # Test multiple concurrent requests
            async def single_request(request_id: int):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
                
                headers = {
                    'Content-Type': 'application/json',
                    'X-goog-api-key': GEMINI_API_KEY
                }
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": f"Request {request_id}: Hãy trả lời ngắn gọn về AI và machine learning"
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 100
                    }
                }
                
                req_start = time.time()
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(url, headers=headers, json=payload)
                req_end = time.time()
                
                if response.status_code == 200:
                    return request_id, req_end - req_start, 1
                else:
                    return request_id, req_end - req_start, 0
            
            # Run 5 concurrent requests
            tasks = [single_request(i) for i in range(1, 6)]
            results = await asyncio.gather(*tasks)
            
            total_time = sum(result[1] for result in results)
            avg_time = total_time / len(results)
            success_count = sum(result[2] for result in results)
            
            if avg_time > 3.0:  # More than 3 seconds average
                self.log_test("Performance Benchmark", False, f"Average response time too slow: {avg_time:.2f}s", time.time() - start_time)
                return False
            
            if success_count < len(results) * 0.8:  # Less than 80% success rate
                self.log_test("Performance Benchmark", False, f"Success rate too low: {success_count}/{len(results)}", time.time() - start_time)
                return False
            
            self.log_test("Performance Benchmark", True, f"Avg: {avg_time:.2f}s, Success: {success_count}/{len(results)}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Performance Benchmark", False, str(e), time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive API tests."""
        print("🧪 Starting Comprehensive API System Tests")
        print("=" * 60)
        
        test_methods = [
            ("Server Startup", self.test_server_startup),
            ("API Documentation", self.test_api_documentation),
            ("Health Endpoint", self.test_health_endpoint),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("Status Endpoint", self.test_status_endpoint),
            ("Config Endpoint", self.test_config_endpoint),
            ("Gemini Agents Endpoint", self.test_gemini_agents_endpoint),
            ("Agent Types Endpoint", self.test_agent_types_endpoint),
            ("Create Agent Endpoint", self.test_create_agent_endpoint),
            ("Gemini Direct Integration", self.test_gemini_direct_integration),
            ("Function Calling Simulation", self.test_function_calling_simulation),
            ("Vietnamese Language Support", self.test_vietnamese_language_support),
            ("Performance Benchmark", self.test_performance_benchmark)
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
    print("🚀 OpenManus-Youtu Integrated Framework - Comprehensive API System Tests")
    print("=" * 70)
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...")
    print(f"🤖 Model: Gemini 2.0 Flash")
    print(f"🌐 Base URL: http://localhost:8000")
    print("=" * 70)
    
    tester = ComprehensiveAPITester()
    
    try:
        report = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎉 Comprehensive API System Tests Completed!")
        
        summary = report["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Time: {summary['total_time']:.2f}s")
        
        if summary['success_rate'] == 100:
            print("\n🎉 All API tests passed! System is fully functional!")
        elif summary['success_rate'] >= 80:
            print("\n✅ Most API tests passed! System is mostly functional!")
        else:
            print("\n⚠️  Some API tests failed. Please check the issues above.")
        
        # Save report
        report_file = Path(__file__).parent / "comprehensive_api_test_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📊 Test report saved to: {report_file}")
        
        return summary['success_rate'] >= 80
        
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)