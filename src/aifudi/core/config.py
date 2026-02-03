#!/usr/bin/env python3
"""
Fudi VoiceOS - 配置文件

环境变量和配置管理
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class AudioConfig:
    """音频配置"""
    sample_rate: int = 16000
    channels: int = 4
    chunk_size: int = 1600
    vad_threshold: float = 0.01
    asr_chunk_size: int = 16000


@dataclass
class ASRConfig:
    """ASR 配置"""
    backend: str = "sherpa-ncnn"
    model_path: str = ""
    language: str = "zh"


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str = "deepseek"
    model: str = "deepseek-chat"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class TTSConfig:
    """TTS 配置"""
    provider: str = "cosyvoice"
    voice: str = "zh_female"
    sample_rate: int = 24000
    speed: float = 1.0


@dataclass
class KWSConfig:
    """KWS 配置"""
    wakeword: str = "你好富di"
    model_path: str = ""
    threshold: float = 0.9


@dataclass
class GatewayConfig:
    """Gateway 配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


@dataclass
class DeviceConfig:
    """设备配置"""
    name: str = "OpenClaw Box"
    type: str = "rk3588"
    enable_cloud: bool = True
    enable_edge: bool = True
    
    audio: AudioConfig = field(default_factory=AudioConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    kws: KWSConfig = field(default_factory=KWSConfig)
    gateway: GatewayConfig = field(default_factory=GatewayConfig)


class Config:
    """配置管理"""
    
    def __init__(self, config_file: str = None):
        self.config = DeviceConfig()
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载"""
        # 音频
        if os.getenv("AUDIO_SAMPLE_RATE"):
            self.config.audio.sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE"))
        
        # ASR
        if os.getenv("ASR_BACKEND"):
            self.config.asr.backend = os.getenv("ASR_BACKEND")
        if os.getenv("ASR_API_KEY"):
            self.config.asr.api_key = os.getenv("ASR_API_KEY")
        
        # LLM
        if os.getenv("LLM_PROVIDER"):
            self.config.llm.provider = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_API_KEY"):
            self.config.llm.api_key = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_MODEL"):
            self.config.llm.model = os.getenv("LLM_MODEL")
        
        # TTS
        if os.getenv("TTS_PROVIDER"):
            self.config.tts.provider = os.getenv("TTS_PROVIDER")
        
        # KWS
        if os.getenv("WAKEWORD"):
            self.config.kws.wakeword = os.getenv("WAKEWORD")
        
        # Gateway
        if os.getenv("GATEWAY_HOST"):
            self.config.gateway.host = os.getenv("GATEWAY_HOST")
        if os.getenv("GATEWAY_PORT"):
            self.config.gateway.port = int(os.getenv("GATEWAY_PORT"))
    
    def get(self) -> DeviceConfig:
        """获取配置"""
        return self.config


# 默认配置文件
DEFAULT_CONFIG = """
# Fudi VoiceOS 配置文件
# 复制为 .env 并修改

# 音频配置
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=4

# ASR 配置
ASR_BACKEND=sherpa-ncnn
ASR_API_KEY=

# LLM 配置
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-your-api-key
LLM_MODEL=deepseek-chat

# TTS 配置
TTS_PROVIDER=cosyvoice

# KWS 配置
WAKEWORD=你好富di

# Gateway 配置
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
"""

def save_default_config(path: str = ".env"):
    """保存默认配置"""
    with open(path, "w") as f:
        f.write(DEFAULT_CONFIG)
    print(f"Saved default config to {path}")


# 使用示例
if __name__ == "__main__":
    config = Config()
    device_config = config.get()
    
    print("Current Config:")
    print(f"  Name: {device_config.name}")
    print(f"  Audio: {device_config.audio.sample_rate}Hz")
    print(f"  LLM: {device_config.llm.provider}/{device_config.llm.model}")
    print(f"  Wakeword: {device_config.kws.wakeword}")
