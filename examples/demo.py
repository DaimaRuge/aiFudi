#!/usr/bin/env python3
"""
Fudi VoiceOS - 完整示例

演示完整语音交互流程
"""

import asyncio
from src.aifudi.gateway.super_gateway import SuperGateway
from src.aifudi.core.llm.router import LLMRouter, ContextManager


async def demo_conversation():
    """演示对话流程"""
    
    print("=" * 60)
    print("🌟 Fudi VoiceOS 对话演示")
    print("=" * 60)
    
    # 初始化组件
    gateway = SuperGateway()
    router = LLMRouter()
    context = ContextManager()
    
    # 示例对话
    conversations = [
        "把客厅灯打开",
        "我有点冷，想看轻松的电影",
        "周末去露营，帮我查查合肥天气，放点巴赫的音乐",
        "明天早上8点叫我起床",
        "帮我订一张去北京的高铁票"
    ]
    
    for user_input in conversations:
        print(f"\n👤 用户: {user_input}")
        print("-" * 40)
        
        # 1. 路由决策
        decision = await router.route(user_input, context.get_context())
        print(f"🧠 路由: {decision.recommended_model.value}")
        print(f"   复杂度: {decision.complexity.value}")
        print(f"   推理: {decision.reasoning}")
        
        # 2. 处理请求
        result = await gateway.process(user_input, context.get_context())
        
        print(f"✅ 结果: {result.result}")
        print(f"⏱️ 耗时: {result.execution_time_ms:.0f}ms")
        
        # 3. 更新上下文
        await context.add("user", user_input)
        await context.add("assistant", result.result.get("message", ""))
    
    print("\n" + "=" * 60)
    print("🎉 演示完成!")
    print("=" * 60)


async def demo_gateway_tools():
    """演示 Gateway 工具注册"""
    
    print("\n📦 Gateway 工具演示")
    print("-" * 40)
    
    gateway = SuperGateway()
    
    # 查看已注册工具
    tools = gateway.tool_registry.tools
    print(f"已注册工具: {len(tools)} 个")
    for name in tools:
        print(f"  - {name}")


async def demo_router():
    """演示路由器"""
    
    print("\n🧠 Router 演示")
    print("-" * 40)
    
    router = LLMRouter()
    
    test_cases = [
        ("打开客厅灯", "简单设备控制"),
        ("现在几点了", "简单查询"),
        ("帮我查天气", "云端查询"),
        ("周末去露营，帮我规划一下", "复杂任务"),
        ("分析一下最新的AI新闻", "复杂任务")
    ]
    
    for query, description in test_cases:
        decision = await router.route(query)
        print(f"\n输入: {query}")
        print(f"类型: {description}")
        print(f"路由: {decision.complexity.value} -> {decision.recommended_model.value}")


if __name__ == "__main__":
    asyncio.run(demo_conversation())
    asyncio.run(demo_gateway_tools())
    asyncio.run(demo_router())
