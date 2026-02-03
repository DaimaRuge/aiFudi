# OpenClaw Box - RK3588 硬件参考设计

**版本**: v1.0
**日期**: 2026-02-04

---

## 1. 产品定义

**OpenClaw Box** - 基于RK3588的混合AI代理架构

不只是一个智能音箱，而是一个**"本地优先、云端增强"**的物理AI代理。

---

## 2. 硬件规格

### 2.1 核心芯片
- **SoC**: RK3588 (8核 CPU + 6T NPU)
- **CPU**: 4x Cortex-A76 + 4x Cortex-A55
- **NPU**: 6 TOPS (INT8)
- **GPU**: Mali-G610 MP4

### 2.2 内存与存储
- **内存**: 16GB LPDDR5 (共享)
- **存储**: 256GB eMMC + M.2 NVMe

### 2.3 音频配置
- **麦克风**: 4-Mic 环形阵列
- **扬声器**: 2x 5W 高保真
- **ADC/DAC**: ES8316 或类似

### 2.4 连接性
- **WiFi**: WiFi 6 (AP6275S)
- **蓝牙**: BT 5.2
- **以太网**: 1Gbps RJ45

### 2.5 扩展接口
- **GPIO**: 40-pin header
- **USB**: 2x USB 3.0 + 2x USB 2.0
- **HDMI**: 2x HDMI 2.1 (8K输出)

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                  OpenClaw Box                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │            Linux (Ubuntu 22.04)                  │  │
│  │   Systemd 服务管理 + Docker 容器                 │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │            OpenClaw Middleware                  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────────────┐ │  │
│  │  │Perception│ │  Brain  │ │     Action      │ │  │
│  │  │ VAD/KWS │ │ Router  │ │ GPIO/MQTT/HA   │ │  │
│  │  │ ASR     │ │ LocalLLM│ │                 │ │  │
│  │  └─────────┘ └─────────┘ └─────────────────┘ │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │            NPU Runtime                          │  │
│  │  ┌─────────────┐ ┌─────────────┐             │  │
│  │  │  RKLLM      │ │  RKNN       │             │  │
│  │  │  (LLM推理)  │ │  (ASR/KWS)  │             │  │
│  │  └─────────────┘ └─────────────┘             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │            Hardware Layer                       │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐         │  │
│  │  │  Mic    │ │ Speaker │ │  GPIO   │         │  │
│  │  │  阵列   │ │  驱动   │ │  控制   │         │  │
│  │  └─────────┘ └─────────┘ └─────────┘         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 软件栈

### 4.1 系统层
- **OS**: Ubuntu 22.04 Server (无桌面)
- **容器**: Docker + Docker Compose
- **服务**: Systemd

### 4.2 驱动层
- **NPU**: rknn2-driver + librknnrt
- **音频**: ALSA (alsa-utils + pyalsaaudio)
- **GPIO**: python-rpi.gpio 或 libgpiod

### 4.3 中间件层 (OpenClaw)
- **Python**: 3.10+
- **推理框架**: RKLLM-Runtime + RKNN-Toolkit2
- **Web框架**: FastAPI
- **异步**: asyncio

### 4.4 模型层
| 模型 | 大小 | 精度 | 位置 |
|------|------|------|------|
| Qwen-1.5B-Int4 | ~1GB | Int4 | NPU |
| SenseVoice-Small | ~100MB | Int8 | NPU |
| CRNN-KWS | ~10MB | Int8 | NPU |

---

## 5. 性能指标

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| **LLM 推理速度** | 15-20 token/s | Qwen-1.5B-Int4 |
| **ASR 延迟** | < 200ms | 端到端 |
| **KWS 延迟** | < 100ms | 唤醒检测 |
| **全链路延迟** | < 1.5s | 本地控制 |
| **功耗 (空闲)** | < 3W | 测量 |
| **功耗 (满载)** | < 15W | 测量 |

---

## 6. 部署步骤

### 6.1 系统安装
```bash
# 1. 烧录镜像
balenaetcher rock-5b.img /dev/sdX

# 2. 基础配置
sudo apt update
sudo apt install -y docker.io docker-compose

# 3. 安装 NPU 驱动
wget https://github.com/rockchip-linux/rknn-toolkit2/releases
tar -xvf rknn-toolkit2-*.whl
pip install rknn-toolkit2-*.whl
```

### 6.2 模型部署
```bash
# 1. 下载模型
mkdir -p /models
wget https://huggingface.co/Qwen/Qwen-1.5B-Chat -O /models/qwen.gguf

# 2. 量化转换
python rkllm-toolkit/convert.py \
    --model /models/qwen.gguf \
    --out_dir /models \
    --quantize int4

# 3. 部署
cp /models/*.rkllm /opt/openclaw/models/
```

### 6.3 服务启动
```bash
# 启动 OpenClaw
docker-compose up -d

# 检查状态
docker logs openclaw
```

---

## 7. 成本估算

| 组件 | 数量 | 单价 | 小计 |
|------|------|------|------|
| RK3588 核心板 | 1 | $80 | $80 |
| 外壳 + PCB | 1 | $30 | $30 |
| 4-Mic 阵列 | 1 | $15 | $15 |
| 扬声器 + 功放 | 1 | $20 | $20 |
| 电源 + 配件 | 1 | $15 | $15 |
| **合计** | | | **$160** |

---

## 8. 产品形态扩展

1. **AI DeskBot**: 带屏幕的桌面机器人
2. **AI Headphone**: 骨传导耳机方案
3. **Privacy Home Hub**: 智能家居中控

---

**版本**: v1.0
