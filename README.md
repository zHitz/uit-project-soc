# SOC Platform

A comprehensive Security Operations Center (SOC) platform built with Docker Compose, featuring the ELK stack, n8n workflow automation, and The Hive case management system.

## Services

### ELK Stack
- **Elasticsearch** (Port 9200): Search and analytics engine
- **Logstash** (Port 5044, 9600): Log processing pipeline
- **Kibana** (Port 5601): Data visualization and management

### Workflow Automation
- **n8n** (Port 5678): Workflow automation platform
  - Username: `admin`
  - Password: `admin123`

### Case Management
- **The Hive** (Port 9002): Security incident response platform
- **Cortex** (Port 9001): Threat intelligence and analysis platform
- **Cassandra** (Internal): Database for The Hive and Cortex

### Testing & Monitoring
- **Nginx Reverse Proxy** (Port 80): Reverse proxy with IP blocking
  - IP blocking using ngx_http_access_module
  - Rate limiting for login attempts
  - Security headers and logging
- **Webhook Service** (Port 8081): API for IP blocking automation
  - REST API endpoints for IP management
  - Auto-blocking based on SIEM alerts
  - Bulk operations support
  - Integration with n8n workflows
- **Vulnerable Web App** (Internal): Test application for brute force attacks
  - Username: admin, user, test, demo, guest
  - Password: admin123, password123, test123, demo123, guest123

## Quick Start

1. **Deploy the platform:**
   ```bash
   docker-compose up -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f [service-name]
   ```

4. **Access services:**
   - Kibana: http://localhost:5601
   - n8n: http://localhost:5678 (admin/admin123)
   - The Hive: http://localhost:9002
   - Cortex: http://localhost:9001
   - Vulnerable Web App: http://localhost:80 (via Nginx)
   - Webhook Service: http://localhost:8081/health

## Service Health Checks

All services include health checks. Monitor them with:
```bash
docker-compose ps
```

## Logging

View logs for all services:
```bash
docker-compose logs -f
```

View logs for specific service:
```bash
docker-compose logs -f elasticsearch
docker-compose logs -f kibana
docker-compose logs -f logstash
docker-compose logs -f n8n
docker-compose logs -f thehive
docker-compose logs -f cortex
```

## Troubleshooting

### Common Issues

1. **Elasticsearch not starting:**
   - Check available memory (requires at least 2GB)
   - Ensure ports 9200 and 9300 are available

2. **The Hive/Cortex connection issues:**
   - Wait for Cassandra to fully start (may take 2-3 minutes)
   - Check Cassandra logs: `docker-compose logs thehive-db`

3. **n8n not accessible:**
   - Verify port 5678 is not in use
   - Check n8n logs for startup issues

### Reset Platform

To completely reset the platform:
```bash
docker-compose down -v
docker-compose up -d
```

## Data Persistence

All data is persisted in Docker volumes:
- `elasticsearch_data`: Elasticsearch indices
- `n8n_data`: n8n workflows and data
- `thehive_db_data`: Cassandra database
- `thehive_data`: The Hive application data
- `cortex_data`: Cortex application data

## Security Notes

- This is a development setup with security disabled for Elasticsearch
- Default credentials are used for n8n
- For production use, enable security features and use strong passwords 