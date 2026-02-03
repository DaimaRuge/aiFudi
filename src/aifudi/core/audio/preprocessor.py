#!/usr/bin/env python3
"""
Fudi VoiceOS - 音频前端处理

SSPE (Speech Signal Processing Engine)

功能:
- AEC (回声消除)
- VAD (语音活动检测)
- Beamforming (波束成形)
- 降噪
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class AudioChunk:
    """音频块"""
    data: np.ndarray
    sample_rate: int
    timestamp: float
    is_speech: bool = True


class VAD:
    """
    Voice Activity Detection
    
    基于 WebRTC VAD 或简单能量检测
    """
    
    def __init__(self, sample_rate: int = 16000, mode: int = 2):
        self.sample_rate = sample_rate
        self.mode = mode
        self.frame_length = int(sample_rate * 0.02)  # 20ms
    
    def detect(self, audio: np.ndarray) -> bool:
        """
        检测是否有语音
        
        Args:
            audio: 音频数据
            
        Returns:
            bool: 是否有语音
        """
        # 简单能量检测
        energy = np.mean(audio ** 2)
        threshold = 0.001  # 可调
        
        return energy > threshold
    
    def split(self, audio: np.ndarray) -> List[np.ndarray]:
        """
        分割音频为语音段
        
        Returns:
            List[AudioChunk]: 语音段列表
        """
        frames = self._frame_split(audio)
        
        speech_frames = []
        for i, frame in enumerate(frames):
            if self.detect(frame):
                speech_frames.append(frame)
        
        return speech_frames
    
    def _frame_split(self, audio: np.ndarray) -> List[np.ndarray]:
        """分帧"""
        frames = []
        
        for i in range(0, len(audio), self.frame_length):
            frame = audio[i:i + self.frame_length]
            if len(frame) == self.frame_length:
                frames.append(frame)
        
        return frames


class AEC:
    """
    Acoustic Echo Cancellation
    
    回声消除 - 消除设备自己播放的声音
    """
    
    def __init__(self, sample_rate: int = 16000, filter_length: int = 4096):
        self.sample_rate = sample_rate
        self.filter_length = filter_length
        self.reference_buffer = []
    
    def cancel(self, mic_signal: np.ndarray, reference: np.ndarray) -> np.ndarray:
        """
        消除回声
        
        Args:
            mic_signal: 麦克风信号 (包含回声)
            reference: 参考信号 (设备播放的音频)
            
        Returns:
            np.ndarray: 回声消除后的信号
        """
        # 简化的回声消除
        # 实际应使用 NLMS / APA 算法
        
        if len(reference) < len(mic_signal):
            reference = np.pad(reference, (0, len(mic_signal) - len(reference)))
        
        # 计算延迟并对齐
        correlation = np.correlate(mic_signal[:1000], reference[:1000], 'full')
        delay = np.argmax(correlation)
        
        # 对齐参考信号
        aligned_ref = np.roll(reference, -delay)
        
        # 简单的减法消除
        output = mic_signal - 0.5 * aligned_ref[:len(mic_signal)]
        
        return output


class Beamformer:
    """
    Beamforming - 波束成形
    
    声源定位 + 波束增强
    """
    
    def __init__(self, mic_positions: List[np.ndarray], sample_rate: int = 16000):
        self.mic_positions = mic_positions
        self.sample_rate = sample_rate
        self.n_mics = len(mic_positions)
    
    def process(self, signals: List[np.ndarray]) -> Tuple[np.ndarray, int]:
        """
        波束成形处理
        
        Args:
            signals: 多个麦克风的信号
            
        Returns:
            Tuple[增强后的信号, 声源方向]
        """
        if len(signals) != self.n_mics:
            raise ValueError(f"Expected {self.n_mics} signals, got {len(signals)}")
        
        # 简化的延迟-累加波束成形
        # 1. 计算到达时间差
        time_delays = self._estimate_delays(signals)
        
        # 2. 对齐并累加
        aligned_signals = self._align_and_sum(signals, time_delays)
        
        # 3. 估计声源方向
        doa = self._estimate_doa(time_delays)
        
        return aligned_signals, doa
    
    def _estimate_delays(self, signals: List[np.ndarray]) -> np.ndarray:
        """估计延迟"""
        delays = np.zeros(self.n_mics)
        
        # 使用互相关估计延迟
        for i in range(1, self.n_mics):
            correlation = np.correlate(signals[0], signals[i], 'full')
            delays[i] = np.argmax(correlation) - len(signals[0]) + 1
        
        return delays
    
    def _align_and_sum(
        self,
        signals: List[np.ndarray],
        delays: np.ndarray
    ) -> np.ndarray:
        """对齐并累加"""
        aligned = []
        
        for i, (signal, delay) in enumerate(zip(signals, delays)):
            if delay > 0:
                aligned_signal = signal[delay:]
            elif delay < 0:
                aligned_signal = np.pad(signal, (abs(delay), 0))[:len(signal)]
            else:
                aligned_signal = signal
            
            aligned.append(aligned_signal)
        
        # 累加
        min_len = min(len(s) for s in aligned)
        aligned = [s[:min_len] for s in aligned]
        output = np.sum(aligned, axis=0) / self.n_mics
        
        return output
    
    def _estimate_doa(self, delays: np.ndarray) -> int:
        """估计声源方向 (角度)"""
        speed_of_sound = 343.0  # m/s
        fs = self.sample_rate
        
        # 简化的 DOA 估计
        # 实际应使用 GCC-PHAT / MUSIC 算法
        
        angles = []
        for i in range(1, self.n_mics):
            delay_samples = delays[i]
            delay_seconds = delay_samples / fs
            
            # 假设麦克风间距 0.05m
            mic_distance = 0.05
            angle = np.degrees(np.arcsin(delay_seconds * speed_of_sound / mic_distance))
            angles.append(angle)
        
        return int(np.mean(angles)) if angles else 0


class AudioPreprocessor:
    """
    音频预处理器
    
    整合 SSPE 各个组件
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.vad = VAD(sample_rate)
        self.aec = AEC(sample_rate)
        self.beamformer = None  # 需要初始化麦克风阵列
    
    def process(
        self,
        mic_signals: List[np.ndarray],
        reference: np.ndarray = None
    ) -> AudioChunk:
        """
        完整音频处理流程
        
        Args:
            mic_signals: 多个麦克风的信号
            reference: 参考信号 (用于 AEC)
            
        Returns:
            AudioChunk: 处理后的音频
        """
        import time
        timestamp = time.time()
        
        # 1. 波束成形
        if self.beamformer and len(mic_signals) >= 2:
            beamformed, doa = self.beamformer.process(mic_signals)
        else:
            beamformed = mic_signals[0] if mic_signals else np.array([])
        
        # 2. 回声消除
        if reference is not None:
            beamformed = self.aec.cancel(beamformed, reference)
        
        # 3. VAD 检测
        is_speech = self.vad.detect(beamformed)
        
        return AudioChunk(
            data=beamformed,
            sample_rate=self.sample_rate,
            timestamp=timestamp,
            is_speech=is_speech
        )
    
    def set_mic_array(self, positions: List[np.ndarray]):
        """设置麦克风阵列配置"""
        self.beamformer = Beamformer(positions, self.sample_rate)


# 测试
if __name__ == "__main__":
    # 创建预处理器
    preprocessor = AudioPreprocessor()
    
    # 模拟 2 麦克风阵列
    mic_positions = [
        np.array([0, 0, 0]),
        np.array([0.05, 0, 0])
    ]
    preprocessor.set_mic_array(mic_positions)
    
    # 生成测试信号
    duration = 1.0
    samples = int(duration * 16000)
    
    mic1 = np.random.randn(samples) * 0.001
    mic2 = np.random.randn(samples) * 0.001
    
    # 处理
    result = preprocessor.process([mic1, mic2])
    
    print(f"✅ 音频处理测试完成")
    print(f"   样本数: {len(result.data)}")
    print(f"   语音检测: {result.is_speech}")
