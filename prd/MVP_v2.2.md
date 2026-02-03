# SkyOne Shuge v2.2 - 语音助手

**版本**: v2.2
**日期**: 2026-02-03

## 新增功能

### 1. 语音识别

```python
# services/voice.py

import speech_recognition as sr
from fastapi import APIRouter

router = APIRouter(prefix="/voice", tags=["语音"])

class VoiceService:
    async def recognize(self, audio_data: bytes) -> str:
        """语音识别"""
        recognizer = sr.Recognizer()
        
        audio = sr.AudioFile(audio_data)
        
        with audio as source:
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data, language='zh-CN')
        
        return text
```

### 2. 语音合成

```python
# services/tts.py

class TTSService:
    async def synthesize(self, text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> bytes:
        """语音合成"""
        # 使用 Azure TTS 或 OpenAI TTS
        pass
```

### 3. 语音命令

```python
# services/voice_commands.py

VOICE_COMMANDS = {
    "扫描文档": "scan_documents",
    "搜索": "search",
    "打开文档": "open_document",
    "分类": "classify",
    "创建分类": "create_category",
}

class VoiceCommandService:
    async def process_command(self, text: str) -> dict:
        """处理语音命令"""
        for command, action in VOICE_COMMANDS.items():
            if command in text:
                return {"action": action, "params": text.replace(command, "")}
        
        return {"action": "search", "params": text}
```

---

**版本**: v2.2
