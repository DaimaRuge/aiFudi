#!/usr/bin/env python3
"""
AI Fudi - 简单示例

演示如何使用 OpenClaw 中间件
"""

import asyncio
import signal
from pathlib import Path

# 添加 src 到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aifudi.agents import OpenClawMiddleware, DeviceConfig, DeviceState
from aifudi.config import settings
from aifudi.logger import get_logger

logger = get_logger("example")


async def main():
    """主函数"""
    print("=" * 60)
    print("🎙️  AI Fudi - OpenClaw 演示")
    print("=" * 60)
    print()
    
    # 配置
    config = DeviceConfig(
        name="Fudi Demo Box",
        wakeword="你好富迪",
        language="zh"
    )
    
    # 创建中间件
    openclaw = OpenClawMiddleware(config)
    
    # 注册自定义技能
    async def custom_greeting(params):
        """自定义问候技能"""
        name = params.get("name", "用户")
        return f"你好，{name}！很高兴为您服务。"
    
    openclaw.register_skill("greeting", custom_greeting, {
        "description": "问候用户",
        "parameters": {
            "name": {"type": "string", "description": "用户名称"}
        }
    })
    
    # 处理 Ctrl+C
    def signal_handler(sig, frame):
        print("\n收到中断信号，正在停止...")
        asyncio.create_task(openclaw.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 初始化
        print("🔧 正在初始化...")
        await openclaw.initialize()
        print(f"✅ 初始化完成！")
        print(f"   设备名称: {config.name}")
        print(f"   唤醒词: '{config.wakeword}'")
        print(f"   已注册技能: {list(openclaw.local_skills.keys())}")
        print()
        
        # 模拟交互 (实际应运行 openclaw.start())
        print("🎯 模拟交互模式 (实际部署时启用语音监听)")
        print("-" * 60)
        
        # 模拟意图解析测试
        test_inputs = [
            "打开客厅的灯",
            "把音量调大一点", 
            "现在几点了",
            "今天天气怎么样",
        ]
        
        for text in test_inputs:
            print(f"\n📝 输入: '{text}'")
            intent = await openclaw._parse_intent(text)
            print(f"   识别技能: {intent.skill}")
            print(f"   参数: {intent.parameters}")
            
            if intent.skill in openclaw.local_skills:
                result = await openclaw._execute_skill(intent)
                print(f"   执行结果: {result}")
        
        print()
        print("-" * 60)
        print("📊 统计信息:")
        stats = openclaw.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print()
        print("✨ 演示完成！")
        print("   实际使用时运行: await openclaw.start()")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        await openclaw.stop()


if __name__ == "__main__":
    asyncio.run(main())
