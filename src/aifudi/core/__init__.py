#!/usr/bin/env python3
"""
Fudi VoiceOS - 核心包
"""

__version__ = "0.1.0"
__author__ = "AI Assistant"

# 版本信息
VERSION = "0.1.0"
NAME = "Fudi VoiceOS"

# 子模块
from .core.config import Config, AudioConfig, LLMConfig, TTSConfig
from .core.pipeline import VoicePipeline, StreamingPipeline
from .core.llm.engine import LLMEngine, LLMRouter, PromptEngine
from .core.llm.router import LLMRouter as LocalLLMRouter
from .core.asr.engine import ASREngine, ASRRouter
from .core.tts.engine import TTSEngine, TTSRouter
from .core.audio.io import AudioIO, AudioStreamHandler
from .core.audio.preprocessor import AudioPreprocessor
from .core.audio.kws_pipeline import KWSPipeline
from .core.audio.kws_trainer import KWSTrainer

__all__ = [
    # 版本
    "__version__",
    "VERSION",
    "NAME",
    
    # 配置
    "Config",
    "AudioConfig",
    "LLMConfig",
    "TTSConfig",
    
    # 流水线
    "VoicePipeline",
    "StreamingPipeline",
    
    # LLM
    "LLMEngine",
    "LLMRouter",
    "PromptEngine",
    
    # ASR
    "ASREngine",
    "ASRRouter",
    
    # TTS
    "TTSEngine",
    "TTSRouter",
    
    # 音频
    "AudioIO",
    "AudioStreamHandler",
    "AudioPreprocessor",
    
    # KWS
    "KWSPipeline",
    "KWSTrainer",
]
