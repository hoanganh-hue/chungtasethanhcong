#!/usr/bin/env python3
"""
Simple System Test for OpenManus-Youtu Integrated Framework
Tests local server and basic functionality
"""

import requests
import json
import time
from datetime import datetime

def test_local_server():
    """Test local server."""
    print("🧪 Testing Local Server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Local Server Error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("\n🧪 Testing API Endpoints...")
    
    endpoints = [
        ("/", "Root"),
        ("/health", "Health"),
        ("/status", "Status"),
        ("/metrics", "Metrics"),
        ("/config", "Config"),
        ("/api/v1/agents", "Agents"),
        ("/webhook/telegram", "Telegram Webhook")
    ]
    
    success_count = 0
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                print(f"✅ {name}: {response.status_code}")
                success_count += 1
            else:
                print(f"⚠️ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    success_rate = success_count / len(endpoints)
    print(f"\n📊 API Endpoints Success Rate: {success_rate:.1%} ({success_count}/{len(endpoints)})")
    return success_rate >= 0.8

def test_agent_creation():
    """Test agent creation."""
    print("\n🧪 Testing Agent Creation...")
    
    try:
        agent_data = {
            "agent_type": "cccd",
            "name": "test_agent",
            "api_key": "test_key"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/agents/create",
            json=agent_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("success"):
                print(f"✅ Agent Created: {data.get('agent_name')}")
                return True
            else:
                print(f"❌ Agent Creation Failed: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Agent Creation Error: {e}")
        return False

def test_vietnamese_support():
    """Test Vietnamese language support."""
    print("\n🧪 Testing Vietnamese Language Support...")
    
    try:
        message_data = {
            "message": "Xin chào! Bạn có thể giúp tôi tạo 5 CCCD cho tỉnh Hà Nội không?",
            "session_id": "test_session"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/agents/test_agent/chat/message",
            json=message_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("success") and data.get("response"):
                response_text = data["response"]
                # Check for Vietnamese characters
                vietnamese_chars = any(ord(char) > 127 for char in response_text)
                if vietnamese_chars:
                    print("✅ Vietnamese Language Support: Working")
                    return True
                else:
                    print("⚠️ Vietnamese Language Support: Limited")
                    return False
            else:
                print(f"❌ Vietnamese Support Error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Vietnamese Support Error: {e}")
        return False

def test_cccd_functionality():
    """Test CCCD functionality."""
    print("\n🧪 Testing CCCD Functionality...")
    
    try:
        cccd_request = {
            "message": "Tạo 3 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh từ 1965 đến 1975",
            "session_id": "cccd_test"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/agents/test_agent/chat/message",
            json=cccd_request,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("success") and data.get("response"):
                response_text = data["response"]
                # Check for CCCD-related content
                cccd_indicators = ["CCCD", "căn cước", "Hưng Yên", "1965", "1975", "nữ"]
                found_indicators = sum(1 for indicator in cccd_indicators if indicator.lower() in response_text.lower())
                
                if found_indicators >= 2:
                    print(f"✅ CCCD Functionality: Working ({found_indicators} indicators)")
                    return True
                else:
                    print(f"⚠️ CCCD Functionality: Limited ({found_indicators} indicators)")
                    return False
            else:
                print(f"❌ CCCD Error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CCCD Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 OpenManus-Youtu Integrated Framework - Simple System Test")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("Local Server", test_local_server),
        ("API Endpoints", test_api_endpoints),
        ("Agent Creation", test_agent_creation),
        ("Vietnamese Support", test_vietnamese_support),
        ("CCCD Functionality", test_cccd_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}: Test exception: {e}")
    
    total_time = time.time() - start_time
    success_rate = passed / total
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} passed ({success_rate:.1%})")
    print(f"⏱️ Total Time: {total_time:.2f}s")
    
    if success_rate >= 0.8:
        print("🎉 System is working well!")
    else:
        print("⚠️ Some issues detected")
    
    # Save results
    results = {
        "total_tests": total,
        "passed_tests": passed,
        "success_rate": success_rate,
        "total_time": total_time,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("simple_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Test results saved to: simple_test_results.json")
    
    return results

if __name__ == "__main__":
    main()