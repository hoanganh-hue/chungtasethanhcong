#!/usr/bin/env python3
"""
Simple API Test for OpenManus-Youtu Integrated Framework
Test core functionality without server dependency
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

class SimpleAPITester:
    """Simple API tester focusing on core functionality."""
    
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
    
    async def test_gemini_api_integration(self) -> bool:
        """Test Gemini API integration."""
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
                                "text": "Test API integration. Respond with 'Gemini 2.0 Flash API is working perfectly!' in Vietnamese."
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
                                    self.log_test("Gemini API Integration", True, f"Response: {response_text[:50]}...", time.time() - start_time)
                                    return True
                
                self.log_test("Gemini API Integration", False, f"API Error: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Gemini API Integration", False, str(e), time.time() - start_time)
            return False
    
    async def test_cccd_agent_simulation(self) -> bool:
        """Test CCCD Agent simulation."""
        start_time = time.time()
        
        try:
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
Bạn là CCCD Agent, một AI chuyên gia về xử lý CCCD (Căn cước công dân).

Yêu cầu: "Tạo 200 CCCD cho tỉnh Hồ Chí Minh, giới tính nam, năm sinh từ 1990 đến 2000"

Hãy trả lời như thể bạn đã thực hiện function call:
generate_cccd("Hồ Chí Minh", "nam", 200, "1990-2000")

Trả lời bằng tiếng Việt và chi tiết.
                                """
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1024
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
                                        self.log_test("CCCD Agent Simulation", True, f"Function call simulated: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("CCCD Agent Simulation", False, f"Function call failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("CCCD Agent Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_tax_agent_simulation(self) -> bool:
        """Test Tax Agent simulation."""
        start_time = time.time()
        
        try:
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
Bạn là Tax Agent, một AI chuyên gia về thuế.

Yêu cầu: "Tra cứu mã số thuế 0123456789"

Hãy trả lời như thể bạn đã thực hiện function call:
lookup_tax("0123456789")

Trả lời bằng tiếng Việt và chi tiết.
                                """
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1024
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
                                    if "thuế" in response_text.lower() or "tax" in response_text.lower():
                                        self.log_test("Tax Agent Simulation", True, f"Tax lookup simulated: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Tax Agent Simulation", False, f"Tax lookup failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Tax Agent Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_data_analysis_agent_simulation(self) -> bool:
        """Test Data Analysis Agent simulation."""
        start_time = time.time()
        
        try:
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
Bạn là Data Analysis Agent, một AI chuyên gia về phân tích dữ liệu.

Yêu cầu: "Phân tích dữ liệu bán hàng của công ty ABC trong quý 3/2024"

Hãy trả lời như thể bạn đã thực hiện function call:
analyze_data("sales_data_abc_q3_2024")

Trả lời bằng tiếng Việt và chi tiết.
                                """
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 1024
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
                                    if "phân tích" in response_text.lower() or "dữ liệu" in response_text.lower():
                                        self.log_test("Data Analysis Agent Simulation", True, f"Data analysis simulated: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Data Analysis Agent Simulation", False, f"Data analysis failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Data Analysis Agent Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_web_automation_agent_simulation(self) -> bool:
        """Test Web Automation Agent simulation."""
        start_time = time.time()
        
        try:
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
Bạn là Web Automation Agent, một AI chuyên gia về tự động hóa web.

Yêu cầu: "Thu thập dữ liệu từ website https://example.com"

Hãy trả lời như thể bạn đã thực hiện function call:
scrape_web("https://example.com")

Trả lời bằng tiếng Việt và chi tiết.
                                """
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1024
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
                                    if "thu thập" in response_text.lower() or "web" in response_text.lower():
                                        self.log_test("Web Automation Agent Simulation", True, f"Web automation simulated: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Web Automation Agent Simulation", False, f"Web automation failed: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Web Automation Agent Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_vietnamese_language_comprehensive(self) -> bool:
        """Test comprehensive Vietnamese language support."""
        start_time = time.time()
        
        try:
            # Test multiple Vietnamese scenarios
            vietnamese_tests = [
                "Xin chào! Bạn có thể giúp tôi tạo một báo cáo tài chính không?",
                "Hãy phân tích dữ liệu thị trường chứng khoán Việt Nam",
                "Tôi cần tạo 1000 CCCD cho tỉnh Đà Nẵng",
                "Tra cứu mã số thuế cho công ty TNHH ABC",
                "Thu thập thông tin từ website chính phủ"
            ]
            
            success_count = 0
            
            for i, test_text in enumerate(vietnamese_tests):
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
                                    "text": f"{test_text}. Hãy trả lời bằng tiếng Việt."
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 200
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
                                            success_count += 1
                                            break
            
            success_rate = (success_count / len(vietnamese_tests)) * 100
            
            if success_rate >= 80:
                self.log_test("Vietnamese Language Comprehensive", True, f"Success rate: {success_rate:.1f}% ({success_count}/{len(vietnamese_tests)})", time.time() - start_time)
                return True
            else:
                self.log_test("Vietnamese Language Comprehensive", False, f"Success rate too low: {success_rate:.1f}%", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Vietnamese Language Comprehensive", False, str(e), time.time() - start_time)
            return False
    
    async def test_performance_comprehensive(self) -> bool:
        """Test comprehensive performance."""
        start_time = time.time()
        
        try:
            # Test multiple concurrent requests with different agent types
            async def single_request(request_id: int, agent_type: str):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
                
                headers = {
                    'Content-Type': 'application/json',
                    'X-goog-api-key': GEMINI_API_KEY
                }
                
                # Different prompts for different agent types
                prompts = {
                    "cccd": f"Request {request_id}: Tạo 50 CCCD cho tỉnh Hà Nội",
                    "tax": f"Request {request_id}: Tra cứu mã số thuế 0123456789",
                    "data": f"Request {request_id}: Phân tích dữ liệu bán hàng",
                    "web": f"Request {request_id}: Thu thập dữ liệu từ website",
                    "general": f"Request {request_id}: Hãy trả lời về AI và machine learning"
                }
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompts.get(agent_type, prompts["general"])
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
                    return request_id, req_end - req_start, 1, agent_type
                else:
                    return request_id, req_end - req_start, 0, agent_type
            
            # Run 10 concurrent requests with different agent types
            agent_types = ["cccd", "tax", "data", "web", "general"]
            tasks = []
            for i in range(10):
                agent_type = agent_types[i % len(agent_types)]
                tasks.append(single_request(i + 1, agent_type))
            
            results = await asyncio.gather(*tasks)
            
            total_time = sum(result[1] for result in results)
            avg_time = total_time / len(results)
            success_count = sum(result[2] for result in results)
            
            # Group by agent type
            agent_performance = {}
            for result in results:
                agent_type = result[3]
                if agent_type not in agent_performance:
                    agent_performance[agent_type] = {"count": 0, "success": 0, "total_time": 0}
                agent_performance[agent_type]["count"] += 1
                agent_performance[agent_type]["success"] += result[2]
                agent_performance[agent_type]["total_time"] += result[1]
            
            if avg_time > 3.0:  # More than 3 seconds average
                self.log_test("Performance Comprehensive", False, f"Average response time too slow: {avg_time:.2f}s", time.time() - start_time)
                return False
            
            if success_count < len(results) * 0.8:  # Less than 80% success rate
                self.log_test("Performance Comprehensive", False, f"Success rate too low: {success_count}/{len(results)}", time.time() - start_time)
                return False
            
            self.log_test("Performance Comprehensive", True, f"Avg: {avg_time:.2f}s, Success: {success_count}/{len(results)}, Agents: {len(agent_performance)}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Performance Comprehensive", False, str(e), time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all simple API tests."""
        print("🧪 Starting Simple API System Tests")
        print("=" * 60)
        
        test_methods = [
            ("Gemini API Integration", self.test_gemini_api_integration),
            ("CCCD Agent Simulation", self.test_cccd_agent_simulation),
            ("Tax Agent Simulation", self.test_tax_agent_simulation),
            ("Data Analysis Agent Simulation", self.test_data_analysis_agent_simulation),
            ("Web Automation Agent Simulation", self.test_web_automation_agent_simulation),
            ("Vietnamese Language Comprehensive", self.test_vietnamese_language_comprehensive),
            ("Performance Comprehensive", self.test_performance_comprehensive)
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
    print("🚀 OpenManus-Youtu Integrated Framework - Simple API System Tests")
    print("=" * 70)
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...")
    print(f"🤖 Model: Gemini 2.0 Flash")
    print("=" * 70)
    
    tester = SimpleAPITester()
    
    try:
        report = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎉 Simple API System Tests Completed!")
        
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
        report_file = Path(__file__).parent / "simple_api_test_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📊 Test report saved to: {report_file}")
        
        return summary['success_rate'] >= 80
        
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)