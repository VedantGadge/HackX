#!/usr/bin/env python3
"""
Quick test script for the FastAPI backend
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_status():
    """Test model status endpoint"""
    print("\nTesting /model-status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-status")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"✅ Gesture model loaded: {data.get('gesture_model_loaded')}")
        print(f"✅ Letter model loaded: {data.get('letter_model_loaded')}")
        print(f"✅ Gesture classes: {len(data.get('gesture_classes', []))}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_homepage():
    """Test homepage"""
    print("\nTesting / homepage...")
    try:
        response = requests.get(BASE_URL)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Content length: {len(response.text)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 50)
    print("FastAPI Backend Test Suite")
    print("=" * 50)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Model Status", test_model_status()))
    results.append(("Homepage", test_homepage()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + ("🎉 All tests passed!" if all_passed else "❌ Some tests failed"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
