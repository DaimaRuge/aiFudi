# SkyOne Shuge v2.4 - 协作与分享

**版本**: v2.4
**日期**: 2026-02-03

## 新增功能

### 1. 共享链接

```python
# models/share.py

class ShareLink(Base):
    id = Column(String(36), primary_key=True)
    token = Column(String(64), unique=True)
    document_id = Column(String(36))
    expires_at = Column(DateTime)
    password = Column(String(128))  # 可选密码
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. 协作编辑

```python
# services/collaboration.py

class CollaborationService:
    async def create_room(self, document_id: str, users: List[str]) -> str:
        """创建协作房间"""
        pass
    
    async def send_message(self, room_id: str, message: dict):
        """发送消息"""
        pass
```

### 3. 评论系统

```python
# models/comment.py

class Comment(Base):
    id = Column(String(36), primary_key=True)
    document_id = Column(String(36))
    user_id = Column(String(36))
    content = Column(Text)
    page_number = Column(Integer)  # PDF 页码
    position = Column(JSONB)  # 位置坐标
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

**版本**: v2.4
