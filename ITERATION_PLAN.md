# 天一阁 (SkyOne Shuge) 每日迭代计划

## 工作节奏
- **工作时间**: 23:00 - 08:00
- **交付时间**: 09:00 每日新版本

---

## 已完成版本

### v0.1 (2026-02-03)
- [x] 产品概述与愿景
- [x] 核心功能定义
- [x] 技术架构初稿
- [x] 使用场景分析

### v0.2 (2026-02-03)
- [x] 数据库表结构设计 (PostgreSQL + Qdrant)
- [x] API 接口规范 (FastAPI)
- [x] 分类引擎设计
- [x] 向量数据库设计
- [x] 核心模块详解 (Scanner/Indexer/Classifier/Sync/Agent)

### v0.3 (2026-02-03)
- [x] MVP 功能优先级定义
- [x] 开发任务拆分 (WBS) - 7 个 Phase, 17 人天
- [x] 技术栈最终确认
- [x] 项目目录结构
- [x] 开发规范文档
- [x] 里程碑规划

### v0.4 (2026-02-03)
- [x] UI/UX 设计原则
- [x] 页面结构设计 (6 个核心页面)
- [x] 线框图设计
- [x] 交互流程图
- [x] 响应式设计方案
- [x] 组件库规划
- [x] 图标规范

### v0.5 (2026-02-03) ✅ 最新
- [x] 数据库详细设计 (8 张核心表)
- [x] 向量数据库设计 (Qdrant)
- [x] API 详细设计 (OpenAPI 规范)
- [x] 数据访问层 (DAL) 设计
- [x] 数据库迁移 (Alembic)
- [x] 错误码定义

---

## 文件清单

```
skyone-shuge/
├── prd/
│   ├── PRODUCT_SPECIFICATION_v0.1.md
│   ├── PRODUCT_SPECIFICATION_v0.2.md
│   ├── PRODUCT_SPECIFICATION_v0.3.md
│   └── UI_DESIGN_v0.4.md
│
└── architecture/
    ├── SYSTEM_ARCHITECTURE_v0.2.md
    ├── DEVELOPMENT_GUIDE_v0.3.md
    ├── DATABASE_DESIGN_v0.5.md
    └── API_DESIGN_v0.5.md
```

---

## 邮件发送配置

- **发送邮箱**: qun.xitang.du@gmail.com
- **接收邮箱**: broadbtinp@gmail.com, dulie@foxmail.com
- **SMTP**: smtp.gmail.com:587
- **App Password**: hzya cyji lhig whiu ✅ 已配置

## 邮件发送规则

### PRD 文档
- 每个版本发送 1 封邮件
- 包含版本更新说明

### 代码包
- **每次代码更新都会打包发送**
- 格式: `skyone_code_v{版本}.tar.gz`
- 包含完整项目代码
- 使用脚本: `scripts/send_code_email.py`

### 发送命令

```bash
# 发送代码包邮件
python scripts/send_code_email.py
```



---

## 今日完成 (2026-02-03)
✅ v0.5 数据库详细设计 (8 张表)
✅ v0.5 API 详细设计
✅ 邮件发送成功 (5 个版本已发送)
