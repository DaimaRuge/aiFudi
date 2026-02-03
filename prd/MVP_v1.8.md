# SkyOne Shuge v1.8 - 企业功能

**版本**: v1.8
**日期**: 2026-02-03

## 新增功能

### 1. 企业管理
### 2. 团队协作
### 3. 审计日志
### 4. SSO 集成

---

## 功能列表

```python
# models/team.py

class Team(Base):
    id = Column(String(36), primary_key=True)
    name = Column(String(200))
    owner_id = Column(String(36))
    settings = Column(JSONB)
    created_at = Column(DateTime)

# models/audit.py

class AuditLog(Base):
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36))
    action = Column(String(100))
    resource = Column(String(200))
    details = Column(JSONB)
    created_at = Column(DateTime)
```

---

**版本**: v1.8
