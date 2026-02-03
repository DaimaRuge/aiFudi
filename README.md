# AI Fudi - Fudi VoiceOS

**Fudi VoiceOS** - 下一代混合AI语音助手框架 (端云协同 + Super Gateway)

## 🎯 产品愿景

抛弃传统"槽位填充"模式，构建**"云端大模型大脑 + 端侧小模型小脑 + 自主进化唤醒"**的混合AIoT语音架构。

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                   Fudi VoiceOS 架构                        │
├─────────────────────────────────────────────────────────────┤
│  感知边缘层 → 云端认知层 → 行动调度层 → 合成表达层         │
│     (快/私)     (深/广)       (手/脚)      (表达)         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
aiFudi/
├── src/aifudi/
│   ├── agents/
│   │   └── openclaw.py          # OpenClaw 中间件 (RK3588)
│   ├── core/
│   │   ├── audio/
│   │   │   ├── kws_pipeline.py   # 合成 KWS 训练管线
│   │   │   └── preprocessor.py   # AEC/VAD/波束成形
│   │   └── llm/
│   │       └── router.py         # 云端+端侧智能分发
│   └── gateway/
│       └── super_gateway.py      # Agent Orchestrator
├── docs/
│   ├── PRD_v1.0.md             # 产品需求文档
│   ├── ARCHITECTURE_v1.0.md    # 架构设计文档
│   └── OPENCLAW_BOX_v1.0.md   # RK3588 硬件设计
└── examples/
    └── demo.py                  # 演示脚本
```

## 🔥 核心组件

| 组件 | 功能 |
|------|------|
| **OpenClaw** | RK3588 中间件框架 |
| **Super Gateway** | OpenAPI注册 + Function Calling + 并发执行 |
| **LLM Router** | 云端/端侧智能分发 |
| **KWS Pipeline** | 合成数据训练 + RIR卷积 |
| **Audio SSPE** | AEC回声消除 + VAD检测 + 波束成形 |

## 🚀 Quick Start

```bash
# 克隆
git clone https://github.com/DaimaRuge/aiFudi.git
cd aiFudi

# 安装依赖
pip install -r requirements.txt

# 运行演示
python examples/demo.py

# 启动 API
uvicorn src.aifudi.gateway.super_gateway:app --reload
```

## 📚 文档

- [产品需求文档](docs/PRD_v1.0.md)
- [架构设计文档](docs/ARCHITECTURE_v1.0.md)
- [OpenClaw Box 硬件设计](docs/OPENCLAW_BOX_v1.0.md)

## 🎯 POC 计划

1. **POC-1**: 端侧 KWS 训练 (合成数据)
2. **POC-2**: Super Gateway API (FastAPI + LangChain)
3. **POC-3**: RK3588 硬件适配

## 📦 硬件选型

| 平台 | 芯片 | NPU | 用途 |
|------|------|-----|------|
| PoC | 树莓派5 | 无 | 快速验证 |
| 量产 | RK3588 | 6 TOPS | 高端产品 |
| 入门 | ESP32-S3 | 有限 | 低成本 |

## 🤝 贡献

欢迎贡献代码和想法！

## 📄 许可证

MIT

---

**GitHub**: https://github.com/DaimaRuge/aiFudi
