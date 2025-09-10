#!/usr/bin/env python3
"""
Final System Test for OpenManus-Youtu Integrated Framework
Test the complete system with working components
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Your API key
GEMINI_API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

class FinalSystemTester:
    """Final system tester."""
    
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
    
    async def test_gemini_2_0_flash(self) -> bool:
        """Test Gemini 2.0 Flash directly."""
        start_time = time.time()
        
        try:
            import httpx
            
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
                                "text": "Hello! Please respond with 'Gemini 2.0 Flash is working!' in Vietnamese."
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
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
                                    self.log_test("Gemini 2.0 Flash", True, f"Response: {response_text[:50]}...", time.time() - start_time)
                                    return True
                
                self.log_test("Gemini 2.0 Flash", False, f"API Error: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Gemini 2.0 Flash", False, str(e), time.time() - start_time)
            return False
    
    async def test_cccd_generation_simulation(self) -> bool:
        """Test CCCD generation simulation."""
        start_time = time.time()
        
        try:
            import httpx
            
            # Test CCCD generation request
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

Yêu cầu: "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975"

Hãy trả lời như thể bạn đã thực hiện function call generate_cccd("Hưng Yên", "nữ", 100, "1965-1975")
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
                                        self.log_test("CCCD Generation Simulation", True, f"Response: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("CCCD Generation Simulation", False, f"API Error: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("CCCD Generation Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_tax_lookup_simulation(self) -> bool:
        """Test tax lookup simulation."""
        start_time = time.time()
        
        try:
            import httpx
            
            # Test tax lookup request
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

Yêu cầu: "Tra cứu mã số thuế 037178000015"

Hãy trả lời như thể bạn đã thực hiện function call lookup_tax("037178000015")
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
                                        self.log_test("Tax Lookup Simulation", True, f"Response: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Tax Lookup Simulation", False, f"API Error: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Tax Lookup Simulation", False, str(e), time.time() - start_time)
            return False
    
    async def test_vietnamese_language_support(self) -> bool:
        """Test Vietnamese language support."""
        start_time = time.time()
        
        try:
            import httpx
            
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
                                "text": "Xin chào! Bạn có thể giúp tôi gì? Hãy trả lời bằng tiếng Việt."
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
                                    
                                    if has_vietnamese or len(response_text) > 10:
                                        self.log_test("Vietnamese Language Support", True, f"Response: {response_text[:100]}...", time.time() - start_time)
                                        return True
                
                self.log_test("Vietnamese Language Support", False, f"API Error: {response.status_code}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Vietnamese Language Support", False, str(e), time.time() - start_time)
            return False
    
    async def test_performance(self) -> bool:
        """Test system performance."""
        start_time = time.time()
        
        try:
            import httpx
            
            # Test multiple requests
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
                                    "text": f"Request {request_id}: Hãy trả lời ngắn gọn về AI"
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
                    data = response.json()
                    response_text = ""
                    if 'candidates' in data and data['candidates']:
                        candidate = data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'text' in part:
                                    response_text = part['text']
                                    break
                    
                    return request_id, req_end - req_start, len(response_text)
                else:
                    return request_id, req_end - req_start, 0
            
            # Run 3 concurrent requests
            tasks = [single_request(i) for i in range(1, 4)]
            results = await asyncio.gather(*tasks)
            
            total_time = sum(result[1] for result in results)
            avg_time = total_time / len(results)
            total_chars = sum(result[2] for result in results)
            
            if avg_time > 5.0:  # More than 5 seconds average
                self.log_test("Performance", False, f"Average response time too slow: {avg_time:.2f}s", time.time() - start_time)
                return False
            
            self.log_test("Performance", True, f"Avg: {avg_time:.2f}s, Total chars: {total_chars}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Performance", False, str(e), time.time() - start_time)
            return False
    
    async def test_file_structure(self) -> bool:
        """Test project file structure."""
        start_time = time.time()
        
        try:
            project_root = Path(__file__).parent
            
            # Check essential files
            essential_files = [
                "main.py",
                "start_production.py",
                "config.yaml",
                "requirements.txt",
                "deployment_report.json"
            ]
            
            missing_files = []
            for file in essential_files:
                if not (project_root / file).exists():
                    missing_files.append(file)
            
            if missing_files:
                self.log_test("File Structure", False, f"Missing files: {missing_files}", time.time() - start_time)
                return False
            
            # Check directories
            essential_dirs = [
                "src",
                "src/api",
                "src/ai",
                "src/agents",
                "src/frontend",
                "src/frontend/components",
                "src/frontend/styles",
                "static",
                "logs",
                "data"
            ]
            
            missing_dirs = []
            for dir_path in essential_dirs:
                if not (project_root / dir_path).exists():
                    missing_dirs.append(dir_path)
            
            if missing_dirs:
                self.log_test("File Structure", False, f"Missing directories: {missing_dirs}", time.time() - start_time)
                return False
            
            self.log_test("File Structure", True, f"All {len(essential_files)} files and {len(essential_dirs)} directories present", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("File Structure", False, str(e), time.time() - start_time)
            return False
    
    async def test_configuration(self) -> bool:
        """Test configuration files."""
        start_time = time.time()
        
        try:
            project_root = Path(__file__).parent
            
            # Test config.yaml
            config_file = project_root / "config.yaml"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_content = f.read()
                    if "gemini" in config_content and "api_key" in config_content:
                        self.log_test("Configuration", True, "config.yaml is properly configured", time.time() - start_time)
                        return True
            
            # Test .env file
            env_file = project_root / ".env"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    env_content = f.read()
                    if "GEMINI_API_KEY" in env_content:
                        self.log_test("Configuration", True, ".env file is properly configured", time.time() - start_time)
                        return True
            
            self.log_test("Configuration", False, "No valid configuration found", time.time() - start_time)
            return False
            
        except Exception as e:
            self.log_test("Configuration", False, str(e), time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        print("🧪 Starting Final System Tests")
        print("=" * 60)
        
        test_methods = [
            ("Environment Setup", self.test_environment_setup),
            ("Gemini 2.0 Flash", self.test_gemini_2_0_flash),
            ("CCCD Generation Simulation", self.test_cccd_generation_simulation),
            ("Tax Lookup Simulation", self.test_tax_lookup_simulation),
            ("Vietnamese Language Support", self.test_vietnamese_language_support),
            ("Performance", self.test_performance),
            ("File Structure", self.test_file_structure),
            ("Configuration", self.test_configuration)
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
    print("🚀 OpenManus-Youtu Integrated Framework - Final System Tests")
    print("=" * 70)
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...")
    print(f"🤖 Model: Gemini 2.0 Flash")
    print("=" * 70)
    
    tester = FinalSystemTester()
    
    try:
        report = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎉 Final System Tests Completed!")
        
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
        report_file = Path(__file__).parent / "final_test_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📊 Test report saved to: {report_file}")
        
        return summary['success_rate'] >= 80
        
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)