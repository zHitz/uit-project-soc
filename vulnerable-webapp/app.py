#!/usr/bin/env python3
"""
Vulnerable Web Application for Brute Force Testing
This application is intentionally vulnerable for security testing purposes.
DO NOT USE IN PRODUCTION!
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import json
import requests
import logging
from datetime import datetime
import os
import hashlib
import time

app = Flask(__name__)
app.secret_key = 'vulnerable_secret_key_123'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory user database (vulnerable - no password hashing, weak passwords)
USERS = {
    'admin': 'admin123',
    'user': 'password123',
    'test': 'test123',
    'demo': 'demo123',
    'guest': 'guest123'
}

# Track login attempts for brute force detection
login_attempts = {}

def send_log_to_siem(event_type, username, ip_address, success, details=""):
    """Send security events to Logstash for SIEM monitoring"""
    try:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "username": username,
            "ip_address": ip_address,
            "success": success,
            "user_agent": request.headers.get('User-Agent', ''),
            "details": details,
            "source": "vulnerable-webapp",
            "severity": "high" if not success else "low"
        }
        
        # Send to Logstash
        requests.post('http://logstash:5044', 
                     json=log_data, 
                     headers={'Content-Type': 'application/json'},
                     timeout=5)
        
        # Also log locally
        logger.info(f"SIEM Event: {json.dumps(log_data)}")
        
    except Exception as e:
        logger.error(f"Failed to send log to SIEM: {e}")

def get_client_ip():
    """Get client IP address from Nginx proxy"""
    # Check for X-Real-IP header (set by Nginx)
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # Check for X-Forwarded-For header
    elif request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    # Fallback to remote address
    return request.remote_addr

@app.route('/')
def index():
    """Main page"""
    client_ip = get_client_ip()
    send_log_to_siem("page_access", "anonymous", client_ip, True, "Accessed main page")
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable Web Application</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d32f2f; text-align: center; }
            .warning { background: #ffebee; border: 1px solid #f44336; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { background: #2196f3; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
            button:hover { background: #1976d2; }
            .users { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .users h3 { margin-top: 0; color: #1976d2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔓 Vulnerable Web Application</h1>
            
            <div class="warning">
                <strong>⚠️ WARNING:</strong> This is a deliberately vulnerable application for security testing.
                <br>DO NOT USE IN PRODUCTION!
            </div>
            
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            
            <div class="users">
                <h3>Test Accounts:</h3>
                <ul>
                    <li><strong>admin</strong> / admin123</li>
                    <li><strong>user</strong> / password123</li>
                    <li><strong>test</strong> / test123</li>
                    <li><strong>demo</strong> / demo123</li>
                    <li><strong>guest</strong> / guest123</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666;">
                <p>All login attempts are logged for SIEM monitoring</p>
                <p>IP: {{ request.remote_addr }}</p>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint - vulnerable to brute force"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    client_ip = get_client_ip()
    
    # Track login attempts
    if client_ip not in login_attempts:
        login_attempts[client_ip] = {'count': 0, 'last_attempt': 0}
    
    login_attempts[client_ip]['count'] += 1
    login_attempts[client_ip]['last_attempt'] = time.time()
    
    # Check credentials
    if username in USERS and USERS[username] == password:
        # Successful login
        session['username'] = username
        session['logged_in'] = True
        
        send_log_to_siem("login_success", username, client_ip, True, 
                        f"Successful login - Attempt #{login_attempts[client_ip]['count']}")
        
        flash(f'Welcome {username}! Login successful.', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Failed login
        send_log_to_siem("login_failed", username, client_ip, False, 
                        f"Failed login attempt #{login_attempts[client_ip]['count']} - Invalid credentials")
        
        flash('Invalid username or password!', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page - requires authentication"""
    if not session.get('logged_in'):
        client_ip = get_client_ip()
        send_log_to_siem("unauthorized_access", "anonymous", client_ip, False, "Attempted to access dashboard without login")
        return redirect(url_for('index'))
    
    username = session.get('username', 'unknown')
    client_ip = get_client_ip()
    send_log_to_siem("dashboard_access", username, client_ip, True, "Accessed dashboard")
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Vulnerable Web App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #4caf50; text-align: center; }
            .success { background: #e8f5e8; border: 1px solid #4caf50; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .logout { background: #ffebee; border: 1px solid #f44336; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .logout a { color: #d32f2f; text-decoration: none; font-weight: bold; }
            .logout a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Welcome to Dashboard</h1>
            
            <div class="success">
                <strong>✅ Login Successful!</strong>
                <br>You are logged in as: <strong>{{ session.username }}</strong>
            </div>
            
            <div class="info">
                <h3>🔍 Security Testing Information:</h3>
                <ul>
                    <li>This application logs all activities to SIEM</li>
                    <li>Check Kibana for security events</li>
                    <li>Monitor for brute force attempts</li>
                    <li>Track failed login patterns</li>
                </ul>
            </div>
            
            <div class="logout">
                <a href="/logout">🚪 Logout</a>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666;">
                <p>Session ID: {{ session.get('username', 'N/A') }}</p>
                <p>IP: {{ request.remote_addr }}</p>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    """Logout endpoint"""
    username = session.get('username', 'unknown')
    client_ip = get_client_ip()
    
    send_log_to_siem("logout", username, client_ip, True, "User logged out")
    
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/api/users')
def api_users():
    """Vulnerable API endpoint - exposes user list"""
    client_ip = get_client_ip()
    send_log_to_siem("api_access", "anonymous", client_ip, True, "Accessed vulnerable API endpoint")
    
    return json.dumps({
        'users': list(USERS.keys()),
        'message': 'This endpoint is vulnerable - exposes user list'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return json.dumps({'status': 'healthy', 'service': 'vulnerable-webapp'})

if __name__ == '__main__':
    print("🚀 Starting Vulnerable Web Application...")
    print("⚠️  WARNING: This application is intentionally vulnerable!")
    print("📊 All activities will be logged to SIEM")
    print("🌐 Access the application at: http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 