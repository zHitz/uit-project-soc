#!/bin/bash

# Webhook Service Test Script using curl
# This script tests all webhook endpoints

# Configuration
WEBHOOK_BASE_URL="http://localhost:8081"
WEBHOOK_SECRET="s0me-s3cr3t-k3y"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Webhook Service Test with curl${NC}"
echo "============================================================"

# Test 1: Health Check
echo -e "\n${YELLOW}🏥 Test 1: Health Check${NC}"
echo "=============================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X GET "${WEBHOOK_BASE_URL}/health" \
  -H "Content-Type: application/json" | jq '.'

# Test 2: Block IP Address
echo -e "\n${YELLOW}🧪 Test 2: Block IP Address${NC}"
echo "================================"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "block",
    "ip_address": "192.168.1.300"
  }' | jq '.'

# Test 3: List Blocked IPs
echo -e "\n${YELLOW}🧪 Test 3: List Blocked IPs${NC}"
echo "================================"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list"
  }' | jq '.'

# Test 4: Auto-block based on SIEM Alert
echo -e "\n${YELLOW}🧪 Test 4: Auto-block based on SIEM Alert${NC}"
echo "================================================"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/auto-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.310",
    "alert_type": "brute_force_attack",
    "severity": "high",
    "attempt_count": 15,
    "details": "Multiple failed login attempts detected"
  }' | jq '.'

# Test 5: Auto-block with medium severity (should skip)
echo -e "\n${YELLOW}🧪 Test 5: Auto-block with Medium Severity (should skip)${NC}"
echo "========================================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/auto-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.320",
    "alert_type": "suspicious_activity",
    "severity": "medium",
    "attempt_count": 5,
    "details": "Suspicious activity detected"
  }' | jq '.'

# Test 6: Bulk Operations
echo -e "\n${YELLOW}🧪 Test 6: Bulk Operations${NC}"
echo "================================"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/bulk-operations" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [
      {"action": "block", "ip_address": "192.168.1.330"},
      {"action": "block", "ip_address": "192.168.1.340"},
      {"action": "list"}
    ]
  }' | jq '.'

# Test 7: Unblock IP Address
echo -e "\n${YELLOW}🧪 Test 7: Unblock IP Address${NC}"
echo "=================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "unblock",
    "ip_address": "192.168.1.300"
  }' | jq '.'

# Test 8: Invalid Action (should fail)
echo -e "\n${YELLOW}🧪 Test 8: Invalid Action (should fail)${NC}"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "invalid_action",
    "ip_address": "192.168.1.350"
  }' | jq '.'

# Test 9: Missing IP Address (should fail)
echo -e "\n${YELLOW}🧪 Test 9: Missing IP Address (should fail)${NC}"
echo "============================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "block"
  }' | jq '.'

# Test 10: Invalid IP Format (should fail)
echo -e "\n${YELLOW}🧪 Test 10: Invalid IP Format (should fail)${NC}"
echo "============================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "block",
    "ip_address": "192.168.1.400"
  }' | jq '.'

# Test 11: Missing Authorization (should fail)
echo -e "\n${YELLOW}🧪 Test 11: Missing Authorization (should fail)${NC}"
echo "==============================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list"
  }' | jq '.'

# Test 12: Wrong Authorization Token (should fail)
echo -e "\n${YELLOW}🧪 Test 12: Wrong Authorization Token (should fail)${NC}"
echo "=================================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer wrong-token" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list"
  }' | jq '.'

# Test 13: Nginx Status
echo -e "\n${YELLOW}🧪 Test 13: Nginx Status${NC}"
echo "================================"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "status"
  }' | jq '.'

# Test 14: Reload Nginx Configuration
echo -e "\n${YELLOW}🧪 Test 14: Reload Nginx Configuration${NC}"
echo "=========================================="
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reload"
  }' | jq '.'

# Final List to see all blocked IPs
echo -e "\n${YELLOW}📋 Final List of Blocked IPs${NC}"
echo "================================"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "${WEBHOOK_BASE_URL}/webhook/ip-block" \
  -H "Authorization: Bearer ${WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "list"
  }' | jq '.'

echo -e "\n${GREEN}🎉 Webhook testing completed!${NC}"
echo -e "${BLUE}📊 Check the webhook service logs for detailed information${NC}" 