# Fudi VoiceOS - 架构设计文档

**版本**: v1.0
**日期**: 2026-02-04

---

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                   Fudi VoiceOS 架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         感知与边缘计算平面 (Edge Layer)              │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │ Mic阵列 │ │   SSPE  │ │  KWS    │ │ Local   │  │  │
│  │  │ 2-4 Mics│ │AEC/VAD  │ │ 唤醒词  │ │  ASR    │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         认知与决策平面 (Cloud Layer)                │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────────────────┐  │  │
│  │  │Streaming │ │ Cloud   │ │     LLM Core        │  │  │
│  │  │ Gateway  │ │   ASR   │ │ DeepSeek/Qwen/豆包  │  │  │
│  │  └─────────┘ └─────────┘ └─────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         行动与调度平面 (Gateway Layer)              │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────────────────┐  │  │
│  │  │   Tool  │ │  Auth   │ │   Execution Engine   │  │  │
│  │  │ Registry│ │ Module  │ │ Parallel + Error     │  │  │
│  │  └─────────┘ └─────────┘ └─────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         合成与表达平面 (Synthesis Layer)             │  │
│  │  ┌─────────────┐ ┌─────────────────────────────┐ │  │
│  │  │   Cloud     │ │     Streaming TTS           │ │  │
│  │  │   TTS       │ │     豆包/CosyVoice          │ │  │
│  │  └─────────────┘ └─────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 详细组件设计

### 2.1 Edge Layer 组件

#### 麦克风阵列
- **类型**: 2-4 MEMS 麦克风
- **配置**: 线性或环形阵列
- **关键参数**:
  - 采样率: 16kHz
  - 位深度: 16-bit
  - DOA 精度: ±5°

#### SSPE (Speech Signal Processing Engine)
```python
class SSPE:
    """
    语音信号处理引擎
    """
    
    def __init__(self):
        self.aec = AEC()
        self.vad = VAD()
        self.beamformer = Beamformer()
    
    def process(self, mic_signals: List[np.ndarray]) -> np.ndarray:
        # 1. 波束成形
        beamformed = self.beamformer.process(mic_signals)
        
        # 2. 回声消除
        output = self.aec.cancel(beamformed)
        
        # 3. VAD 检测
        is_speech = self.vad.detect(output)
        
        return output, is_speech
```

#### KWS (Keyword Spotting)
```python
class KWS:
    """
    关键词检测
    """
    
    def __init__(self, model_path: str):
        self.model = load_model(model_path)  # CRNN/BC-ResNet
    
    def detect(self, audio: np.ndarray) -> Dict:
        # 1. 提取 Mel 频谱
        mel_spec = self.extract_mel(audio)
        
        # 2. 模型推理
        prob = self.model.predict(mel_spec)
        
        # 3. 返回结果
        return {
            "is_wakeword": prob > 0.9,
            "confidence": prob
        }
```

---

### 2.2 Cloud Layer 组件

#### Streaming Gateway
```python
class StreamingGateway:
    """
    WebSocket 流式接入网关
    """
    
    async def handle_connection(self, websocket):
        # 音频流解包
        async for audio_chunk in websocket:
            # 分发给 ASR
            result = await self.asr.process(audio_chunk)
            # 发送到 LLM
            await self.llm.send(result)
```

#### LLM Core
```python
class LLMCore:
    """
    LLM 核心
    """
    
    def __init__(self, model: str = "deepseek-v3"):
        self.model = model
        self.prompt_engineering = PromptEngine()
    
    async def reason(self, text: str, context: Dict) -> Dict:
        # 1. 构建 Prompt
        prompt = self.prompt_engineering.build(text, context)
        
        # 2. 调用 LLM
        response = await self.call_api(prompt)
        
        # 3. 解析 JSON Action
        action = self.parse_action(response)
        
        return action
```

---

### 2.3 Gateway Layer 组件

#### Tool Registry
```python
class ToolRegistry:
    """
    工具注册中心
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register_from_openapi(self, openapi_spec: Dict):
        """从 OpenAPI 规范注册工具"""
        for path, methods in openapi_spec["paths"].items():
            for method, details in methods.items():
                if method in ["get", "post"]:
                    tool = Tool(
                        name=f"{method}_{path}",
                        schema=details,
                        handler=self._generate_handler(details)
                    )
                    self.tools[tool.name] = tool
```

#### Execution Engine
```python
class ExecutionEngine:
    """
    执行引擎
    """
    
    async def execute(self, actions: List[Action]) -> List[Result]:
        """并发执行多个 Action"""
        tasks = [self._execute(action) for action in actions]
        return await asyncio.gather(*tasks)
```

---

## 3. 数据流设计

### 3.1 本地控制流 (< 800ms)
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Mic    │ -> │   SSPE   │ -> │   KWS    │ -> │  Local   │
│  阵列    │    │ AEC/VAD  │    │  唤醒词  │    │   SLM    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                                      v
┌──────────┐    ┌──────────┐                          │
│  设备    │ <- │   IoT    │ <- ┌────────────────────┘
│  执行    │    │ Protocol │    │
└──────────┘    └──────────┘    └────────────────────┐
                                                      v
                                              ┌──────────┐
                                              │ Feedback │
                                              │  音效    │
                                              └──────────┘
```

### 3.2 云端复杂流
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Mic    │ -> │  Cloud   │ -> │   LLM    │ -> │ Gateway  │
│  阵列    │    │   ASR    │    │  推理    │    │  执行    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                              ┌───────────────────────┘
                              v
                    ┌───────────────────┐
                    │ 并发调用多个 API  │
                    │ (天气 + 音乐)     │
                    └───────────────────┘
                              │
                              v
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Feedback │ <- │   LLM    │ <- │  结果    │
│  播报    │    │  汇总    │    │  汇总    │
└──────────┘    └──────────┘    └──────────┘
```

---

## 4. 技术选型

### 4.1 芯片选型

| 级别 | 芯片 | NPU | 内存 | 用途 |
|------|------|-----|------|------|
| **PoC** | 树莓派5 | 无 | 8GB | 快速验证 |
| **量产** | RK3588 | 6 TOPS | 16GB | 高端产品 |
| **入门** | ESP32-S3 | 有限 | 2MB | 低成本 |

### 4.2 模型选型

| 类型 | 模型 | 精度 | 延迟 |
|------|------|------|------|
| **云端 LLM** | DeepSeek-V3 | FP16 | ~2s |
| **端侧 SLM** | Qwen-1.5B-Int4 | Int4 | <500ms |
| **KWS** | CRNN | Int8 | <100ms |
| **ASR** | Sherpa-ncnn | Int8 | <200ms |

---

## 5. 性能指标

| 场景 | 目标延迟 | 当前指标 |
|------|----------|----------|
| 本地控制 | < 800ms | TBD |
| 云端响应 | < 2s | TBD |
| 唤醒率 | > 95% | TBD |
| 误触率 | < 1% | TBD |

---

**版本**: v1.0
