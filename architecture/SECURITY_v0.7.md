# SkyOne Shuge 安全与隐私设计 v0.7

## 1. 安全架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SkyOne Shuge 安全架构                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     网络安全层                                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │  TLS    │ │  WAF    │ │  Rate   │ │  IP     │       │   │
│  │  │  加密   │ │  防护   │ │  限制   │ │  白名单 │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     应用安全层                                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │  认证   │ │  授权   │ │  输入   │ │  API    │       │   │
│  │  │  OAuth  │ │  RBAC   │ │  验证   │ │  安全   │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     数据安全层                                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │  加密   │ │  脱敏   │ │  备份   │ │  密钥   │       │   │
│  │  │  存储   │ │  处理   │ │  恢复   │ │  管理   │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 认证与授权

### 2.1 认证机制

```python
# 认证流程
AUTH_FLOWS = {
    "local": {
        "type": "password",
        "hash": "bcrypt",
        "min_length": 8,
        "mfa_required": False
    },
    "oauth": {
        "providers": ["google", "github", "microsoft"],
        "scope": ["openid", "profile", "email"]
    },
    "mfa": {
        "type": "totp",  # 或 sms, email
        "backup_codes": 10
    }
}
```

### 2.2 JWT Token 设计

```python
TOKEN_CONFIG = {
    "access_token": {
        "algorithm": "HS256",
        "expiry": "15m",  # 15 分钟
        "payload": {
            "sub": "user_id",
            "type": "access",
            "roles": ["user"],
            "permissions": ["read", "write"]
        }
    },
    "refresh_token": {
        "algorithm": "HS256",
        "expiry": "7d",
        "payload": {
            "type": "refresh",
            "sub": "user_id"
        }
    }
}
```

### 2.3 RBAC 权限模型

```python
# 角色定义
ROLES = {
    "admin": {
        "permissions": ["*"],
        "description": "完全管理员"
    },
    "user": {
        "permissions": [
            "documents:read", "documents:write", "documents:delete",
            "categories:read", "categories:write",
            "projects:read", "projects:write",
            "tags:read", "tags:write",
            "search:read"
        ],
        "description": "普通用户"
    },
    "viewer": {
        "permissions": [
            "documents:read",
            "categories:read",
            "projects:read",
            "tags:read",
            "search:read"
        ],
        "description": "只读用户"
    }
}

# 资源权限
RESOURCES = {
    "documents": ["create", "read", "update", "delete", "share"],
    "categories": ["create", "read", "update", "delete"],
    "projects": ["create", "read", "update", "delete", "manage_members"],
    "tags": ["create", "read", "update", "delete"],
    "sync": ["enable", "disable", "configure"],
    "settings": ["read", "update"]
}
```

---

## 3. 数据加密

### 3.1 传输加密

```python
# TLS 配置
TLS_CONFIG = {
    "version": "TLS 1.3",
    "ciphers": [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256"
    ],
    "hsts": {
        "enabled": True,
        "max_age": 31536000,  # 1 年
        "include_subdomains": True
    },
    "certificate": {
        "provider": "letsencrypt",
        "auto_renew": True,
        "renew_before": 30  # 30 天
    }
}
```

### 3.2 存储加密

```python
# 文件加密
FILE_ENCRYPTION = {
    "algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2",
    "iterations": 600000,
    "chunk_size": 64 * 1024,  # 64KB
    "nonce_size": 12,
    "tag_size": 16
}

# 数据库加密
DATABASE_ENCRYPTION = {
    "at_rest": {
        "type": "transparent",
        "algorithm": "AES-256"
    },
    "fields": {
        "sensitive": ["api_keys", "tokens", "passwords"],
        "method": "field_level"
    }
}
```

### 3.3 密钥管理

```python
# 密钥轮换
KEY_ROTATION = {
    "enabled": True,
    "interval_days": 90,
    "keep_previous_versions": 2
}

# 主密钥存储
MASTER_KEY_STORAGE = {
    "type": "kms",  # AWS KMS / Azure Key Vault
    "fallback": "hardware_security_module"
}
```

---

## 4. API 安全

### 4.1 安全头部

```python
# CSP 配置
CSP_CONFIG = {
    "directives": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'", "https://api.openai.com"],
        "frame-ancestors": ["'none'"]
    }
}

# 安全头部
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

### 4.2 Rate Limiting

```python
RATE_LIMITS = {
    "default": {
        "requests": 100,
        "window": "1 minute"
    },
    "auth": {
        "requests": 5,
        "window": "1 minute"
    },
    "search": {
        "requests": 30,
        "window": "1 minute"
    },
    "ai": {
        "requests": 10,
        "window": "1 minute"
    },
    "upload": {
        "requests": 5,
        "window": "1 hour"
    }
}
```

### 4.3 输入验证

```python
# 输入验证规则
INPUT_VALIDATION = {
    "file_uploads": {
        "max_size": 500 * 1024 * 1024,  # 500MB
        "allowed_types": [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/markdown",
            "text/plain"
        ],
        "max_name_length": 255,
        "scan_virus": True
    },
    "text_fields": {
        "max_length": 10000,
        "sanitize": True,
        "allowed_html_tags": []  # 默认不允许 HTML
    },
    "api_requests": {
        "max_body_size": 100 * 1024 * 1024,  # 100MB
        "max_query_params": 50
    }
}
```

---

## 5. 隐私保护

### 5.1 数据分类

```python
DATA_CLASSIFICATION = {
    "public": {
        "description": "公开数据",
        "examples": ["文档标题", "分类名称"],
        "encryption": False,
        "retention": "indefinite"
    },
    "internal": {
        "description": "内部数据",
        "examples": ["用户偏好", "使用统计"],
        "encryption": True,
        "retention": "3 years"
    },
    "confidential": {
        "description": "机密数据",
        "examples": ["API Keys", "同步令牌"],
        "encryption": True,
        "retention": "1 year",
        "access_log": True
    },
    "restricted": {
        "description": "高度机密",
        "examples": ["用户密码", "支付信息"],
        "encryption": True,
        "retention": "permanent until deleted",
        "access_log": True,
        "mfa_required": True
    }
}
```

### 5.2 AI 数据处理

```python
# AI 功能隐私设置
AI_PRIVACY = {
    "offline_mode": {
        "enabled": True,
        "description": "完全离线运行，不发送数据到云端"
    },
    "local_embedding": {
        "enabled": True,
        "model": "BGE-local",
        "description": "使用本地向量模型"
    },
    "cloud_llm": {
        "enabled": False,
        "description": "可选使用云端 LLM",
        "data_minimization": True,
        "content_filter": True
    },
    "user_control": {
        "opt_in_required": True,
        "explainable_ai": True,
        "data_deletion": True
    }
}
```

### 5.3 数据脱敏

```python
# 日志脱敏
LOG_MASKING = {
    "patterns": [
        {"pattern": r"\b\d{16}\b", "replacement": "****-CARD-****"},
        {"pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "replacement": "***@***.com"},
        {"pattern": r"(api_key|token|password)\s*[:=]\s*[\w-]+", "replacement": "\\1=***"},
        {"pattern": r"\b\d{3}-\d{2}-\d{4}\b", "replacement": "***-**-****"}
    ]
}
```

---

## 6. 审计日志

### 6.1 审计事件

```python
AUDIT_EVENTS = {
    "authentication": {
        "login": {"level": "info"},
        "logout": {"level": "info"},
        "login_failed": {"level": "warning"},
        "password_changed": {"level": "info"},
        "mfa_enabled": {"level": "info"},
        "mfa_disabled": {"level": "info"}
    },
    "authorization": {
        "permission_denied": {"level": "warning"},
        "role_changed": {"level": "info"}
    },
    "data_access": {
        "document_viewed": {"level": "info"},
        "document_downloaded": {"level": "info"},
        "search_performed": {"level": "info"}
    },
    "data_modification": {
        "document_created": {"level": "info"},
        "document_updated": {"level": "info"},
        "document_deleted": {"level": "warning"},
        "category_created": {"level": "info"},
        "category_deleted": {"level": "warning"}
    },
    "security": {
        "suspicious_activity": {"level": "critical"},
        "brute_force_detected": {"level": "warning"},
        "api_key_created": {"level": "info"},
        "api_key_revoked": {"level": "info"}
    }
}

# 审计日志格式
AUDIT_LOG_FORMAT = {
    "timestamp": "ISO8601",
    "user_id": "UUID",
    "event_type": "string",
    "resource_type": "string",
    "resource_id": "UUID",
    "action": "string",
    "ip_address": "string",
    "user_agent": "string",
    "result": "success | failure",
    "details": "JSON object"
}
```

---

## 7. 安全合规

### 7.1 合规清单

```python
COMPLIANCE_CHECKLIST = {
    "gdpr": {
        "enabled": True,
        "requirements": [
            "data_processing_consent",
            "right_to_access",
            "right_to_be_forgotten",
            "data_portability",
            "data_protection_officer"
        ]
    },
    "ccpa": {
        "enabled": True,
        "requirements": [
            "privacy_notice",
            "right_to_know",
            "right_to_delete",
            "opt_out_sale"
        ]
    },
    "soc2": {
        "enabled": False,  # 企业版可选
        "requirements": [
            "security_monitoring",
            "incident_response",
            "change_management"
        ]
    }
}
```

### 7.2 用户权利

```python
USER_RIGHTS = {
    "access": {
        "endpoint": "/api/v1/users/me/data",
        "description": "导出所有个人数据"
    },
    "rectification": {
        "endpoint": "/api/v1/users/me/profile",
        "description": "更正个人信息"
    },
    "erasure": {
        "endpoint": "/api/v1/users/me/delete",
        "description": "删除账户及所有数据",
        "verification": "password"
    },
    "portability": {
        "endpoint": "/api/v1/users/me/export",
        "format": "json",  # 或 zip, csv
        "description": "导出数据为机器可读格式"
    },
    "objection": {
        "endpoint": "/api/v1/users/me/privacy",
        "description": "拒绝特定数据处理"
    }
}
```

---

## 8. 事件响应

### 8.1 安全事件分级

```python
INCIDENT_LEVELS = {
    "critical": {
        "description": "数据泄露、系统入侵",
        "response_time": "15 minutes",
        "notification": ["admin", "user", "authorities"]
    },
    "high": {
        "description": "未授权访问尝试、服务中断",
        "response_time": "1 hour",
        "notification": ["admin", "affected_users"]
    },
    "medium": {
        "description": "策略违反、异常行为",
        "response_time": "4 hours",
        "notification": ["admin"]
    },
    "low": {
        "description": "轻微违规、配置问题",
        "response_time": "24 hours",
        "notification": ["admin"]
    }
}
```

### 8.2 响应流程

```
事件检测
    │
    ▼
┌────────────────────────────────────────────┐
│ 1. 初步评估 (15 分钟)                       │
│    - 确定事件类型和范围                       │
│    - 评估影响程度                            │
│    - 激活响应团队                           │
└────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────┐
│ 2. 遏制措施                                 │
│    - 隔离受影响系统                         │
│    - 阻断攻击路径                           │
│    - 保护证据                              │
└────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────┐
│ 3. 根因分析                                 │
│    - 收集日志和证据                         │
│    - 分析攻击向量                           │
│    - 识别漏洞                              │
└────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────┐
│ 4. 恢复措施                                 │
│    - 清除威胁                              │
│    - 恢复系统                              │
│    - 验证完整性                            │
└────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────┐
│ 5. 事后处理                                 │
│    - 文档记录                              │
│    - 改进措施                              │
│    - 通知受影响用户                         │
└────────────────────────────────────────────┘
```

---

**版本**: v0.7
**日期**: 2026-02-03
**主题**: 安全与隐私设计
