# SkyOne Shuge v1.3 - 项目管理与协作

**版本**: v1.3
**日期**: 2026-02-03

## 新增功能

### 1. 项目管理
### 2. 协作功能
### 3. 权限控制
### 4. 共享链接

---

```python
# models/project.py

class Project(Base):
    id = Column(String(36), primary_key=True)
    name = Column(String(200))
    description = Column(Text)
    owner_id = Column(String(36))
    settings = Column(JSONB)
    created_at = Column(DateTime)

# api/routers/projects.py

@router.get("/projects")
async def list_projects():
    """项目列表"""
    pass


@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """创建项目"""
    pass
```

---

**版本**: v1.3
