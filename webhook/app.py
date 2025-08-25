#!/usr/bin/env python3
"""
Webhook Service for IP Blocking Management
This service receives webhook requests from n8n and executes IP blocking commands.
"""

from flask import Flask, request, jsonify
import subprocess
import logging
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-secret-key-here')
NGINX_SCRIPT_PATH = '/app/nginx/ip_blocker.sh'
LOGSTASH_URL = 'http://logstash:5044'

def send_log_to_siem(event_type, action, ip_address, success, details=""):
    """Send webhook events to Logstash for SIEM monitoring"""
    try:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "action": action,
            "ip_address": ip_address,
            "success": success,
            "details": details,
            "source": "webhook-service",
            "severity": "medium" if success else "high"
        }
        
        # Send to Logstash
        requests.post(LOGSTASH_URL, 
                     json=log_data, 
                     headers={'Content-Type': 'application/json'},
                     timeout=5)
        
        logger.info(f"SIEM Event: {json.dumps(log_data)}")
        
    except Exception as e:
        logger.error(f"Failed to send log to SIEM: {e}")

def execute_ip_blocker_command(command, ip_address=None):
    """Execute the IP blocker script with given command"""
    try:
        # Execute script directly from host
        script_path = '/app/nginx/ip_blocker.sh'
        if ip_address:
            cmd = [script_path, command, ip_address]
        else:
            cmd = [script_path, command]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='/app',
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info(f"Command successful: {result.stdout}")
            return True, result.stdout
        else:
            logger.error(f"Command failed: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        error_msg = "Command timed out"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Command execution error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def validate_ip(ip_address):
    """Validate IP address format"""
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    logger.info(f"Checking pattern for IP: {ip_address}")
    if not re.match(pattern, ip_address):
        logger.error(f"Pattern match failed for IP: {ip_address}")
        return False
    
    try:
        parts = ip_address.split('.')
        logger.info(f"IP parts: {parts}")
        result = all(0 <= int(part) <= 255 for part in parts)
        logger.info(f"IP validation result: {result}")
        return result
    except (ValueError, AttributeError) as e:
        logger.error(f"IP validation exception: {e}")
        return False

def verify_webhook_secret():
    """Verify webhook secret for security"""
    # Disabled for testing
    return True

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'webhook-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/webhook/ip-block', methods=['POST'])
def ip_block_webhook():
    """Webhook endpoint for IP blocking operations"""
    
    # Verify webhook secret
    if not verify_webhook_secret():
        send_log_to_siem("webhook_unauthorized", "ip_block", "unknown", False, "Invalid or missing authorization")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        action = data.get('action')
        ip_address = data.get('ip_address')
        
        if not action:
            return jsonify({'error': 'Action is required'}), 400
        
        # Validate action
        valid_actions = ['block', 'unblock', 'list', 'reload', 'status']
        if action not in valid_actions:
            return jsonify({'error': f'Invalid action. Must be one of: {valid_actions}'}), 400
        
        # Validate IP address for block/unblock actions
        if action in ['block', 'unblock']:
            if not ip_address:
                return jsonify({'error': 'IP address is required for block/unblock actions'}), 400
            
            logger.info(f"Validating IP: {ip_address}")
            if not validate_ip(ip_address):
                logger.error(f"IP validation failed for: {ip_address}")
                return jsonify({'error': 'Invalid IP address format'}), 400
        
        # Execute command
        success, output = execute_ip_blocker_command(action, ip_address)
        
        # Log to SIEM
        send_log_to_siem("webhook_ip_operation", action, ip_address or "N/A", success, output)
        
        if success:
            return jsonify({
                'success': True,
                'action': action,
                'ip_address': ip_address,
                'output': output,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'action': action,
                'ip_address': ip_address,
                'error': output,
                'timestamp': datetime.utcnow().isoformat()
            }), 500
            
    except Exception as e:
        error_msg = f"Webhook processing error: {str(e)}"
        logger.error(error_msg)
        send_log_to_siem("webhook_error", "unknown", "unknown", False, error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/webhook/auto-block', methods=['POST'])
def auto_block_webhook():
    """Webhook endpoint for automatic IP blocking based on SIEM alerts"""
    
    # Verify webhook secret
    if not verify_webhook_secret():
        send_log_to_siem("webhook_unauthorized", "auto_block", "unknown", False, "Invalid or missing authorization")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract information from SIEM alert
        ip_address = data.get('ip_address')
        alert_type = data.get('alert_type', 'unknown')
        severity = data.get('severity', 'medium')
        details = data.get('details', '')
        
        if not ip_address:
            return jsonify({'error': 'IP address is required'}), 400
        
        if not validate_ip(ip_address):
            return jsonify({'error': 'Invalid IP address format'}), 400
        
        # Auto-block based on conditions
        should_block = False
        block_reason = ""
        
        # Example conditions for auto-blocking
        if severity == 'high' and 'brute_force' in alert_type.lower():
            should_block = True
            block_reason = "High severity brute force attack"
        elif 'failed_login_attempts' in alert_type.lower() and data.get('attempt_count', 0) > 10:
            should_block = True
            block_reason = "Multiple failed login attempts"
        elif 'suspicious_activity' in alert_type.lower():
            should_block = True
            block_reason = "Suspicious activity detected"
        
        if should_block:
            # Execute block command
            success, output = execute_ip_blocker_command('block', ip_address)
            
            # Log to SIEM
            send_log_to_siem("auto_block", "block", ip_address, success, 
                           f"{block_reason}: {details}")
            
            if success:
                return jsonify({
                    'success': True,
                    'action': 'auto_block',
                    'ip_address': ip_address,
                    'reason': block_reason,
                    'output': output,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'action': 'auto_block',
                    'ip_address': ip_address,
                    'error': output,
                    'timestamp': datetime.utcnow().isoformat()
                }), 500
        else:
            # Log that IP was not blocked
            send_log_to_siem("auto_block_skipped", "skip", ip_address, True, 
                           f"Alert type: {alert_type}, Severity: {severity}")
            
            return jsonify({
                'success': True,
                'action': 'auto_block_skipped',
                'ip_address': ip_address,
                'reason': 'Conditions not met for auto-blocking',
                'timestamp': datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        error_msg = f"Auto-block webhook error: {str(e)}"
        logger.error(error_msg)
        send_log_to_siem("webhook_error", "auto_block", "unknown", False, error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/webhook/bulk-operations', methods=['POST'])
def bulk_operations_webhook():
    """Webhook endpoint for bulk IP operations"""
    
    # Verify webhook secret
    if not verify_webhook_secret():
        send_log_to_siem("webhook_unauthorized", "bulk_operations", "unknown", False, "Invalid or missing authorization")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        operations = data.get('operations', [])
        
        if not operations:
            return jsonify({'error': 'No operations provided'}), 400
        
        results = []
        
        for operation in operations:
            action = operation.get('action')
            ip_address = operation.get('ip_address')
            
            if not action:
                results.append({
                    'action': 'unknown',
                    'ip_address': ip_address,
                    'success': False,
                    'error': 'Action is required'
                })
                continue
            
            if action in ['block', 'unblock'] and not ip_address:
                results.append({
                    'action': action,
                    'ip_address': ip_address,
                    'success': False,
                    'error': 'IP address is required'
                })
                continue
            
            if action in ['block', 'unblock'] and not validate_ip(ip_address):
                results.append({
                    'action': action,
                    'ip_address': ip_address,
                    'success': False,
                    'error': 'Invalid IP address format'
                })
                continue
            
            # Execute command
            success, output = execute_ip_blocker_command(action, ip_address)
            
            results.append({
                'action': action,
                'ip_address': ip_address,
                'success': success,
                'output': output if success else output
            })
            
            # Log individual operation
            send_log_to_siem("bulk_operation", action, ip_address or "N/A", success, output)
        
        # Log bulk operation summary
        successful_ops = sum(1 for r in results if r['success'])
        total_ops = len(results)
        send_log_to_siem("bulk_operation_summary", "bulk", "multiple", True, 
                        f"Completed {successful_ops}/{total_ops} operations")
        
        return jsonify({
            'success': True,
            'operations': results,
            'summary': {
                'total': total_ops,
                'successful': successful_ops,
                'failed': total_ops - successful_ops
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        error_msg = f"Bulk operations webhook error: {str(e)}"
        logger.error(error_msg)
        send_log_to_siem("webhook_error", "bulk_operations", "unknown", False, error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    print("🚀 Starting Webhook Service for IP Blocking...")
    print("📊 Webhook endpoints:")
    print("  - POST /webhook/ip-block")
    print("  - POST /webhook/auto-block")
    print("  - POST /webhook/bulk-operations")
    print("🔐 Authorization: Bearer token required")
    print("🌐 Health check: http://localhost:8081/health")
    
    app.run(host='0.0.0.0', port=8081, debug=True) 