# SkyOne Shuge 部署方案 v0.6

## 1. 部署架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                          部署架构                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     用户设备 (Client)                        │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐          │   │
│  │  │   Web     │  │  Desktop  │  │   CLI     │          │   │
│  │  │  (浏览器)  │  │ (Tauri)   │  │  (本地)   │          │   │
│  │  └───────────┘  └───────────┘  └───────────┘          │   │
│  │                                                             │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │              本地服务 (Local Service)                │  │   │
│  │  │     FastAPI + SQLite + Qdrant (可选)               │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│                              │                                       │
│                         HTTPS/TLS                                    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    云端服务 (Server - 可选)                  │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              负载均衡 (Nginx)                       │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │  API #1     │  │  API #2     │  │  API #3     │    │   │
│  │  │ (K8s Pod)   │  │ (K8s Pod)   │  │ (K8s Pod)   │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              Redis (缓存/队列)                    │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │  ┌───────────────────┐  ┌───────────────────────────┐│   │
│  │  │   PostgreSQL      │  │        Qdrant             ││   │
│  │  │   (主从)          │  │      (向量数据库)          ││   │
│  │  └───────────────────┘  └───────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 部署模式

### 2.1 模式对比

| 模式 | 说明 | 适用场景 | 同步 |
|-----|------|---------|------|
| **纯本地** | 所有服务本地运行 | 个人使用 | 无需网络 |
| **本地+云端 API** | 本地存储 + 云端 AI | 需要 AI 能力 | 可选 |
| **全云端** | 全部云端运行 | 团队协作 | 自动 |

### 2.2 推荐配置

**个人用户 (MVP)**:
```
┌────────────────────────────────────┐
│  本地设备                           │
│  ├── FastAPI (CLI)                 │
│  ├── SQLite                        │
│  ├── Qdrant (可选, 向量搜索)       │
│  └── 用户浏览器访问 localhost        │
└────────────────────────────────────┘
```

**团队/企业**:
```
┌────────────────────────────────────┐
│  云端服务器                          │
│  ├── Nginx (负载均衡)               │
│  ├── FastAPI x 3 (高可用)          │
│  ├── PostgreSQL (主从)              │
│  ├── Qdrant Cluster               │
│  └── Redis (缓存/队列)             │
│                                     │
│  本地设备                           │
│  ├── Desktop App (Tauri)          │
│  └── CLI 工具                      │
└────────────────────────────────────┘
```

---

## 3. Docker 部署

### 3.1 docker-compose.yml

```yaml
version: '3.8'

services:
  # API 服务
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    image: skyone-shuge/api:latest
    container_name: skyone-api
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://skyone:skyone@postgres:5432/skyone
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - API_HOST=0.0.0.0
      - API_PORT=8080
      - LOG_LEVEL=INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
      qdrant:
        condition: service_started
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/indexes:/app/indexes
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  worker:
    build:
      context: ./api
      dockerfile: Dockerfile
    image: skyone-shuge/api:latest
    container_name: skyone-worker
    command: celery -A app.worker worker -l info
    environment:
      - DATABASE_URL=postgresql://skyone:skyone@postgres:5432/skyone
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/indexes:/app/indexes
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: skyone-postgres
    environment:
      - POSTGRES_DB=skyone
      - POSTGRES_USER=skyone
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-skyone123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-spoint-initdb.dcripts:/docker-entry
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U skyone -d skyone"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: skyone-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Qdrant (向量数据库)
  qdrant:
    image: qdrant/qdrant:latest
    container_name: skyone-qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/collections"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx (反向代理 + 静态资源)
  nginx:
    image: nginx:alpine
    container_name: skyone-nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./data/uploads:/var/www/uploads:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  qdrant_data:

networks:
  default:
    name: skyone-network
```

### 3.2 API Dockerfile

```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 安装 Python 依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
```

### 3.3 nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;

    # 上传文件大小限制
    client_max_body_size 100M;

    # API 服务
    upstream api_servers {
        server api:8080 weight=5;
        keepalive 32;
    }

    server {
        listen 80;
        server_name localhost;

        # 健康检查
        location /health {
            proxy_pass http://api_servers/health;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }

        # API 路由
        location /api/ {
            proxy_pass http://api_servers/api/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket 支持
        location /ws/ {
            proxy_pass http://api_servers/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # 静态资源
        location /static/ {
            alias /usr/share/nginx/html/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # 前端 SPA
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
    }
}
```

---

## 4. Kubernetes 部署

### 4.1 namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: skyone-shuge
  labels:
    app: skyone-shuge
```

### 4.2 deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: skyone-api
  namespace: skyone-shuge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: skyone-api
  template:
    metadata:
      labels:
        app: skyone-api
    spec:
      containers:
      - name: api
        image: skyone-shuge/api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: skyone-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: skyone-secrets
              key: redis-url
        - name: QDRANT_URL
          valueFrom:
            configMapKeyRef:
              name: skyone-config
              key: qdrant-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: skyone-api
  namespace: skyone-shuge
spec:
  selector:
    app: skyone-api
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### 4.3 ingress.yaml

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: skyone-ingress
  namespace: skyone-shuge
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
spec:
  tls:
  - hosts:
    - api.skyoneshuge.com
    secretName: skyone-tls
  rules:
  - host: api.skyoneshuge.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: skyone-api
            port:
              number: 80
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: skyone-api
            port:
              number: 80
```

---

## 5. 监控与日志

### 5.1 Prometheus 配置

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: skyone-monitor
  namespace: skyone-shuge
spec:
  selector:
    matchLabels:
      app: skyone-api
  endpoints:
  - port: metrics
    path: /metrics
    interval: 15s
```

### 5.2 日志聚合 (ELK)

```yaml
# fluent-bit 配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: skyone-shuge
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         5
        Log_Level     info
        Daemon        off
        Parsers_File  parsers.conf
        HTTP_Server   On
        HTTP_Listen   0.0.0.0
        HTTP_Port     2020

    [INPUT]
        Name              tail
        Path              /var/log/containers/*skyone*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        Mem_Buf_Limit     50MB

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix     kube.var.log.containers.

    [OUTPUT]
        Name            es
        Match           *
        Host            elasticsearch.logging.svc
        Port            9200
        Index           skyone-logs
        Type            _doc
```

---

## 6. 备份策略

### 6.1 数据库备份

```bash
#!/bin/bash
# backup.sh - 数据库备份脚本

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="skyone-postgres"

# 创建备份
docker exec $DB_CONTAINER pg_dump -U skyone skyone > "$BACKUP_DIR/skyone_$DATE.sql"

# 压缩
gzip "$BACKUP_DIR/skyone_$DATE.sql"

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

# 同步到对象存储 (可选)
# aws s3 cp $BACKUP_DIR/skyone_$DATE.sql.gz s3://skyone-backups/

echo "备份完成: skyone_$DATE.sql.gz"
```

### 6.2 定时任务 (Cron)

```bash
# /etc/cron.d/skyone-backup
# 每天凌晨 2 点执行备份
0 2 * * * root /opt/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## 7. 环境配置

### 7.1 环境变量模板

```bash
# .env.production

# 数据库
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://skyone:your_secure_password_here@postgres:5432/skyone

# Redis
REDIS_URL=redis://redis:6379

# Qdrant
QDRANT_URL=http://qdrant:6333

# API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx

# 安全
SECRET_KEY=your-secret-key-min-32-chars
ALLOWED_ORIGINS=https://your-domain.com

# 邮件
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=qun.xitang.du@gmail.com
SMTP_PASSWORD=your_app_password

# 监控
METRICS_ENABLED=true
```

---

## 8. 部署检查清单

### 部署前
- [ ] 配置域名 DNS
- [ ] 申请 SSL 证书
- [ ] 配置环境变量
- [ ] 创建数据库
- [ ] 准备备份恢复方案

### 部署中
- [ ] 启动基础设施 (PostgreSQL, Redis, Qdrant)
- [ ] 启动 API 服务
- [ ] 配置 Nginx
- [ ] 设置健康检查
- [ ] 验证服务状态

### 部署后
- [ ] 执行冒烟测试
- [ ] 配置监控告警
- [ ] 设置日志聚合
- [ ] 验证备份恢复
- [ ] 更新文档

---

**版本**: v0.6
**日期**: 2026-02-03
**主题**: 部署方案设计
