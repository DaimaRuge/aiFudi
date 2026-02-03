# AI Fudi - Fudi VoiceOS

下一代混合AI语音助手框架 (端云协同 + Super Gateway)

## 核心架构

```
aiFudi/
├── core/              # 核心引擎
│   ├── audio/        # 音频处理 (VAD/AEC/Beamforming)
│   ├── asr/          # ASR 引擎
│   ├── llm/          # LLM 集成
│   └── tts/          # TTS 引擎
├── gateway/          # Super Gateway (Agent Orchestrator)
├── agents/           # AI Agent
├── models/           # 数据模型
└── scripts/         # 工具脚本
```

## 功能特性

- 🎤 **全双工语音交互** - 支持打断
- 🧠 **混合推理** - 云端LLM + 端侧SLM
- 🌐 **Super Gateway** - OpenAPI注册 + Function Calling
- 🔒 **隐私保护** - 本地优先处理
- ⚡ **低延迟** - 全链路流式处理

## Quick Start

```bash
# 克隆
git clone https://github.com/DaimaRuge/aiFudi.git

# 安装依赖
pip install -r requirements.txt

# 运行
python -m aifudi
```

## 文档

见 docs/ 目录
