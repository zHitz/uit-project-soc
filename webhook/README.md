# 🔗 Webhook Service cho IP Blocking

## Mô tả
Webhook service cho phép n8n và các hệ thống khác gửi requests để tự động quản lý IP blocking thông qua Nginx. Service này thay thế việc chạy script bằng tay và cung cấp API endpoints để tích hợp với SIEM.

## 🏗️ Kiến trúc

```
n8n → Webhook Service → IP Blocker Script → Nginx Configuration
```

## 🚀 Endpoints

### 1. **Health Check**
```
GET /health
```
Kiểm tra trạng thái service.

### 2. **IP Blocking Operations**
```
POST /webhook/ip-block
```
Thực hiện các thao tác IP blocking cơ bản.

**Headers:**
```
Authorization: Bearer your-secret-key-here
Content-Type: application/json
```

**Body:**
```json
{
  "action": "block|unblock|list|reload|status",
  "ip_address": "192.168.1.100"  // Required for block/unblock
}
```

### 3. **Auto-block based on SIEM Alerts**
```
POST /webhook/auto-block
```
Tự động block IP dựa trên alerts từ SIEM.

**Body:**
```json
{
  "ip_address": "192.168.1.100",
  "alert_type": "brute_force_attack",
  "severity": "high|medium|low",
  "attempt_count": 15,
  "details": "Multiple failed login attempts detected"
}
```

### 4. **Bulk Operations**
```
POST /webhook/bulk-operations
```
Thực hiện nhiều thao tác cùng lúc.

**Body:**
```json
{
  "operations": [
    {"action": "block", "ip_address": "192.168.1.100"},
    {"action": "unblock", "ip_address": "192.168.1.200"},
    {"action": "list"}
  ]
}
```

## 🔐 Bảo mật

### Authentication
Tất cả endpoints (trừ `/health`) yêu cầu Bearer token:
```
Authorization: Bearer your-secret-key-here
```

### Environment Variable
```bash
WEBHOOK_SECRET=your-secret-key-here
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "action": "block",
  "ip_address": "192.168.1.100",
  "output": "IP 192.168.1.100 has been blocked",
  "timestamp": "2025-08-06T13:45:30.123Z"
}
```

### Error Response
```json
{
  "success": false,
  "action": "block",
  "ip_address": "192.168.1.100",
  "error": "IP is already blocked",
  "timestamp": "2025-08-06T13:45:30.123Z"
}
```

## 🧪 Testing

### Sử dụng test script:
```bash
cd webhook
python3 test_webhook.py
```

### Test thủ công:
```bash
# Health check
curl http://localhost:8081/health

# Block IP
curl -X POST http://localhost:8081/webhook/ip-block \
  -H "Authorization: Bearer your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"action": "block", "ip_address": "192.168.1.100"}'

# List blocked IPs
curl -X POST http://localhost:8081/webhook/ip-block \
  -H "Authorization: Bearer your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"action": "list"}'
```

## 🔄 Tích hợp với n8n

### 1. **HTTP Request Node**
```
Method: POST
URL: http://webhook:8081/webhook/ip-block
Headers:
  Authorization: Bearer your-secret-key-here
  Content-Type: application/json
Body:
  {
    "action": "block",
    "ip_address": "{{ $json.ip_address }}"
  }
```

### 2. **Auto-block Workflow**
```
Trigger: SIEM Alert
→ Filter: High severity brute force
→ HTTP Request: POST /webhook/auto-block
→ Notification: Block result
```

### 3. **Bulk Operations Workflow**
```
Trigger: Scheduled
→ Get IP list from threat feed
→ HTTP Request: POST /webhook/bulk-operations
→ Log results to SIEM
```

## 📈 SIEM Integration

### Event Types
- `webhook_ip_operation`: Thao tác IP blocking thủ công
- `auto_block`: Tự động block IP
- `auto_block_skipped`: Bỏ qua auto-block
- `bulk_operation`: Thao tác bulk
- `webhook_unauthorized`: Truy cập trái phép
- `webhook_error`: Lỗi webhook

### Log Fields
```json
{
  "timestamp": "2025-08-06T13:45:30.123Z",
  "event_type": "webhook_ip_operation",
  "action": "block",
  "ip_address": "192.168.1.100",
  "success": true,
  "details": "IP 192.168.1.100 has been blocked",
  "source": "webhook-service",
  "severity": "medium"
}
```

## 🛠️ Configuration

### Environment Variables
```bash
WEBHOOK_SECRET=your-secret-key-here
LOGSTASH_URL=http://logstash:5044
NGINX_SCRIPT_PATH=/app/nginx/ip_blocker.sh
```

### Auto-block Conditions
Service sẽ tự động block IP khi:
- `severity = "high"` AND `alert_type` contains "brute_force"
- `alert_type` contains "failed_login_attempts" AND `attempt_count > 10`
- `alert_type` contains "suspicious_activity"

## 🔧 Troubleshooting

### Kiểm tra logs:
```bash
docker compose logs webhook
```

### Test connectivity:
```bash
# Test webhook service
curl http://localhost:8081/health

# Test IP blocker script
docker exec webhook /app/nginx/ip_blocker.sh list
```

### Common Issues:
1. **401 Unauthorized**: Kiểm tra WEBHOOK_SECRET
2. **500 Internal Error**: Kiểm tra IP blocker script
3. **Timeout**: Kiểm tra Nginx container

## 📝 Examples

### n8n Workflow Example
```javascript
// Trigger: SIEM Alert
{
  "ip_address": "192.168.1.100",
  "alert_type": "brute_force_attack",
  "severity": "high",
  "attempt_count": 15
}

// HTTP Request Node
{
  "url": "http://webhook:8081/webhook/auto-block",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer your-secret-key-here",
    "Content-Type": "application/json"
  },
  "body": {
    "ip_address": "{{ $json.ip_address }}",
    "alert_type": "{{ $json.alert_type }}",
    "severity": "{{ $json.severity }}",
    "attempt_count": "{{ $json.attempt_count }}"
  }
}
```

### Bulk Block from Threat Feed
```javascript
// HTTP Request Node
{
  "url": "http://webhook:8081/webhook/bulk-operations",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer your-secret-key-here",
    "Content-Type": "application/json"
  },
  "body": {
    "operations": [
      {"action": "block", "ip_address": "192.168.1.100"},
      {"action": "block", "ip_address": "192.168.1.200"},
      {"action": "block", "ip_address": "192.168.1.300"}
    ]
  }
}
```

## 🎯 Next Steps

1. **SSL/TLS**: Cấu hình HTTPS cho webhook
2. **Rate Limiting**: Thêm rate limiting cho webhook endpoints
3. **Audit Logging**: Log chi tiết tất cả operations
4. **Dashboard**: Tạo dashboard để monitor webhook activities
5. **Alerting**: Tích hợp với notification system 