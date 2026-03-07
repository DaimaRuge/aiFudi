#!/usr/bin/env python3
"""
OpenClaw - RK3588 中间件框架 v0.2.0

边缘AI代理系统的核心中间件

功能:
- 连接 NPU 算力
- 语音 IO 管理
- 本地技能调度
- 云端生态接入
- 错误恢复与容错

版本: 0.2.0
"""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from ..logger import get_logger
from ..config import settings

logger = get_logger("agents.openclaw")


class DeviceState(Enum):
    """设备状态机"""
    IDLE = "idle"           # 空闲等待
    LISTENING = "listening" # 监听唤醒
    ACTIVE = "active"       # 激活状态 (可接收指令)
    PROCESSING = "processing"  # 处理中
    SPEAKING = "speaking"   # 播报中
    ERROR = "error"         # 错误状态
    SHUTDOWN = "shutdown"   # 关闭中


class ErrorCode(Enum):
    """错误代码"""
    OK = 0
    AUDIO_INIT_FAILED = 1001
    MODEL_LOAD_FAILED = 1002
    KWS_DETECT_FAILED = 1003
    ASR_TRANSCRIBE_FAILED = 1004
    LLM_INFERENCE_FAILED = 1005
    TTS_SYNTHESIS_FAILED = 1006
    SKILL_EXECUTION_FAILED = 1007
    NETWORK_ERROR = 1008
    TIMEOUT_ERROR = 1009


@dataclass
class AudioConfig:
    """音频配置 (兼容旧版，建议使用 settings.audio)"""
    sample_rate: int = 16000
    channels: int = 4
    chunk_size: int = 1600
    vad_threshold: float = 0.01
    input_device: str = "default"
    output_device: str = "default"


@dataclass
class ModelConfig:
    """模型配置 (兼容旧版，建议使用 settings.model)"""
    kws_model: str = "/models/kws.onnx"
    asr_model: str = "/models/asr.onnx"
    llm_model: str = "/models/llm.onnx"
    tts_model: str = "/models/tts.onnx"


@dataclass
class DeviceConfig:
    """设备配置 (兼容旧版，建议使用 settings)"""
    name: str = "OpenClaw Box"
    wakeword: str = "你好富迪"
    language: str = "zh"
    audio: AudioConfig = field(default_factory=AudioConfig)
    models: ModelConfig = field(default_factory=ModelConfig)


class OpenClawError(Exception):
    """OpenClaw 异常基类"""
    def __init__(self, message: str, code: ErrorCode = ErrorCode.OK):
        super().__init__(message)
        self.code = code
        self.message = message


class AudioEngine:
    """音频引擎 (Mock 实现)"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.is_initialized = False
        self._buffer = bytearray()
        
    async def initialize(self) -> bool:
        """初始化音频引擎"""
        try:
            logger.info(f"Initializing audio engine: {self.config.input_device}")
            # TODO: 实际初始化 ALSA/PyAudio
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Audio init failed: {e}")
            raise OpenClawError(f"Audio init failed: {e}", ErrorCode.AUDIO_INIT_FAILED)
    
    async def read_chunk(self) -> bytes:
        """读取音频块"""
        if not self.is_initialized:
            raise OpenClawError("Audio engine not initialized", ErrorCode.AUDIO_INIT_FAILED)
        
        # Mock: 返回静音数据
        return bytes(self.config.chunk_size * 2)  # 16-bit samples
    
    async def play(self, audio_data: bytes) -> bool:
        """播放音频"""
        logger.debug(f"Playing {len(audio_data)} bytes of audio")
        return True
    
    async def close(self):
        """关闭音频引擎"""
        self.is_initialized = False
        logger.info("Audio engine closed")


class KWSEngine:
    """唤醒词检测引擎 (Mock 实现)"""
    
    def __init__(self, model_path: str, wakeword: str):
        self.model_path = Path(model_path)
        self.wakeword = wakeword
        self.is_loaded = False
        self._confidence_threshold = 0.8
        
    async def load(self) -> bool:
        """加载模型"""
        try:
            logger.info(f"Loading KWS model: {self.model_path}")
            # TODO: 加载 ONNX/RKNN 模型
            self.is_loaded = True
            return True
        except Exception as e:
            logger.error(f"KWS model load failed: {e}")
            raise OpenClawError(f"KWS load failed: {e}", ErrorCode.MODEL_LOAD_FAILED)
    
    def detect(self, audio: bytes) -> tuple[bool, float]:
        """
        检测唤醒词
        
        Returns:
            (detected, confidence)
        """
        if not self.is_loaded:
            return False, 0.0
        
        # Mock: 随机检测 (实际应调用模型)
        # TODO: 实现 actual KWS inference
        import random
        confidence = random.random()
        detected = confidence > self._confidence_threshold
        
        return detected, confidence


class ASREngine:
    """语音识别引擎 (Mock 实现)"""
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.is_loaded = False
        
    async def load(self) -> bool:
        """加载模型"""
        logger.info(f"Loading ASR model: {self.model_path}")
        self.is_loaded = True
        return True
    
    async def transcribe(self, audio: bytes) -> str:
        """语音转文字"""
        if not self.is_loaded:
            raise OpenClawError("ASR not loaded", ErrorCode.ASR_TRANSCRIBE_FAILED)
        
        # Mock: 返回模拟文本
        # TODO: 实现 actual ASR inference
        return "请打开客厅的灯"


class LLMEngine:
    """语言模型引擎"""
    
    def __init__(self, config: settings.__class__):
        self.config = config.model
        self.is_loaded = False
        
    async def load(self) -> bool:
        """加载模型"""
        if self.config.use_local_llm and self.config.local_llm_path:
            logger.info(f"Loading local LLM: {self.config.local_llm_path}")
            # TODO: 加载 RKLLM 模型
        else:
            logger.info(f"Using cloud LLM: {self.config.llm_provider}/{self.config.llm_model}")
        
        self.is_loaded = True
        return True
    
    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """对话生成"""
        if not self.is_loaded:
            raise OpenClawError("LLM not loaded", ErrorCode.LLM_INFERENCE_FAILED)
        
        # Mock: 简单回复
        # TODO: 接入实际 LLM API (DeepSeek/Qwen)
        responses = {
            "你好": "你好！我是富迪，有什么可以帮您的？",
            "时间": "现在是下午3点。",
        }
        
        for key, value in responses.items():
            if key in message:
                return value
        
        return f"收到您的指令: {message}"


class TTSEngine:
    """语音合成引擎 (Mock 实现)"""
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.is_loaded = False
        
    async def load(self) -> bool:
        """加载模型"""
        logger.info(f"Loading TTS model: {self.model_path}")
        self.is_loaded = True
        return True
    
    async def synthesize(self, text: str) -> bytes:
        """合成语音"""
        if not self.is_loaded:
            raise OpenClawError("TTS not loaded", ErrorCode.TTS_SYNTHESIS_FAILED)
        
        # Mock: 返回模拟音频数据
        # TODO: 实现 actual TTS inference
        sample_count = len(text) * 100  # 简单模拟
        return bytes(sample_count * 2)


@dataclass
class Intent:
    """意图解析结果"""
    skill: str
    parameters: Dict[str, Any]
    confidence: float = 1.0
    raw_text: str = ""


class OpenClawMiddleware:
    """
    OpenClaw 中间件
    
    连接 NPU 算力、语音 IO、本地技能与云端生态
    
    Example:
        ```python
        config = DeviceConfig()
        openclaw = OpenClawMiddleware(config)
        await openclaw.initialize()
        await openclaw.start()
        ```
    """
    
    def __init__(self, config: Optional[DeviceConfig] = None):
        self.config = config or DeviceConfig()
        self.state = DeviceState.IDLE
        
        # 引擎
        self.audio: Optional[AudioEngine] = None
        self.kws: Optional[KWSEngine] = None
        self.asr: Optional[ASREngine] = None
        self.llm: Optional[LLMEngine] = None
        self.tts: Optional[TTSEngine] = None
        
        # 技能注册表
        self.local_skills: Dict[str, Callable] = {}
        self._skill_schemas: Dict[str, Dict] = {}
        
        # 状态
        self.is_running = False
        self._shutdown_event = asyncio.Event()
        
        # 对话上下文
        self._conversation_history: List[Dict] = []
        self._max_history = 10
        
        # 统计
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "wakeword_triggers": 0,
        }
    
    async def initialize(self) -> bool:
        """
        初始化中间件
        
        Returns:
            bool: 初始化是否成功
        """
        logger.info(f"🚀 Initializing {self.config.name} v{settings.app_version}")
        
        try:
            # 1. 初始化音频引擎
            self.audio = AudioEngine(self.config.audio)
            await self.audio.initialize()
            
            # 2. 加载 KWS 模型
            self.kws = KWSEngine(
                self.config.models.kws_model,
                self.config.wakeword
            )
            await self.kws.load()
            
            # 3. 加载 ASR 模型
            self.asr = ASREngine(self.config.models.asr_model)
            await self.asr.load()
            
            # 4. 加载 LLM 引擎
            self.llm = LLMEngine(settings)
            await self.llm.load()
            
            # 5. 加载 TTS 模型
            self.tts = TTSEngine(self.config.models.tts_model)
            await self.tts.load()
            
            # 6. 注册技能
            self._register_default_skills()
            
            self.state = DeviceState.IDLE
            logger.info(f"✅ {self.config.name} initialized successfully!")
            return True
            
        except OpenClawError as e:
            logger.error(f"❌ Initialization failed: {e.message} (code={e.code.value})")
            self.state = DeviceState.ERROR
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during initialization: {e}")
            self.state = DeviceState.ERROR
            raise OpenClawError(f"Initialization failed: {e}", ErrorCode.OK)
    
    def _register_default_skills(self):
        """注册默认技能"""
        skills = [
            ("light_control", self._skill_light_control, "灯光控制"),
            ("volume_control", self._skill_volume_control, "音量控制"),
            ("get_time", self._skill_get_time, "获取时间"),
            ("get_weather", self._skill_get_weather, "获取天气"),
            ("chat", self._skill_chat, "通用对话"),
        ]
        
        for name, handler, desc in skills:
            if name in settings.enabled_skills or name == "chat":
                self.register_skill(name, handler, {"description": desc})
                logger.debug(f"Registered skill: {name} ({desc})")
    
    def register_skill(
        self,
        name: str,
        handler: Callable,
        schema: Optional[Dict] = None
    ):
        """
        注册本地技能
        
        Args:
            name: 技能名称
            handler: 处理函数
            schema: 技能 Schema (参数定义等)
        """
        self.local_skills[name] = handler
        self._skill_schemas[name] = schema or {}
        logger.info(f"📝 Registered skill: {name}")
    
    def unregister_skill(self, name: str):
        """注销技能"""
        self.local_skills.pop(name, None)
        self._skill_schemas.pop(name, None)
        logger.info(f"🗑️ Unregistered skill: {name}")
    
    async def start(self):
        """启动主循环"""
        self.is_running = True
        self.state = DeviceState.LISTENING
        self._shutdown_event.clear()
        
        logger.info("🎯 Starting main loop...")
        logger.info(f"   Wakeword: '{self.config.wakeword}'")
        logger.info(f"   Listening... (Press Ctrl+C to stop)")
        
        try:
            while self.is_running and not self._shutdown_event.is_set():
                await self._main_loop_iteration()
                
        except asyncio.CancelledError:
            logger.info("Main loop cancelled")
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            self.state = DeviceState.ERROR
            raise
    
    async def _main_loop_iteration(self):
        """主循环单次迭代"""
        try:
            # 1. 音频采集
            audio_chunk = await self.audio.read_chunk()
            
            # 2. VAD + KWS 检测
            if self.state == DeviceState.LISTENING:
                detected, confidence = self.kws.detect(audio_chunk)
                
                if detected:
                    logger.info(f"🎤 Wakeword detected! (confidence={confidence:.2f})")
                    self._stats["wakeword_triggers"] += 1
                    self.state = DeviceState.ACTIVE
                    await self._handle_activation()
            
            # 短暂休眠避免 CPU 占用过高
            await asyncio.sleep(0.01)
            
        except OpenClawError as e:
            logger.error(f"Loop error: {e.message}")
            await self._handle_error(e)
        except Exception as e:
            logger.error(f"Unexpected loop error: {e}")
            await self._handle_error(OpenClawError(str(e)))
    
    async def _handle_activation(self):
        """处理唤醒激活"""
        try:
            # 播放提示音 (可选)
            await self._play_beep()
            
            # 收集语音指令
            audio_buffer = bytearray()
            silence_count = 0
            max_silence = 30  # 约 300ms 静音视为结束
            
            logger.info("👂 Listening for command...")
            
            while silence_count < max_silence and self.is_running:
                chunk = await self.audio.read_chunk()
                audio_buffer.extend(chunk)
                
                # 简单 VAD (实际应使用 webrtcvad)
                # Mock: 假设一定时间后自动结束
                silence_count += 1
                await asyncio.sleep(0.01)
            
            # 处理指令
            await self._process_command(bytes(audio_buffer))
            
        except Exception as e:
            logger.error(f"Activation handling error: {e}")
        finally:
            self.state = DeviceState.LISTENING
    
    async def _process_command(self, audio: bytes):
        """处理语音指令"""
        self.state = DeviceState.PROCESSING
        self._stats["total_requests"] += 1
        
        try:
            # 1. ASR 转写
            text = await self.asr.transcribe(audio)
            logger.info(f"📝 ASR: '{text}'")
            
            # 2. 意图解析
            intent = await self._parse_intent(text)
            
            # 3. 执行技能
            if intent.skill in self.local_skills:
                result = await self._execute_skill(intent)
                await self._speak(result)
                self._stats["successful_requests"] += 1
            else:
                # 未识别的意图，使用通用对话
                response = await self.llm.chat(text)
                await self._speak(response)
                self._stats["successful_requests"] += 1
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            self._stats["failed_requests"] += 1
            await self._speak("抱歉，处理指令时出错了，请重试。")
        finally:
            self.state = DeviceState.IDLE
    
    async def _parse_intent(self, text: str) -> Intent:
        """
        解析用户意图
        
        目前使用简单规则，未来可接入意图分类模型
        """
        text_lower = text.lower()
        
        # 灯光控制
        if any(kw in text_lower for kw in ["灯", "光", "亮"]):
            action = "on" if any(kw in text_lower for kw in ["开", "亮"]) else "off"
            target = "客厅灯" if "客厅" in text else "卧室灯" if "卧室" in text else "灯"
            return Intent(
                skill="light_control",
                parameters={"action": action, "target": target},
                raw_text=text
            )
        
        # 音量控制
        if any(kw in text_lower for kw in ["音量", "声音", "大声", "小声"]):
            if any(kw in text_lower for kw in ["大", "高", "增"]):
                return Intent(
                    skill="volume_control",
                    parameters={"action": "increase"},
                    raw_text=text
                )
            elif any(kw in text_lower for kw in ["小", "低", "减", "降"]):
                return Intent(
                    skill="volume_control",
                    parameters={"action": "decrease"},
                    raw_text=text
                )
        
        # 时间查询
        if any(kw in text_lower for kw in ["时间", "几点", "时候"]):
            return Intent(skill="get_time", parameters={}, raw_text=text)
        
        # 天气查询
        if any(kw in text_lower for kw in ["天气", "温度", "下雨"]):
            return Intent(skill="get_weather", parameters={"location": "本地"}, raw_text=text)
        
        # 默认：通用对话
        return Intent(skill="chat", parameters={"message": text}, raw_text=text)
    
    async def _execute_skill(self, intent: Intent) -> str:
        """执行技能"""
        handler = self.local_skills.get(intent.skill)
        
        if not handler:
            return f"抱歉，暂时不支持 '{intent.skill}' 功能"
        
        try:
            result = await handler(intent.parameters)
            return result
        except Exception as e:
            logger.error(f"Skill execution error: {e}")
            raise OpenClawError(f"Skill failed: {e}", ErrorCode.SKILL_EXECUTION_FAILED)
    
    async def _speak(self, text: str):
        """语音播报"""
        self.state = DeviceState.SPEAKING
        logger.info(f"🔊 TTS: '{text}'")
        
        try:
            # 合成语音
            audio = await self.tts.synthesize(text)
            # 播放
            await self.audio.play(audio)
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            self.state = DeviceState.IDLE
    
    async def _play_beep(self):
        """播放提示音"""
        # Mock: 实际应播放 WAV 文件
        logger.debug("Playing beep...")
    
    async def _handle_error(self, error: OpenClawError):
        """处理错误"""
        logger.error(f"Error handled: {error.message} (code={error.code.value})")
        
        # 尝试恢复
        if error.code in [ErrorCode.AUDIO_INIT_FAILED, ErrorCode.MODEL_LOAD_FAILED]:
            logger.warning("Critical error, attempting recovery...")
            # 可以实现重连逻辑
    
    async def stop(self):
        """优雅停止"""
        logger.info("🛑 Stopping OpenClaw...")
        self.is_running = False
        self._shutdown_event.set()
        self.state = DeviceState.SHUTDOWN
        
        if self.audio:
            await self.audio.close()
        
        logger.info("✅ OpenClaw stopped")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self._stats,
            "state": self.state.value,
            "registered_skills": list(self.local_skills.keys()),
        }
    
    # ===== 默认技能实现 =====
    
    async def _skill_light_control(self, params: Dict) -> str:
        """灯光控制技能"""
        action = params.get("action", "on")
        target = params.get("target", "灯")
        action_text = "打开" if action == "on" else "关闭"
        return f"已{action_text}{target}"
    
    async def _skill_volume_control(self, params: Dict) -> str:
        """音量控制技能"""
        action = params.get("action", "set")
        value = params.get("value", "50")
        
        action_map = {
            "increase": "调高",
            "decrease": "调低",
            "set": "设置为",
            "mute": "静音",
        }
        action_text = action_map.get(action, action)
        return f"音量已{action_text}{value if action == 'set' else ''}"
    
    async def _skill_get_time(self, params: Dict) -> str:
        """获取时间技能"""
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%Y年%m月%d日")
        weekday = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
        return f"现在是{date_str} 星期{weekday} {time_str}"
    
    async def _skill_get_weather(self, params: Dict) -> str:
        """获取天气技能 (Mock)"""
        location = params.get("location", "本地")
        # TODO: 接入实际天气 API
        return f"{location}今天晴，温度 18-25°C，适宜出行。"
    
    async def _skill_chat(self, params: Dict) -> str:
        """通用对话技能"""
        message = params.get("message", "")
        return await self.llm.chat(message)


# 主入口
async def main():
    """主函数"""
    config = DeviceConfig(
        name=settings.device_name,
        wakeword=settings.wakeword
    )
    
    openclaw = OpenClawMiddleware(config)
    
    try:
        await openclaw.initialize()
        await openclaw.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        await openclaw.stop()
        
        # 打印统计
        stats = openclaw.get_stats()
        logger.info(f"📊 Session stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
