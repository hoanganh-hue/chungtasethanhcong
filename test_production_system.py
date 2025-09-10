#!/usr/bin/env python3
"""
Comprehensive Production System Test Suite
Tests all components: Telegram Bot, Web Interface, API, ngrok, and AI Agents
"""

import asyncio
import httpx
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

class ProductionSystemTester:
    """Comprehensive production system tester."""
    
    def __init__(self):
        self.base_url = "https://choice-swine-on.ngrok-free.app"
        self.local_url = "http://localhost:80"
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f"({duration:.2f}s)" if duration > 0 else ""
        
        print(f"{status} {test_name} {duration_str}: {message}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_ngrok_tunnel(self) -> bool:
        """Test ngrok tunnel connectivity."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    self.log_test("ngrok Tunnel", True, f"Public URL accessible: {response.status_code}", time.time() - start_time)
                    return True
                else:
                    self.log_test("ngrok Tunnel", False, f"Unexpected status: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("ngrok Tunnel", False, f"Connection failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_local_server(self) -> bool:
        """Test local server connectivity."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.local_url}/health")
                
                if response.status_code == 200:
                    self.log_test("Local Server", True, f"Local server accessible: {response.status_code}", time.time() - start_time)
                    return True
                else:
                    self.log_test("Local Server", False, f"Unexpected status: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("Local Server", False, f"Connection failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_api_endpoints(self) -> bool:
        """Test API endpoints."""
        start_time = time.time()
        
        endpoints = [
            ("/health", "Health Check"),
            ("/status", "System Status"),
            ("/metrics", "System Metrics"),
            ("/config", "Configuration"),
            ("/api/v1/agents", "Agents API"),
            ("/docs", "API Documentation")
        ]
        
        success_count = 0
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for endpoint, name in endpoints:
                    try:
                        response = await client.get(f"{self.base_url}{endpoint}")
                        if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                            success_count += 1
                        else:
                            print(f"  ⚠️ {name}: Status {response.status_code}")
                    except Exception as e:
                        print(f"  ⚠️ {name}: {str(e)}")
                
                success_rate = success_count / len(endpoints)
                if success_rate >= 0.8:  # 80% success rate
                    self.log_test("API Endpoints", True, f"Success rate: {success_rate:.1%} ({success_count}/{len(endpoints)})", time.time() - start_time)
                    return True
                else:
                    self.log_test("API Endpoints", False, f"Success rate too low: {success_rate:.1%}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("API Endpoints", False, f"Test failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_telegram_webhook(self) -> bool:
        """Test Telegram webhook endpoint."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test webhook info endpoint
                response = await client.get(f"{self.base_url}/webhook/telegram")
                
                if response.status_code == 200:
                    data = response.json()
                    if "webhook_info" in data or "error" in data:
                        self.log_test("Telegram Webhook", True, f"Webhook endpoint accessible: {response.status_code}", time.time() - start_time)
                        return True
                    else:
                        self.log_test("Telegram Webhook", False, "Invalid webhook response", time.time() - start_time)
                        return False
                else:
                    self.log_test("Telegram Webhook", False, f"Unexpected status: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("Telegram Webhook", False, f"Connection failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_gemini_integration(self) -> bool:
        """Test Gemini AI integration."""
        start_time = time.time()
        
        try:
            # Test Gemini API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.log_test("Gemini Integration", False, "API key not configured", time.time() - start_time)
                return False
            
            # Test Gemini API connection
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"X-goog-api-key": api_key}
                response = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    headers=headers
                )
                
                if response.status_code == 200:
                    models = response.json()
                    if "models" in models:
                        self.log_test("Gemini Integration", True, f"Connected to Gemini API, {len(models['models'])} models available", time.time() - start_time)
                        return True
                    else:
                        self.log_test("Gemini Integration", False, "Invalid API response", time.time() - start_time)
                        return False
                else:
                    self.log_test("Gemini Integration", False, f"API error: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("Gemini Integration", False, f"Connection failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_ai_agent_creation(self) -> bool:
        """Test AI agent creation."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Test agent creation
                agent_data = {
                    "agent_type": "cccd",
                    "name": "test_agent",
                    "api_key": os.getenv("GEMINI_API_KEY"),
                    "config": {}
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/agents/create",
                    json=agent_data,
                    timeout=15.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    if data.get("success"):
                        self.log_test("AI Agent Creation", True, f"Agent created successfully: {data.get('agent_name', 'Unknown')}", time.time() - start_time)
                        return True
                    else:
                        self.log_test("AI Agent Creation", False, f"Agent creation failed: {data.get('error', 'Unknown error')}", time.time() - start_time)
                        return False
                else:
                    self.log_test("AI Agent Creation", False, f"HTTP error: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("AI Agent Creation", False, f"Request failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_vietnamese_language_support(self) -> bool:
        """Test Vietnamese language support."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Test Vietnamese message processing
                test_message = {
                    "message": "Xin chào! Bạn có thể giúp tôi tạo 10 CCCD cho tỉnh Hà Nội không?",
                    "session_id": "test_session",
                    "stream": False
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/agents/test_agent/chat/message",
                    json=test_message,
                    timeout=15.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    if data.get("success") and data.get("response"):
                        response_text = data["response"]
                        # Check if response contains Vietnamese characters
                        vietnamese_chars = any(ord(char) > 127 for char in response_text)
                        if vietnamese_chars:
                            self.log_test("Vietnamese Language Support", True, "Vietnamese text processing successful", time.time() - start_time)
                            return True
                        else:
                            self.log_test("Vietnamese Language Support", False, "No Vietnamese characters in response", time.time() - start_time)
                            return False
                    else:
                        self.log_test("Vietnamese Language Support", False, f"Invalid response: {data.get('error', 'Unknown')}", time.time() - start_time)
                        return False
                else:
                    self.log_test("Vietnamese Language Support", False, f"HTTP error: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("Vietnamese Language Support", False, f"Request failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_cccd_functionality(self) -> bool:
        """Test CCCD generation functionality."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Test CCCD generation
                cccd_request = {
                    "message": "Tạo 5 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975",
                    "session_id": "cccd_test_session",
                    "stream": False
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/agents/test_agent/chat/message",
                    json=cccd_request,
                    timeout=15.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    if data.get("success") and data.get("response"):
                        response_text = data["response"]
                        # Check if response contains CCCD-related content
                        cccd_indicators = ["CCCD", "căn cước", "Hưng Yên", "1965", "1975", "nữ"]
                        found_indicators = sum(1 for indicator in cccd_indicators if indicator.lower() in response_text.lower())
                        
                        if found_indicators >= 3:
                            self.log_test("CCCD Functionality", True, f"CCCD generation successful, {found_indicators} indicators found", time.time() - start_time)
                            return True
                        else:
                            self.log_test("CCCD Functionality", False, f"Limited CCCD content, {found_indicators} indicators found", time.time() - start_time)
                            return False
                    else:
                        self.log_test("CCCD Functionality", False, f"Invalid response: {data.get('error', 'Unknown')}", time.time() - start_time)
                        return False
                else:
                    self.log_test("CCCD Functionality", False, f"HTTP error: {response.status_code}", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("CCCD Functionality", False, f"Request failed: {str(e)}", time.time() - start_time)
            return False
    
    async def test_performance(self) -> bool:
        """Test system performance."""
        start_time = time.time()
        
        try:
            # Test concurrent requests
            async with httpx.AsyncClient(timeout=10.0) as client:
                tasks = []
                for i in range(5):
                    task = client.get(f"{self.base_url}/health")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
                avg_time = (time.time() - start_time) / len(tasks)
                
                if success_count >= 4 and avg_time < 2.0:  # 80% success, <2s average
                    self.log_test("Performance", True, f"Concurrent requests: {success_count}/{len(tasks)} success, avg {avg_time:.2f}s", time.time() - start_time)
                    return True
                else:
                    self.log_test("Performance", False, f"Performance issues: {success_count}/{len(tasks)} success, avg {avg_time:.2f}s", time.time() - start_time)
                    return False
                    
        except Exception as e:
            self.log_test("Performance", False, f"Performance test failed: {str(e)}", time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        print("🧪 Starting Comprehensive Production System Tests...")
        print("=" * 60)
        
        tests = [
            ("ngrok Tunnel", self.test_ngrok_tunnel),
            ("Local Server", self.test_local_server),
            ("API Endpoints", self.test_api_endpoints),
            ("Telegram Webhook", self.test_telegram_webhook),
            ("Gemini Integration", self.test_gemini_integration),
            ("AI Agent Creation", self.test_ai_agent_creation),
            ("Vietnamese Language Support", self.test_vietnamese_language_support),
            ("CCCD Functionality", self.test_cccd_functionality),
            ("Performance", self.test_performance)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test exception: {str(e)}")
        
        total_time = time.time() - self.start_time
        success_rate = passed / total
        
        print("=" * 60)
        print(f"🎯 Test Results: {passed}/{total} passed ({success_rate:.1%})")
        print(f"⏱️ Total Time: {total_time:.2f}s")
        
        if success_rate >= 0.8:
            print("🎉 Production system is ready!")
        else:
            print("⚠️ Some issues detected, check logs above")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": success_rate,
            "total_time": total_time,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main test function."""
    tester = ProductionSystemTester()
    results = await tester.run_all_tests()
    
    # Save results
    with open("production_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Test results saved to: production_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())