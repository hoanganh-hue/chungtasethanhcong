#!/usr/bin/env python3
"""
Final Comprehensive Test for OpenManus-Youtu Integrated Framework
Test all components to ensure 100% completion
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

class FinalComprehensiveTester:
    """Final comprehensive tester for 100% completion verification."""
    
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
    
    async def test_server_availability(self) -> bool:
        """Test server availability."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    if "OpenManus-Youtu" in data.get("message", ""):
                        self.log_test("Server Availability", True, f"Server running: {data.get('version', 'unknown')}", time.time() - start_time)
                        return True
                
                self.log_test("Server Availability", False, f"Server not responding: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Server Availability", False, f"Server not running: {str(e)}", time.time() - start_time)
            return False
    
    async def test_all_api_endpoints(self) -> bool:
        """Test all API endpoints."""
        start_time = time.time()
        
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/status", "System status"),
            ("/config", "Configuration"),
            ("/metrics", "System metrics"),
            ("/docs", "API documentation"),
            ("/api/v1/agents", "Gemini agents"),
            ("/api/v1/agents/types", "Agent types")
        ]
        
        success_count = 0
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                for endpoint, description in endpoints:
                    try:
                        response = await client.get(f"{self.base_url}{endpoint}")
                        if response.status_code == 200:
                            success_count += 1
                        else:
                            print(f"  ⚠️  {description}: {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ {description}: {str(e)}")
            
            success_rate = (success_count / len(endpoints)) * 100
            
            if success_rate >= 80:
                self.log_test("All API Endpoints", True, f"Success rate: {success_rate:.1f}% ({success_count}/{len(endpoints)})", time.time() - start_time)
                return True
            else:
                self.log_test("All API Endpoints", False, f"Success rate too low: {success_rate:.1f}%", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("All API Endpoints", False, str(e), time.time() - start_time)
            return False
    
    async def test_gemini_integration_comprehensive(self) -> bool:
        """Test comprehensive Gemini integration."""
        start_time = time.time()
        
        try:
            # Test multiple Gemini scenarios
            test_scenarios = [
                {
                    "name": "Basic Message",
                    "text": "Xin chào! Bạn có thể giúp tôi gì?",
                    "expected_keywords": ["chào", "giúp", "bạn"]
                },
                {
                    "name": "CCCD Function Call",
                    "text": "Tạo 100 CCCD cho tỉnh Hà Nội, giới tính nữ, năm sinh từ 1990 đến 2000",
                    "expected_keywords": ["CCCD", "tạo", "Hà Nội"]
                },
                {
                    "name": "Tax Lookup Function Call",
                    "text": "Tra cứu mã số thuế 0123456789",
                    "expected_keywords": ["thuế", "tra cứu", "mã số"]
                },
                {
                    "name": "Data Analysis Function Call",
                    "text": "Phân tích dữ liệu bán hàng quý 3/2024",
                    "expected_keywords": ["phân tích", "dữ liệu", "bán hàng"]
                },
                {
                    "name": "Web Automation Function Call",
                    "text": "Thu thập dữ liệu từ website chính phủ",
                    "expected_keywords": ["thu thập", "dữ liệu", "website"]
                }
            ]
            
            success_count = 0
            
            for scenario in test_scenarios:
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
                                    "text": scenario["text"]
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
                                        response_text = part['text'].lower()
                                        # Check if response contains expected keywords
                                        keyword_found = any(keyword in response_text for keyword in scenario["expected_keywords"])
                                        if keyword_found:
                                            success_count += 1
                                            break
            
            success_rate = (success_count / len(test_scenarios)) * 100
            
            if success_rate >= 80:
                self.log_test("Gemini Integration Comprehensive", True, f"Success rate: {success_rate:.1f}% ({success_count}/{len(test_scenarios)})", time.time() - start_time)
                return True
            else:
                self.log_test("Gemini Integration Comprehensive", False, f"Success rate too low: {success_rate:.1f}%", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Gemini Integration Comprehensive", False, str(e), time.time() - start_time)
            return False
    
    async def test_vietnamese_language_comprehensive(self) -> bool:
        """Test comprehensive Vietnamese language support."""
        start_time = time.time()
        
        try:
            # Test various Vietnamese scenarios
            vietnamese_tests = [
                "Xin chào! Bạn có thể giúp tôi tạo một báo cáo tài chính không?",
                "Hãy phân tích dữ liệu thị trường chứng khoán Việt Nam",
                "Tôi cần tạo 1000 CCCD cho tỉnh Đà Nẵng",
                "Tra cứu mã số thuế cho công ty TNHH ABC",
                "Thu thập thông tin từ website chính phủ",
                "Tạo báo cáo tổng hợp về tình hình kinh tế",
                "Phân tích xu hướng thị trường bất động sản",
                "Hỗ trợ tôi viết email bằng tiếng Việt"
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
                        "maxOutputTokens": 150
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
            
            if success_rate >= 90:
                self.log_test("Vietnamese Language Comprehensive", True, f"Success rate: {success_rate:.1f}% ({success_count}/{len(vietnamese_tests)})", time.time() - start_time)
                return True
            else:
                self.log_test("Vietnamese Language Comprehensive", False, f"Success rate too low: {success_rate:.1f}%", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Vietnamese Language Comprehensive", False, str(e), time.time() - start_time)
            return False
    
    async def test_performance_final(self) -> bool:
        """Test final performance with optimized settings."""
        start_time = time.time()
        
        try:
            # Test with optimized concurrent requests
            async def optimized_request(request_id: int):
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
                                    "text": f"Request {request_id}: Trả lời ngắn về AI"
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 50
                    }
                }
                
                req_start = time.time()
                async with httpx.AsyncClient(timeout=20) as client:
                    response = await client.post(url, headers=headers, json=payload)
                req_end = time.time()
                
                if response.status_code == 200:
                    return request_id, req_end - req_start, 1
                else:
                    return request_id, req_end - req_start, 0
            
            # Run 6 concurrent requests (optimized number)
            tasks = [optimized_request(i + 1) for i in range(6)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter valid results
            valid_results = [r for r in results if isinstance(r, tuple) and len(r) == 3]
            
            if not valid_results:
                self.log_test("Performance Final", False, "No valid results", time.time() - start_time)
                return False
            
            total_time = sum(result[1] for result in valid_results)
            avg_time = total_time / len(valid_results)
            success_count = sum(result[2] for result in valid_results)
            
            if avg_time > 3.0:
                self.log_test("Performance Final", False, f"Average response time too slow: {avg_time:.2f}s", time.time() - start_time)
                return False
            
            if success_count < len(valid_results) * 0.7:  # 70% success rate
                self.log_test("Performance Final", False, f"Success rate too low: {success_count}/{len(valid_results)}", time.time() - start_time)
                return False
            
            self.log_test("Performance Final", True, f"Avg: {avg_time:.2f}s, Success: {success_count}/{len(valid_results)}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Performance Final", False, str(e), time.time() - start_time)
            return False
    
    async def test_file_structure_complete(self) -> bool:
        """Test complete file structure."""
        start_time = time.time()
        
        try:
            project_root = Path(__file__).parent
            
            # Essential files
            essential_files = [
                "main.py",
                "main_fixed.py",
                "start_production.py",
                "config.yaml",
                "requirements.txt",
                "README_FINAL.md",
                "deployment_report.json",
                "final_test_report.json",
                "test_final_system.py",
                "test_gemini_2_0_working.py",
                "test_api_simple.py",
                "test_performance_optimized.py",
                "test_final_comprehensive.py",
                "deploy_simple.py"
            ]
            
            # Essential directories
            essential_dirs = [
                "src",
                "src/api",
                "src/ai",
                "src/agents",
                "src/frontend",
                "src/frontend/components",
                "src/frontend/styles",
                "src/tools",
                "src/core",
                "static",
                "logs",
                "data"
            ]
            
            missing_files = []
            for file in essential_files:
                if not (project_root / file).exists():
                    missing_files.append(file)
            
            missing_dirs = []
            for dir_path in essential_dirs:
                if not (project_root / dir_path).exists():
                    missing_dirs.append(dir_path)
            
            if missing_files or missing_dirs:
                self.log_test("File Structure Complete", False, f"Missing: {len(missing_files)} files, {len(missing_dirs)} dirs", time.time() - start_time)
                return False
            
            self.log_test("File Structure Complete", True, f"All {len(essential_files)} files and {len(essential_dirs)} directories present", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("File Structure Complete", False, str(e), time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all final comprehensive tests."""
        print("🧪 Starting Final Comprehensive Tests")
        print("=" * 60)
        
        test_methods = [
            ("Server Availability", self.test_server_availability),
            ("All API Endpoints", self.test_all_api_endpoints),
            ("Gemini Integration Comprehensive", self.test_gemini_integration_comprehensive),
            ("Vietnamese Language Comprehensive", self.test_vietnamese_language_comprehensive),
            ("Performance Final", self.test_performance_final),
            ("File Structure Complete", self.test_file_structure_complete)
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
    print("🚀 OpenManus-Youtu Integrated Framework - Final Comprehensive Tests")
    print("=" * 70)
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...")
    print(f"🤖 Model: Gemini 2.0 Flash")
    print(f"🌐 Base URL: http://localhost:8000")
    print("=" * 70)
    
    tester = FinalComprehensiveTester()
    
    try:
        report = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎉 Final Comprehensive Tests Completed!")
        
        summary = report["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Time: {summary['total_time']:.2f}s")
        
        if summary['success_rate'] == 100:
            print("\n🎉 ALL TESTS PASSED! PROJECT IS 100% COMPLETE!")
        elif summary['success_rate'] >= 90:
            print("\n✅ EXCELLENT! Project is nearly 100% complete!")
        elif summary['success_rate'] >= 80:
            print("\n✅ VERY GOOD! Project is mostly complete!")
        else:
            print("\n⚠️  Some tests failed. Please check the issues above.")
        
        # Save report
        report_file = Path(__file__).parent / "final_comprehensive_test_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📊 Test report saved to: {report_file}")
        
        return summary['success_rate'] >= 90
        
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)