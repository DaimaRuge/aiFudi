# AI Fudi - Fudi VoiceOS v0.2.0

**Fudi VoiceOS** - 下一代混合AI语音助手框架 (端云协同 + Super Gateway)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.2.0-orange)](https://github.com/DaimaRuge/aiFudi)

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
│   ├── __init__.py
│   ├── agents/                      # 🆕 Agent 模块 v0.2.0
│   │   ├── __init__.py
│   │   └── openclaw.py              # OpenClaw 中间件 (RK3588)
│   ├── config.py                    # 🆕 Pydantic 配置系统
│   ├── logger.py                    # 🆕 结构化日志
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # 配置文件管理
│   │   ├── pipeline.py              # 完整语音交互流水线
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py            # LLM 引擎 (DeepSeek/Qwen/豆包)
│   │   │   └── router.py            # LLM 路由
│   │   ├── asr/
│   │   │   └── engine.py            # ASR 引擎 (Sherpa/Whisper)
│   │   ├── tts/
│   │   │   └── engine.py            # TTS 引擎 (CosyVoice/Edge-TTS)
│   │   └── audio/
│   │       ├── __init__.py
│   │       ├── preprocessor.py      # AEC/VAD/波束成形
│   │       ├── io.py                # 音频 I/O (ALSA)
│   │       ├── kws_pipeline.py      # KWS Pipeline
│   │       └── kws_trainer.py       # KWS 完整训练管线
│   └── gateway/
│       └── super_gateway.py         # Agent Orchestrator
├── docs/
│   ├── PRD_v1.0.md
│   ├── ARCHITECTURE_v1.0.md
│   ├── OPENCLAW_BOX_v1.0.md
│   └── FILE_STRUCTURE.md
├── examples/
│   ├── demo.py
│   └── demo_agent.py                # 🆕 Agent 演示脚本
├── tests/
│   ├── README.md
│   └── test_agents.py               # 🆕 Agent 单元测试
├── requirements.txt                 # 🆕 依赖管理
├── pyproject.toml                   # 🆕 项目配置
└── README.md
```

## 🔥 核心组件

| 组件 | 功能 | 状态 |
|------|------|------|
| **OpenClaw** | RK3588 中间件框架 | ✅ v0.2.0 |
| **Super Gateway** | OpenAPI注册 + Function Calling + 并发执行 | ✅ v0.1.0 |
| **LLM Router** | 云端/端侧智能分发 | 🔄 WIP |
| **KWS Pipeline** | 合成数据训练 + RIR卷积 | 🔄 WIP |
| **Audio SSPE** | AEC回声消除 + VAD检测 + 波束成形 | 🔄 WIP |

### v0.2.0 新特性 🆕

- **配置系统**: Pydantic Settings + 环境变量支持
- **错误处理**: 完整的错误代码体系 + 异常恢复机制
- **Mock 引擎**: 可运行的演示版本 (无需实际硬件)
- **单元测试**: pytest 全覆盖测试
- **结构化日志**: 可配置的日志级别和格式
- **技能注册**: 动态技能注册/注销 API

## 🚀 Quick Start

### 安装

```bash
# 克隆仓库
git clone https://github.com/DaimaRuge/aiFudi.git
cd aiFudi

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行演示

```bash
# Agent 演示 (模拟模式)
python examples/demo_agent.py

# 启动 API 服务
uvicorn src.aifudi.gateway.super_gateway:app --reload --port 8000
```

### 配置

创建 `.env` 文件：

```env
# 设备配置
DEVICE_NAME="Fudi Box"
WAKEWORD="你好富迪"

# 日志
LOG_LEVEL=INFO
LOG_FILE=logs/aifudi.log

# 模型路径
MODEL_KWS_MODEL=/models/kws.onnx
MODEL_ASR_MODEL=/models/asr.onnx

# LLM (云端)
MODEL_LLM_PROVIDER=deepseek
MODEL_LLM_MODEL=deepseek-chat
MODEL_LLM_API_KEY=your-api-key
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行 Agent 测试
pytest tests/test_agents.py -v

# 带覆盖率报告
pytest tests/ --cov=src/aifudi --cov-report=html
```

## 📖 使用示例

### 基础用法

```python
import asyncio
from aifudi.agents import OpenClawMiddleware, DeviceConfig

async def main():
    # 配置
    config = DeviceConfig(
        name="Fudi Box",
        wakeword="你好富迪"
    )
    
    # 创建中间件
    openclaw = OpenClawMiddleware(config)
    
    # 注册自定义技能
    async def weather_skill(params):
        city = params.get("city", "北京")
        return f"{city}今天晴，25°C"
    
    openclaw.register_skill("weather", weather_skill)
    
    # 初始化和启动
    await openclaw.initialize()
    await openclaw.start()

asyncio.run(main())
```

### 意图解析

```python
# 解析用户指令
intent = await openclaw._parse_intent("打开客厅的灯")
print(intent.skill)       # "light_control"
print(intent.parameters)  # {"action": "on", "target": "客厅灯"}
```

### 状态机

```python
from aifudi.agents import DeviceState

# 检查设备状态
if openclaw.state == DeviceState.LISTENING:
    print("等待唤醒...")
elif openclaw.state == DeviceState.PROCESSING:
    print("处理中...")
```

## 📚 文档

- [产品需求文档](docs/PRD_v1.0.md)
- [架构设计文档](docs/ARCHITECTURE_v1.0.md)
- [OpenClaw Box 硬件设计](docs/OPENCLAW_BOX_v1.0.md)
- [API 文档](http://localhost:8000/docs) (启动后访问)

## 🎯 Roadmap

### v0.3.0 (计划中)
- [ ] 接入实际 ASR 模型 (Whisper)
- [ ] 接入实际 TTS 模型 (CosyVoice)
- [ ] Redis 记忆持久化
- [ ] WebSocket 实时通信

### v0.4.0 (计划中)
- [ ] RK3588 NPU 加速
- [ ] 本地 LLM 部署 (RKLLM)
- [ ] 音频预处理优化 (AEC/VAD)

## 📦 硬件选型

| 平台 | 芯片 | NPU | 用途 | 状态 |
|------|------|-----|------|------|
| PoC | 树莓派5 | 无 | 快速验证 | ✅ |
| 量产 | RK3588 | 6 TOPS | 高端产品 | 🔄 |
| 入门 | ESP32-S3 | 有限 | 低成本 | 📋 |

## 🤝 贡献

欢迎贡献代码和想法！

```bash
# Fork 并克隆
# 创建分支
git checkout -b feature/your-feature

# 提交更改
git commit -am "Add: your feature"

# 推送到 GitHub
git push origin feature/your-feature

# 创建 Pull Request
```

## 📄 许可证

[MIT License](LICENSE)

---

**GitHub**: https://github.com/DaimaRuge/aiFudi  
**Issues**: https://github.com/DaimaRuge/aiFudi/issues  
**Documentation**: https://docs.aifudi.ai

Built with ❤️ by the Fudi Team
