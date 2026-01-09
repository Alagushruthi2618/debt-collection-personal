# backend/test_api.py

"""
Simple test script to verify the backend API works.
Run this after starting the server to test the endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_init():
    """Test session initialization."""
    print("Testing /api/init endpoint...")
    response = requests.post(
        f"{BASE_URL}/api/init",
        json={"phone": "+919876543210"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}\n")
    return data.get("session_id")


def test_chat(session_id, user_input):
    """Test chat endpoint."""
    print(f"Testing /api/chat endpoint with input: '{user_input}'...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "session_id": session_id,
            "user_input": user_input
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}\n")
        return data
    else:
        print(f"Error: {response.text}\n")
        return None


if __name__ == "__main__":
    print("=" * 50)
    print("Backend API Test")
    print("=" * 50)
    print()
    
    # Test health
    test_health()
    
    # Test init
    session_id = test_init()
    if not session_id:
        print("Failed to initialize session. Exiting.")
        exit(1)
    
    # Test chat flow
    test_chat(session_id, "Yes, this is Rajesh")
    test_chat(session_id, "15-03-1985")
    test_chat(session_id, "I want a payment plan")
    
    print("=" * 50)
    print("Test completed!")
    print("=" * 50)

