#!/bin/bash

# IP Blocker Script for Nginx
# This script manages IP blocking using ngx_http_access_module

NGINX_CONF_DIR="/etc/nginx/conf.d"
CONTAINER_NAME="nginx"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [IP_ADDRESS]"
    echo ""
    echo "Commands:"
    echo "  block <ip>     - Block an IP address"
    echo "  unblock <ip>   - Unblock an IP address"
    echo "  list           - List all blocked IPs"
    echo "  reload         - Reload Nginx configuration"
    echo "  status         - Show Nginx status"
    echo ""
    echo "Examples:"
    echo "  $0 block 192.168.1.100"
    echo "  $0 unblock 192.168.1.100"
    echo "  $0 list"
}

# Function to block an IP
block_ip() {
    local ip=$1
    
    if [[ -z "$ip" ]]; then
        echo -e "${RED}Error: IP address is required${NC}"
        show_usage
        exit 1
    fi
    
    # Validate IP format
    if ! [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo -e "${RED}Error: Invalid IP address format${NC}"
        exit 1
    fi
    
    # Check if IP is already blocked
    if grep -q "$ip" nginx/conf.d/vulnerable-webapp.conf; then
        echo -e "${YELLOW}IP $ip is already blocked${NC}"
        return
    fi
    
    # Add IP to blacklist
    sed -i "/# Add IPs to block here/a\    $ip 1;  # Blocked by script" nginx/conf.d/vulnerable-webapp.conf
    
    echo -e "${GREEN}IP $ip has been blocked${NC}"
    
    # Reload Nginx (skip if nginx not available)
    if command -v nginx >/dev/null 2>&1; then
        reload_nginx
    else
        echo -e "${YELLOW}Nginx reload skipped (nginx not available)${NC}"
    fi
}

# Function to unblock an IP
unblock_ip() {
    local ip=$1
    
    if [[ -z "$ip" ]]; then
        echo -e "${RED}Error: IP address is required${NC}"
        show_usage
        exit 1
    fi
    
    # Check if IP is blocked
    if ! grep -q "$ip" nginx/conf.d/vulnerable-webapp.conf; then
        echo -e "${YELLOW}IP $ip is not blocked${NC}"
        return
    fi
    
    # Remove IP from blacklist
    sed -i "/$ip 1;.*# Blocked by script/d" nginx/conf.d/vulnerable-webapp.conf
    
    echo -e "${GREEN}IP $ip has been unblocked${NC}"
    
    # Reload Nginx (skip if nginx not available)
    if command -v nginx >/dev/null 2>&1; then
        reload_nginx
    else
        echo -e "${YELLOW}Nginx reload skipped (nginx not available)${NC}"
    fi
}

# Function to list blocked IPs
list_blocked_ips() {
    echo -e "${YELLOW}Blocked IP addresses:${NC}"
    echo "================================"
    
    # Extract blocked IPs from config
    grep -E "^[[:space:]]*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[[:space:]]+1;" nginx/conf.d/vulnerable-webapp.conf | \
    while read line; do
        ip=$(echo "$line" | awk '{print $1}')
        comment=$(echo "$line" | sed 's/.*# //')
        echo "  $ip - $comment"
    done
    
    echo ""
    echo -e "${YELLOW}Total blocked IPs:${NC} $(grep -c "^[[:space:]]*[0-9]" nginx/conf.d/vulnerable-webapp.conf)"
}

# Function to reload Nginx
reload_nginx() {
    echo -e "${YELLOW}Reloading Nginx configuration...${NC}"
    
    # Test configuration
    if nginx -t; then
        # Reload configuration
        nginx -s reload
        echo -e "${GREEN}Nginx configuration reloaded successfully${NC}"
    else
        echo -e "${RED}Error: Invalid Nginx configuration${NC}"
        exit 1
    fi
}

# Function to show Nginx status
show_status() {
    echo -e "${YELLOW}Nginx Status:${NC}"
    echo "=============="
    
    # Check if nginx is running
    if pgrep nginx > /dev/null; then
        echo -e "${GREEN}✓ Nginx is running${NC}"
        
        # Show nginx info
        echo ""
        echo "Nginx Info:"
        nginx -v
        
        # Show recent logs
        echo ""
        echo "Recent Logs:"
        tail -5 /var/log/nginx/error.log
    else
        echo -e "${RED}✗ Nginx is not running${NC}"
    fi
}

# Main script logic
case "$1" in
    "block")
        block_ip "$2"
        ;;
    "unblock")
        unblock_ip "$2"
        ;;
    "list")
        list_blocked_ips
        ;;
    "reload")
        reload_nginx
        ;;
    "status")
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 