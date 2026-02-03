#!/usr/bin/env python3
"""
Fudi VoiceOS - 音频 I/O

麦克风输入和扬声器输出

支持:
- ALSA 音频驱动
- 音频流处理
- 回声消除参考
"""

import asyncio
import numpy as np
from typing import AsyncIterator, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AudioChunk:
    """音频块"""
    data: bytes
    sample_rate: int
    channels: int
    timestamp: float


class BaseAudioIO(ABC):
    """音频 I/O 基类"""
    
    @abstractmethod
    async def start(self):
        """启动"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止"""
        pass
    
    @abstractmethod
    async def read_chunk(self) -> AudioChunk:
        """读取音频块"""
        pass
    
    @abstractmethod
    async def write_chunk(self, audio: bytes):
        """写入音频块"""
        pass


class MockAudioIO(BaseAudioIO):
    """
    模拟音频 I/O
    
    测试用
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = 1600
        self.is_running = False
    
    async def start(self):
        """启动"""
        self.is_running = True
        print(f"MockAudioIO started: {self.sample_rate}Hz, {self.channels} ch")
    
    async def stop(self):
        """停止"""
        self.is_running = False
        print("MockAudioIO stopped")
    
    async def read_chunk(self) -> AudioChunk:
        """读取模拟音频"""
        # 生成静音
        data = bytes(np.zeros(self.chunk_size, dtype=np.int16))
        
        return AudioChunk(
            data=data,
            sample_rate=self.sample_rate,
            channels=self.channels,
            timestamp=0.0
        )
    
    async def write_chunk(self, audio: bytes):
        """写入模拟音频"""
        pass


class AlsaAudioIO(BaseAudioIO):
    """
    ALSA 音频 I/O
    
    真实的 ALSA 驱动
    """
    
    def __init__(
        self,
        device: str = "default",
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1600
    ):
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.is_running = False
        
        # PyALSAAudio
        self.alsaudio = None
        self.pcm = None
    
    async def start(self):
        """启动"""
        try:
            import alsaaudio
            
            self.alsaudio = alsaaudio
            
            # 打开录音设备
            self.pcm = alsaaudio.PCM(
                alsaaudio.PCM_CAPTURE,
                alsaaudio.PCM_NORMAL,
                channels=self.channels,
                rate=self.sample_rate,
                format=alsaaudio.PCM_FORMAT_S16_LE,
                periodsize=self.chunk_size,
                device=self.device
            )
            
            self.is_running = True
            print(f"ALSA Audio started: {self.device}")
            
        except ImportError:
            print("PyALSAAudio not installed, using mock")
            self.is_running = True
    
    async def stop(self):
        """停止"""
        if self.pcm:
            self.pcm.close()
        self.is_running = False
        print("ALSA Audio stopped")
    
    async def read_chunk(self) -> AudioChunk:
        """读取音频"""
        if not self.is_running:
            raise RuntimeError("Audio not started")
        
        if self.pcm:
            # 真实读取
            l, data = self.pcm.read()
            if l > 0:
                return AudioChunk(
                    data=data,
                    sample_rate=self.sample_rate,
                    channels=self.channels,
                    timestamp=0.0
                )
        
        # 返回静音
        return AudioChunk(
            data=bytes(self.chunk_size * 2),
            sample_rate=self.sample_rate,
            channels=self.channels,
            timestamp=0.0
        )
    
    async def write_chunk(self, audio: bytes):
        """写入音频"""
        if self.pcm:
            self.pcm.write(audio)


class AudioStreamHandler:
    """
    音频流处理器
    
    管理音频流
    """
    
    def __init__(self, audio_io: BaseAudioIO):
        self.audio_io = audio_io
        self.listeners: List = []
        self.is_capturing = False
    
    def add_listener(self, listener):
        """添加监听器"""
        self.listeners.append(listener)
    
    async def start_capture(self):
        """开始采集"""
        self.is_capturing = True
        await self.audio_io.start()
        
        while self.is_capturing:
            chunk = await self.audio_io.read_chunk()
            
            # 通知所有监听器
            for listener in self.listeners:
                await listener(chunk)
    
    async def stop_capture(self):
        """停止采集"""
        self.is_capturing = False
        await self.audio_io.stop()
    
    async def play_audio(self, audio: bytes):
        """播放音频"""
        await self.audio_io.write_chunk(audio)


class EchoReferenceManager:
    """
    回声参考管理器
    
    追踪播放的音频用于 AEC
    """
    
    def __init__(self, max_history: int = 5):
        self.history: List[bytes] = []
        self.max_history = max_history
    
    def add(self, audio: bytes):
        """添加参考音频"""
        self.history.append(audio)
        
        # 保持历史长度
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_reference(self) -> bytes:
        """获取参考音频"""
        return b''.join(self.history)
    
    def clear(self):
        """清空"""
        self.history.clear()


# 音频工具函数
def bytes_to_float(audio: bytes) -> np.ndarray:
    """字节转浮点"""
    return np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0


def float_to_bytes(audio: np.ndarray) -> bytes:
    """浮点转字节"""
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767).astype(np.int16).tobytes()


def mix_audio(audio1: bytes, audio2: bytes) -> bytes:
    """混合两个音频"""
    a1 = bytes_to_float(audio1)
    a2 = bytes_to_float(audio2)
    
    # 长度对齐
    max_len = max(len(a1), len(a2))
    a1 = np.pad(a1, (0, max_len - len(a1)))
    a2 = np.pad(a2, (0, max_len - len(a2)))
    
    mixed = (a1 + a2) / 2
    
    return float_to_bytes(mixed)


# 测试
async def main():
    """测试音频 I/O"""
    
    print("=" * 50)
    print("Audio I/O Test")
    print("=" * 50)
    
    # 创建音频 I/O
    audio_io = MockAudioIO(
        sample_rate=16000,
        channels=1,
        chunk_size=1600
    )
    
    # 创建流处理器
    handler = AudioStreamHandler(audio_io)
    
    # 添加监听器
    async def on_chunk(chunk: AudioChunk):
        print(f"Received chunk: {len(chunk.data)} bytes")
    
    handler.add_listener(on_chunk)
    
    # 开始采集
    print("Starting capture...")
    await handler.start_capture()
    
    # 模拟运行
    await asyncio.sleep(2)
    
    # 停止
    print("Stopping...")
    await handler.stop_capture()
    
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
