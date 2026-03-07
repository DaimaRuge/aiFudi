"""
OpenClaw Agent 单元测试

运行: pytest tests/test_agents.py -v
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.aifudi.agents import (
    OpenClawMiddleware,
    DeviceState,
    ErrorCode,
    OpenClawError,
    DeviceConfig,
    AudioConfig,
    Intent,
    KWSEngine,
    ASREngine,
    TTSEngine,
    LLMEngine,
)


class TestDeviceState:
    """测试设备状态"""
    
    def test_state_values(self):
        assert DeviceState.IDLE.value == "idle"
        assert DeviceState.LISTENING.value == "listening"
        assert DeviceState.PROCESSING.value == "processing"
        assert DeviceState.SPEAKING.value == "speaking"
        assert DeviceState.ERROR.value == "error"


class TestErrorCode:
    """测试错误代码"""
    
    def test_error_codes(self):
        assert ErrorCode.OK.value == 0
        assert ErrorCode.AUDIO_INIT_FAILED.value == 1001
        assert ErrorCode.MODEL_LOAD_FAILED.value == 1002


class TestOpenClawError:
    """测试异常类"""
    
    def test_error_creation(self):
        err = OpenClawError("test error", ErrorCode.AUDIO_INIT_FAILED)
        assert err.message == "test error"
        assert err.code == ErrorCode.AUDIO_INIT_FAILED
    
    def test_error_default_code(self):
        err = OpenClawError("default error")
        assert err.code == ErrorCode.OK


class TestDeviceConfig:
    """测试设备配置"""
    
    def test_default_config(self):
        config = DeviceConfig()
        assert config.name == "OpenClaw Box"
        assert config.wakeword == "你好富迪"
        assert config.language == "zh"
    
    def test_custom_config(self):
        config = DeviceConfig(
            name="Test Box",
            wakeword="Hey Fudi",
            language="en"
        )
        assert config.name == "Test Box"
        assert config.wakeword == "Hey Fudi"


@pytest.mark.asyncio
class TestOpenClawMiddleware:
    """测试 OpenClaw 中间件"""
    
    @pytest.fixture
    def config(self):
        return DeviceConfig(
            name="Test Box",
            wakeword="测试唤醒词"
        )
    
    @pytest.fixture
    def middleware(self, config):
        return OpenClawMiddleware(config)
    
    async def test_initialization(self, middleware):
        """测试初始化"""
        # Mock 所有引擎
        with patch.object(middleware, '_register_default_skills'):
            with patch('src.aifudi.agents.openclaw.AudioEngine') as mock_audio:
                with patch('src.aifudi.agents.openclaw.KWSEngine') as mock_kws:
                    with patch('src.aifudi.agents.openclaw.ASREngine') as mock_asr:
                        mock_audio_instance = AsyncMock()
                        mock_audio.return_value = mock_audio_instance
                        
                        mock_kws_instance = AsyncMock()
                        mock_kws.return_value = mock_kws_instance
                        
                        mock_asr_instance = AsyncMock()
                        mock_asr.return_value = mock_asr_instance
                        
                        # 执行初始化
                        result = await middleware.initialize()
                        
                        assert result is True
                        assert middleware.state == DeviceState.IDLE
    
    def test_skill_registration(self, middleware):
        """测试技能注册"""
        mock_handler = AsyncMock()
        schema = {"description": "Test skill"}
        
        middleware.register_skill("test_skill", mock_handler, schema)
        
        assert "test_skill" in middleware.local_skills
        assert middleware.local_skills["test_skill"] == mock_handler
        assert middleware._skill_schemas["test_skill"] == schema
    
    def test_skill_unregistration(self, middleware):
        """测试技能注销"""
        middleware.register_skill("test_skill", AsyncMock())
        middleware.unregister_skill("test_skill")
        
        assert "test_skill" not in middleware.local_skills
    
    async def test_parse_intent_light(self, middleware):
        """测试灯光意图解析"""
        intent = await middleware._parse_intent("打开客厅的灯")
        
        assert intent.skill == "light_control"
        assert intent.parameters["action"] == "on"
        assert intent.parameters["target"] == "客厅灯"
    
    async def test_parse_intent_volume_up(self, middleware):
        """测试音量增加意图"""
        intent = await middleware._parse_intent("把音量调大一点")
        
        assert intent.skill == "volume_control"
        assert intent.parameters["action"] == "increase"
    
    async def test_parse_intent_volume_down(self, middleware):
        """测试音量减小意图"""
        intent = await middleware._parse_intent("音量调小")
        
        assert intent.skill == "volume_control"
        assert intent.parameters["action"] == "decrease"
    
    async def test_parse_intent_time(self, middleware):
        """测试时间查询意图"""
        intent = await middleware._parse_intent("现在几点了")
        
        assert intent.skill == "get_time"
    
    async def test_parse_intent_weather(self, middleware):
        """测试天气查询意图"""
        intent = await middleware._parse_intent("今天天气怎么样")
        
        assert intent.skill == "get_weather"
    
    async def test_parse_intent_chat(self, middleware):
        """测试通用对话意图"""
        intent = await middleware._parse_intent("随便聊聊")
        
        assert intent.skill == "chat"
    
    async def test_skill_light_control(self, middleware):
        """测试灯光控制技能"""
        result = await middleware._skill_light_control({
            "action": "on",
            "target": "客厅灯"
        })
        assert result == "已打开客厅灯"
        
        result = await middleware._skill_light_control({
            "action": "off",
            "target": "卧室灯"
        })
        assert result == "已关闭卧室灯"
    
    async def test_skill_volume_control(self, middleware):
        """测试音量控制技能"""
        result = await middleware._skill_volume_control({
            "action": "increase"
        })
        assert "调高" in result
        
        result = await middleware._skill_volume_control({
            "action": "decrease"
        })
        assert "调低" in result
        
        result = await middleware._skill_volume_control({
            "action": "set",
            "value": "80"
        })
        assert "设置为 80" in result
    
    async def test_skill_get_time(self, middleware):
        """测试获取时间技能"""
        result = await middleware._skill_get_time({})
        
        assert "现在是" in result
        assert "年" in result
        assert "星期" in result
    
    async def test_skill_get_weather(self, middleware):
        """测试获取天气技能"""
        result = await middleware._skill_get_weather({
            "location": "北京"
        })
        
        assert "北京" in result
        assert "度" in result
    
    def test_get_stats(self, middleware):
        """测试统计信息"""
        stats = middleware.get_stats()
        
        assert "total_requests" in stats
        assert "successful_requests" in stats
        assert "failed_requests" in stats
        assert "wakeword_triggers" in stats
        assert "state" in stats
        assert "registered_skills" in stats


@pytest.mark.asyncio
class TestKWSEngine:
    """测试唤醒词引擎"""
    
    async def test_load(self):
        kws = KWSEngine("/models/kws.onnx", "你好富迪")
        result = await kws.load()
        assert result is True
        assert kws.is_loaded is True
    
    def test_detect_not_loaded(self):
        kws = KWSEngine("/models/kws.onnx", "你好富迪")
        detected, confidence = kws.detect(b"audio_data")
        assert detected is False
        assert confidence == 0.0
    
    def test_detect_loaded(self):
        kws = KWSEngine("/models/kws.onnx", "你好富迪")
        kws.is_loaded = True
        detected, confidence = kws.detect(b"audio_data")
        assert isinstance(detected, bool)
        assert 0 <= confidence <= 1


@pytest.mark.asyncio
class TestASREngine:
    """测试语音识别引擎"""
    
    async def test_load(self):
        asr = ASREngine("/models/asr.onnx")
        result = await asr.load()
        assert result is True
        assert asr.is_loaded is True
    
    async def test_transcribe(self):
        asr = ASREngine("/models/asr.onnx")
        await asr.load()
        
        result = await asr.transcribe(b"audio_data")
        assert isinstance(result, str)
        assert len(result) > 0
    
    async def test_transcribe_not_loaded(self):
        asr = ASREngine("/models/asr.onnx")
        
        with pytest.raises(OpenClawError):
            await asr.transcribe(b"audio_data")


@pytest.mark.asyncio
class TestTTSEngine:
    """测试语音合成引擎"""
    
    async def test_load(self):
        tts = TTSEngine("/models/tts.onnx")
        result = await tts.load()
        assert result is True
        assert tts.is_loaded is True
    
    async def test_synthesize(self):
        tts = TTSEngine("/models/tts.onnx")
        await tts.load()
        
        result = await tts.synthesize("你好世界")
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    async def test_synthesize_not_loaded(self):
        tts = TTSEngine("/models/tts.onnx")
        
        with pytest.raises(OpenClawError):
            await tts.synthesize("你好")


class TestIntent:
    """测试意图类"""
    
    def test_intent_creation(self):
        intent = Intent(
            skill="light_control",
            parameters={"action": "on"},
            confidence=0.95,
            raw_text="打开灯"
        )
        
        assert intent.skill == "light_control"
        assert intent.parameters["action"] == "on"
        assert intent.confidence == 0.95
        assert intent.raw_text == "打开灯"
    
    def test_intent_defaults(self):
        intent = Intent(skill="chat", parameters={})
        
        assert intent.confidence == 1.0
        assert intent.raw_text == ""
