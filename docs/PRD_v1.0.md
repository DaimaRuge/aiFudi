# Fudi VoiceOS - 产品需求文档 (PRD)

**版本**: v1.0
**日期**: 2026-02-04
**状态**: 正式版

---

## 1. 产品愿景 (Vision)

**Fudi VoiceOS** - 下一代全双工、混合架构AI语音体

抛弃传统基于"槽位填充"和"正则匹配"的僵化开发模式，构建一个**"云端大模型大脑 + 端侧小模型小脑 + 自主进化唤醒"**的混合AIoT语音架构。

实现真正的自然语言理解、复杂任务规划与全场景生态接入。

---

## 2. 总体架构拓扑图

系统划分为**四个核心平面**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Fudi VoiceOS                            │
├─────────────────────────────────────────────────────────────┤
│  感知与边缘计算平面  │  认知与决策平面  │  行动与调度平面  │
│  (Edge Layer)     │  (Cloud Layer) │  (Gateway Layer) │
├─────────────────────────────────────────────────────────────┤
│  合成与表达平面 (Synthesis Layer)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 详细组件构成

### 3.1 第一层：端侧感知与边缘计算 (Edge Layer)

**目标**: 极速响应、隐私保护、信号清洗

#### 硬件层 (Hardware)
- **Mic Array**: 2-4 麦克风线性或环形阵列（MEMS麦克风）
- **SoC**: RK3588 / 高通 QCS 系列 / 带 NPU 的高性能 MCU

#### 音频前端处理 (SSPE)
- **AEC**: 回声消除，消除设备自己发出的声音
- **BSS/Beamforming**: 盲源分离与波束成形
- **VAD**: 语音活动检测

#### 边缘模型服务 (Edge AI Models)
- **KWS**: BC-ResNet 或 CRNN，合成数据训练
- **Local ASR**: Sherpa-ncnn / Whisper.cpp
- **Local SLM**: Qwen-1.5B-Int4 / Gemma-2B-Int4

---

### 3.2 第二层：云端认知与决策 (Cloud Layer)

**目标**: 语义理解、意图推理、复杂对话管理

- **流式接入网关**: WebSocket / gRPC
- **Cloud ASR**: 豆包 ASR / 阿里 Paraformer-Large
- **LLM Core**: DeepSeek-V3 / Qwen-Max / 豆包 Pro
- **Context Manager**: Vector DB (Qdrant) + Redis

---

### 3.3 第三层：行动与调度平面 (Super Gateway)

**目标**: 替代传统"技能开发"

- **工具注册中心**: OpenAPI/Swagger 解析器
- **鉴权模块**: OAuth2 / API Keys
- **执行引擎**: 并发执行 + Error Handler

---

### 3.4 第四层：合成与表达平面 (TTS Layer)

- **Cloud TTS**: 豆包 TTS / CosyVoice
- **流式合成**: 降低首字延迟
- **情感控制**: 根据 LLM 输出的情感标签调整语调

---

## 4. 关键业务流程

### 场景 A：本地极速控制 (< 800ms)
```
用户："把灯关了。"
1. Mic: 采集音频 -> AEC/降噪
2. Edge KWS: 唤醒 Fudi
3. Local SLM: 解析意图
4. IoT Protocol: 发送指令
5. Feedback: 播放音效
```

### 场景 B：云端复杂任务
```
用户："帮我查天气，放巴赫音乐。"
1. Cloud ASR: 实时转写
2. LLM Reasoning: 分析意图
3. Super Gateway: 并发调用 API
4. LLM Generation: 汇总回复
5. TTS: 流式播报
```

---

## 5. 专项研发：合成 KWS 管线

1. **声学指纹采集器**: RIR 录制
2. **文本生成器**: LLM 生成语料
3. **TTS 合成工厂**: VITS / Edge-TTS
4. **声学增强**: RIR 卷积 + 噪音叠加
5. **自动训练**: CRNN / MatchboxNet

---

## 6. 产品实施计划

### POC-1 (端侧): KWS 训练
- 合成数据训练脚本
- PC 模拟推理验证

### POC-2 (网关): Super Gateway
- FastAPI + LangChain
- ASR -> LLM -> Tool -> TTS 闭环

### POC-3 (硬件): RK3588 适配
- Mic 阵列音频读取
- AEC 处理

---

**版本**: v1.0
