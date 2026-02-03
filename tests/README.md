# Fudi VoiceOS 测试

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单个测试
pytest tests/test_pipeline.py -v

# 查看覆盖率
pytest tests/ --cov=src --cov-report=html
```

## 测试结构

```
tests/
├── conftest.py           # 测试配置
├── test_pipeline.py      # 流水线测试
├── test_asr.py          # ASR 测试
├── test_tts.py          # TTS 测试
├── test_llm.py          # LLM 测试
├── test_gateway.py      # Gateway 测试
└── test_kws.py          # KWS 测试
```

## 单元测试

```python
# tests/test_pipeline.py

import pytest
from src.aifudi.core.pipeline import VoicePipeline, PipelineConfig


@pytest.fixture
def pipeline():
    config = PipelineConfig()
    return VoicePipeline(config)


@pytest.mark.asyncio
async def test_pipeline(pipeline):
    """测试流水线"""
    # 模拟音频
    mock_audio = bytes(32000)
    
    # 运行
    result = await pipeline.run(mock_audio)
    
    # 验证
    assert result.success is True
```

## 集成测试

```python
# tests/integration/

async def test_full_pipeline():
    """端到端测试"""
    pass
```

## Mock 数据

```
tests/fixtures/
├── audio/                # 测试音频
├── models/              # 测试模型
└── responses/           # 测试响应
```
