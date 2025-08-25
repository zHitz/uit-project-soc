# 🔓 Vulnerable Web Application - SIEM Testing

## Mô tả
Đây là một web application được thiết kế cố ý để dễ bị tấn công brute force, nhằm mục đích test và monitor SIEM (Security Information and Event Management).

## ⚠️ CẢNH BÁO
**KHÔNG SỬ DỤNG TRONG MÔI TRƯỜNG PRODUCTION!**
Ứng dụng này được thiết kế cố ý để dễ bị tấn công cho mục đích học tập và test SIEM.

## 🚀 Truy cập ứng dụng

### URL chính
- **Web Application**: http://localhost:8080
- **Kibana**: http://localhost:5601
- **API Endpoint**: http://localhost:8080/api/users
- **Health Check**: http://localhost:8080/health

### Tài khoản test
| Username | Password |
|----------|----------|
| admin | admin123 |
| user | password123 |
| test | test123 |
| demo | demo123 |
| guest | guest123 |

## 🔍 Tính năng

### 1. Login System
- Form đăng nhập cơ bản
- Không có rate limiting
- Không có captcha
- Dễ bị brute force

### 2. Logging System
- Ghi log tất cả hoạt động đăng nhập
- Gửi logs đến Logstash (port 5044)
- Track IP address, username, success/failure
- Severity levels cho SIEM

### 3. Vulnerable API
- Endpoint `/api/users` expose danh sách users
- Không có authentication
- Information disclosure vulnerability

## 🧪 Test Brute Force

### Sử dụng script có sẵn
```bash
cd vulnerable-webapp
python3 brute_force_test.py
```

### Test thủ công
```bash
# Test login thành công
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Test login thất bại
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=wrongpassword" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Test API endpoint
curl http://localhost:8080/api/users
```

### Sử dụng tools khác
```bash
# Hydra
hydra -L users.txt -P passwords.txt localhost http-post-form "/login:username=^USER^&password=^PASS^:Invalid"

# Nmap scripts
nmap --script http-brute -p 8080 localhost

# Burp Suite
# Import target: http://localhost:8080
# Use Intruder for brute force
```

## 📊 Monitor trong SIEM

### Kibana Dashboard
1. Truy cập Kibana: http://localhost:5601
2. Vào Discover
3. Tìm index pattern: `soc-logs-*`
4. Tạo dashboard với các metrics:
   - Failed login attempts
   - Successful logins
   - Brute force patterns
   - IP addresses

### Log Fields
```json
{
  "timestamp": "2025-08-06T12:35:37.123Z",
  "event_type": "login_failed",
  "username": "admin",
  "ip_address": "192.168.1.100",
  "success": false,
  "user_agent": "Mozilla/5.0...",
  "details": "Failed login attempt #15 - Invalid credentials",
  "source": "vulnerable-webapp",
  "severity": "high"
}
```

### Event Types
- `login_success`: Đăng nhập thành công
- `login_failed`: Đăng nhập thất bại
- `page_access`: Truy cập trang
- `dashboard_access`: Truy cập dashboard
- `unauthorized_access`: Truy cập trái phép
- `logout`: Đăng xuất
- `api_access`: Truy cập API

## 🛡️ Security Testing Scenarios

### 1. Brute Force Attack
```bash
# Tạo file users.txt
echo -e "admin\nuser\ntest\ndemo\nguest" > users.txt

# Tạo file passwords.txt
echo -e "admin123\npassword123\ntest123\ndemo123\nguest123\npassword\n123456" > passwords.txt

# Chạy brute force
python3 brute_force_test.py
```

### 2. Information Disclosure
```bash
# Test API endpoint
curl http://localhost:8080/api/users

# Test health endpoint
curl http://localhost:8080/health
```

### 3. Session Management
```bash
# Test session hijacking
# Sử dụng Burp Suite để capture và replay requests
```

## 📈 SIEM Alerts

### Tạo alerts trong Kibana
1. **Brute Force Detection**:
   - Trigger: >10 failed logins từ cùng IP trong 5 phút
   - Severity: High

2. **Successful Brute Force**:
   - Trigger: Login thành công sau nhiều lần thất bại
   - Severity: Critical

3. **API Abuse**:
   - Trigger: Nhiều requests đến `/api/users`
   - Severity: Medium

### Elasticsearch Queries
```json
// Failed logins per IP
GET soc-logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"event_type": "login_failed"}},
        {"range": {"timestamp": {"gte": "now-5m"}}}
      ]
    }
  },
  "aggs": {
    "ips": {
      "terms": {"field": "ip_address"},
      "aggs": {
        "count": {"value_count": {"field": "ip_address"}}
      }
    }
  }
}
```

## 🔧 Troubleshooting

### Kiểm tra logs
```bash
# Container logs
docker compose logs vulnerable-webapp

# Logstash logs
docker compose logs logstash

# Elasticsearch logs
docker compose logs elasticsearch
```

### Kiểm tra connectivity
```bash
# Test web app
curl http://localhost:8080/health

# Test Logstash
curl http://localhost:9600

# Test Elasticsearch
curl http://localhost:9200/_cluster/health
```

## 📝 Notes
- Tất cả logs được gửi đến Logstash qua HTTP POST
- Logs được index vào Elasticsearch với pattern `soc-logs-YYYY.MM.DD`
- Web application restart sẽ reset session và login attempts counter
- Không có persistent storage cho user sessions

## 🎯 Next Steps
1. Tạo Kibana dashboard cho security monitoring
2. Thiết lập alerts cho brute force detection
3. Tích hợp với The Hive cho incident response
4. Sử dụng n8n để automate response actions 