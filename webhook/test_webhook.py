#!/usr/bin/env python3
"""
Test Script for Webhook Service
This script demonstrates how to use the webhook endpoints.
"""

import requests
import json
import time

# Configuration
WEBHOOK_BASE_URL = "http://localhost:8081"
WEBHOOK_SECRET = "s0me-s3cr3t-k3y"  # Change this to match your secret

def test_webhook(endpoint, data, description):
    """Test a webhook endpoint"""
    print(f"\n🧪 Testing: {description}")
    print("=" * 50)
    
    url = f"{WEBHOOK_BASE_URL}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEBHOOK_SECRET}'
    }
    
    try:
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Webhook Service Test")
    print("=" * 60)
    
    # Test health first
    if not test_health():
        print("❌ Health check failed. Is the webhook service running?")
        return
    
    print("✅ Health check passed!")
    
    # Test 1: Block an IP
    test_webhook(
        "/webhook/ip-block",
        {
            "action": "block",
            "ip_address": "192.168.1.250"
        },
        "Block IP Address"
    )
    
    # Test 2: List blocked IPs
    test_webhook(
        "/webhook/ip-block",
        {
            "action": "list"
        },
        "List Blocked IPs"
    )
    
    # Test 3: Auto-block based on SIEM alert
    test_webhook(
        "/webhook/auto-block",
        {
            "ip_address": "192.168.1.251",
            "alert_type": "brute_force_attack",
            "severity": "high",
            "attempt_count": 15,
            "details": "Multiple failed login attempts detected"
        },
        "Auto-block based on SIEM Alert"
    )
    
    # Test 4: Bulk operations
    test_webhook(
        "/webhook/bulk-operations",
        {
            "operations": [
                {"action": "block", "ip_address": "192.168.1.252"},
                {"action": "block", "ip_address": "192.168.1.253"},
                {"action": "list"}
            ]
        },
        "Bulk Operations"
    )
    
    # Test 5: Unblock an IP
    test_webhook(
        "/webhook/ip-block",
        {
            "action": "unblock",
            "ip_address": "192.168.1.250"
        },
        "Unblock IP Address"
    )
    
    # Test 6: Invalid action
    test_webhook(
        "/webhook/ip-block",
        {
            "action": "invalid_action",
            "ip_address": "192.168.1.254"
        },
        "Invalid Action (should fail)"
    )
    
    # Test 7: Missing authorization
    print("\n🧪 Testing: Missing Authorization")
    print("=" * 40)
    
    try:
        response = requests.post(
            f"{WEBHOOK_BASE_URL}/webhook/ip-block",
            json={"action": "list"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n🎉 Webhook testing completed!")
    print("📊 Check the webhook service logs for detailed information")

if __name__ == "__main__":
    main() 