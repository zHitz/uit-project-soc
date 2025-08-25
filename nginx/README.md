# 🛡️ Nginx Reverse Proxy với IP Blocking

## Mô tả
Nginx được cấu hình như một reverse proxy trước ứng dụng Python, sử dụng module `ngx_http_access_module` để chặn IP và cung cấp các tính năng bảo mật bổ sung.

## 🏗️ Kiến trúc

```
Internet → Nginx (Port 80) → Vulnerable Web App (Port 8080)
```

## ⚙️ Cấu hình

### Files chính:
- `nginx.conf` - Cấu hình Nginx chính
- `conf.d/vulnerable-webapp.conf` - Virtual host cho web application
- `ip_blocker.sh` - Script quản lý IP blocking

### Tính năng bảo mật:

#### 1. **IP Blocking (ngx_http_access_module)**
```nginx
geo $blocked_ip {
    default 0;
    192.168.1.100 1;  # IP bị chặn
    10.0.0.50 1;      # IP bị chặn
}

if ($blocked_ip) {
    return 403;
}
```

#### 2. **Rate Limiting**
```nginx
# Login attempts: 10 requests/minute
limit_req_zone $binary_remote_addr zone=login:10m rate=10r/m;

# API requests: 30 requests/minute  
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
```

#### 3. **Security Headers**
```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
```

## 🚀 Sử dụng

### Truy cập ứng dụng:
- **URL**: http://localhost:80
- **Health Check**: http://localhost/health
- **API**: http://localhost/api/users

### Quản lý IP Blocking:

#### 1. **Block một IP:**
```bash
./nginx/ip_blocker.sh block 192.168.1.100
```

#### 2. **Unblock một IP:**
```bash
./nginx/ip_blocker.sh unblock 192.168.1.100
```

#### 3. **Xem danh sách IP bị block:**
```bash
./nginx/ip_blocker.sh list
```

#### 4. **Reload cấu hình Nginx:**
```bash
./nginx/ip_blocker.sh reload
```

#### 5. **Kiểm tra trạng thái Nginx:**
```bash
./nginx/ip_blocker.sh status
```

## 📊 Logging

### Log Files:
- `/var/log/nginx/access.log` - Access logs chuẩn
- `/var/log/nginx/security.log` - Security logs với thông tin IP blocking
- `/var/log/nginx/error.log` - Error logs

### Log Format Security:
```
$remote_addr - $remote_user [$time_local] "$request" 
$status $body_bytes_sent "$http_referer" 
"$http_user_agent" "$http_x_forwarded_for" 
blocked:$blocked_ip allowed:$allowed_ip
```

## 🧪 Testing

### 1. **Test IP Blocking:**
```bash
# Block một IP
./nginx/ip_blocker.sh block 192.168.1.200

# Test từ IP bị block (sẽ nhận 403)
curl -H "X-Forwarded-For: 192.168.1.200" http://localhost/
```

### 2. **Test Rate Limiting:**
```bash
# Test rate limiting cho login
for i in {1..15}; do
  curl -X POST http://localhost/login \
    -d "username=admin&password=wrong" \
    -H "Content-Type: application/x-www-form-urlencoded"
done
```

### 3. **Test Brute Force qua Nginx:**
```bash
cd vulnerable-webapp
python3 brute_force_test.py
```

## 🔧 Troubleshooting

### Kiểm tra cấu hình Nginx:
```bash
docker exec nginx nginx -t
```

### Xem logs Nginx:
```bash
docker compose logs nginx
```

### Restart Nginx:
```bash
docker compose restart nginx
```

### Kiểm tra connectivity:
```bash
# Test từ host
curl http://localhost/health

# Test từ container
docker exec nginx wget -q -O- http://vulnerable-webapp:8080/health
```

## 📈 Monitoring

### 1. **Nginx Metrics:**
- Request rate
- Error rate (4xx, 5xx)
- Response time
- Blocked requests

### 2. **Security Events:**
- Blocked IPs
- Rate limit violations
- Failed login attempts
- Unauthorized access

### 3. **SIEM Integration:**
Nginx logs được gửi đến Logstash qua filebeat hoặc syslog forwarding.

## 🛠️ Advanced Configuration

### 1. **Whitelist IPs:**
```nginx
geo $allowed_ip {
    default 0;
    192.168.1.10 1;  # IP được phép
}

if ($allowed_ip = 0) {
    return 403;
}
```

### 2. **Custom Rate Limiting:**
```nginx
# Tùy chỉnh rate limit cho từng endpoint
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

### 3. **SSL/TLS:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
}
```

## 🔒 Security Best Practices

1. **Regular Updates**: Cập nhật Nginx thường xuyên
2. **Log Monitoring**: Monitor logs để phát hiện attacks
3. **IP Reputation**: Sử dụng IP reputation lists
4. **WAF Integration**: Tích hợp Web Application Firewall
5. **SSL/TLS**: Sử dụng HTTPS trong production

## 📝 Notes

- Nginx reload không làm gián đoạn service
- IP blocking có hiệu lực ngay lập tức
- Rate limiting được áp dụng per IP
- Logs được rotate tự động
- Configuration được mount từ host

## 🎯 Next Steps

1. **SSL/TLS Setup**: Cấu hình HTTPS
2. **WAF Integration**: Tích hợp ModSecurity
3. **Load Balancing**: Cấu hình multiple backend servers
4. **Monitoring**: Setup Prometheus + Grafana
5. **Automation**: Tích hợp với SIEM cho auto-blocking 