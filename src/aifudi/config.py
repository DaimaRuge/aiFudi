"""
AI Fudi - Configuration Management

使用 Pydantic Settings 管理配置
支持环境变量和配置文件
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioSettings(BaseSettings):
    """音频配置"""
    model_config = SettingsConfigDict(env_prefix="AUDIO_")
    
    sample_rate: int = Field(default=16000, description="采样率")
    channels: int = Field(default=4, description="通道数 (麦克风阵列)")
    chunk_size: int = Field(default=1600, description="块大小 (100ms @ 16kHz)")
    vad_threshold: float = Field(default=0.01, description="VAD 阈值")
    
    # ALSA 配置
    input_device: str = Field(default="default", description="输入设备")
    output_device: str = Field(default="default", description="输出设备")
    
    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: int) -> int:
        valid_rates = [8000, 16000, 22050, 44100, 48000]
        if v not in valid_rates:
            raise ValueError(f"sample_rate must be one of {valid_rates}")
        return v


class ModelSettings(BaseSettings):
    """模型配置"""
    model_config = SettingsConfigDict(env_prefix="MODEL_")
    
    # 模型路径
    kws_model: str = Field(default="/models/kws.onnx", description="唤醒词模型")
    asr_model: str = Field(default="/models/asr.onnx", description="ASR 模型")
    tts_model: str = Field(default="/models/tts.onnx", description="TTS 模型")
    
    # 云端 LLM 配置
    llm_provider: str = Field(default="deepseek", description="LLM 提供商")
    llm_model: str = Field(default="deepseek-chat", description="LLM 模型")
    llm_api_key: Optional[str] = Field(default=None, description="API Key")
    llm_base_url: Optional[str] = Field(default=None, description="API Base URL")
    
    # 本地 LLM (RKLLM)
    local_llm_path: Optional[str] = Field(default=None, description="本地 LLM 路径")
    use_local_llm: bool = Field(default=False, description="使用本地 LLM")


class GatewaySettings(BaseSettings):
    """Super Gateway 配置"""
    model_config = SettingsConfigDict(env_prefix="GATEWAY_")
    
    host: str = Field(default="0.0.0.0", description="主机地址")
    port: int = Field(default=8000, description="端口")
    workers: int = Field(default=1, description="工作进程数")
    
    # 记忆体配置
    memory_backend: str = Field(default="memory", description="记忆后端 (memory/redis)")
    redis_url: Optional[str] = Field(default=None, description="Redis URL")
    
    # 超时配置
    request_timeout: float = Field(default=30.0, description="请求超时 (秒)")


class LoggingSettings(BaseSettings):
    """日志配置"""
    model_config = SettingsConfigDict(env_prefix="LOG_")
    
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    file: Optional[str] = Field(default=None, description="日志文件路径")
    
    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"level must be one of {valid_levels}")
        return v_upper


class Settings(BaseSettings):
    """全局配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 应用信息
    app_name: str = Field(default="AI Fudi", description="应用名称")
    app_version: str = Field(default="0.2.0", description="版本号")
    debug: bool = Field(default=False, description="调试模式")
    
    # 设备配置
    device_name: str = Field(default="OpenClaw Box", description="设备名称")
    wakeword: str = Field(default="你好富迪", description="唤醒词")
    language: str = Field(default="zh", description="语言")
    
    # 子配置
    audio: AudioSettings = Field(default_factory=AudioSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)
    gateway: GatewaySettings = Field(default_factory=GatewaySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    # 技能白名单 (安全控制)
    enabled_skills: List[str] = Field(
        default_factory=lambda: ["light_control", "volume_control", "get_time", "weather"],
        description="启用的技能列表"
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例 (单例)"""
    return Settings()


# 全局配置对象
settings = get_settings()
