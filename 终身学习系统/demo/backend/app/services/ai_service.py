"""AI 服务 - 支持 OpenAI 和模拟模式"""
from typing import Optional, List
import json
from app.core.config import settings


class MockAIService:
    """模拟 AI 服务（用于开发测试）"""

    @staticmethod
    def generate_response(message: str, context: Optional[str] = None) -> str:
        """生成模拟回复"""
        # 根据消息内容生成不同的回复
        message_lower = message.lower()

        if any(word in message_lower for word in ["你好", "hello", "hi", "您好"]):
            return "你好！我是你的学习助手，有什么可以帮助你的吗？你可以问我关于你上传的文档内容，或者让我帮你规划学习路径。"

        if any(word in message_lower for word in ["总结", "摘要", "summary"]):
            if context:
                return f"根据文档内容，主要要点如下：\n\n1. 这份文档讨论了核心概念和方法\n2. 文档提供了实用的指导和示例\n3. 内容涵盖了从基础到进阶的知识\n\n需要我详细解释某个部分吗？"
            return "请先上传文档，我可以帮你总结内容。"

        if any(word in message_lower for word in ["什么", "什么是", "what"]):
            if context:
                return f"根据文档内容，这个问题涉及以下要点：\n\n{context[:500]}...\n\n需要更详细的解释吗？"
            return "这是一个很好的问题！请上传相关文档，我可以基于文档内容给你更准确的解答。"

        if any(word in message_lower for word in ["学习", "推荐", "建议"]):
            return "基于你的学习进度，我建议：\n\n1. 先掌握基础概念\n2. 然后通过实践加深理解\n3. 定期复习巩固知识\n\n你想要针对哪个主题进行学习？"

        # 默认回复
        if context:
            return f"我理解你的问题。根据文档内容分析：\n\n{context[:300]}...\n\n这应该能回答你的问题。如果需要更多信息，请告诉我！"
        return "我理解你的问题。为了给你更准确的回答，建议你上传相关文档，这样我可以基于文档内容提供更有针对性的帮助。"

    @staticmethod
    def generate_summary(text: str) -> str:
        """生成文档摘要"""
        # 模拟摘要生成
        if len(text) < 100:
            return text

        # 提取前几句作为摘要
        sentences = text.replace("。", "。\n").split("\n")
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]

        if summary_sentences:
            return "。".join(summary_sentences) + "。"
        return text[:200] + "..."

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """提取关键词"""
        # 模拟关键词提取
        common_keywords = ["学习", "知识", "方法", "系统", "技术", "应用", "发展", "研究"]
        return common_keywords[:5]

    @staticmethod
    def generate_learning_path(topic: str, difficulty: str = "intermediate") -> dict:
        """生成学习路径"""
        units = [
            {
                "title": f"{topic} - 基础概念",
                "description": f"了解{topic}的基本概念和核心原理",
                "duration_minutes": 45,
                "difficulty": "beginner"
            },
            {
                "title": f"{topic} - 深入理解",
                "description": f"深入探讨{topic}的内部机制和工作原理",
                "duration_minutes": 60,
                "difficulty": difficulty
            },
            {
                "title": f"{topic} - 实践应用",
                "description": f"通过实际案例学习{topic}的应用场景",
                "duration_minutes": 90,
                "difficulty": difficulty
            },
            {
                "title": f"{topic} - 进阶技巧",
                "description": f"掌握{topic}的高级技巧和最佳实践",
                "duration_minutes": 60,
                "difficulty": "advanced"
            },
            {
                "title": f"{topic} - 综合练习",
                "description": f"综合运用所学知识完成{topic}相关项目",
                "duration_minutes": 120,
                "difficulty": "advanced"
            }
        ]

        return {
            "title": f"{topic} 学习路径",
            "description": f"从零开始学习{topic}，从基础到进阶的完整学习计划",
            "goal": f"掌握{topic}的核心概念和实践技能",
            "difficulty": difficulty,
            "units": units
        }


class OpenAIService:
    """OpenAI 服务"""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    async def generate_response(self, message: str, context: Optional[str] = None) -> str:
        """使用 OpenAI 生成回复"""
        if not self.client:
            return MockAIService.generate_response(message, context)

        system_prompt = """你是一个专业的学习助手，帮助用户理解文档内容、规划学习路径。
回答时要：
1. 简洁明了，避免冗长
2. 如果有文档上下文，基于文档内容回答
3. 提供有建设性的建议
4. 鼓励用户继续学习"""

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append({
                "role": "system",
                "content": f"以下是相关的文档内容：\n\n{context[:2000]}"
            })

        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 错误: {e}")
            return MockAIService.generate_response(message, context)

    async def generate_summary(self, text: str) -> str:
        """使用 OpenAI 生成摘要"""
        if not self.client:
            return MockAIService.generate_summary(text)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "请为以下内容生成一个简洁的摘要，突出主要观点："},
                    {"role": "user", "content": text[:4000]}
                ],
                max_tokens=300,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 错误: {e}")
            return MockAIService.generate_summary(text)

    async def extract_keywords(self, text: str) -> List[str]:
        """使用 OpenAI 提取关键词"""
        if not self.client:
            return MockAIService.extract_keywords(text)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "请从以下文本中提取5-10个关键词，以JSON数组格式返回。"},
                    {"role": "user", "content": text[:2000]}
                ],
                max_tokens=100,
                temperature=0.3
            )
            keywords = json.loads(response.choices[0].message.content)
            return keywords if isinstance(keywords, list) else MockAIService.extract_keywords(text)
        except Exception as e:
            print(f"OpenAI API 错误: {e}")
            return MockAIService.extract_keywords(text)

    async def generate_learning_path(self, topic: str, difficulty: str = "intermediate") -> dict:
        """使用 OpenAI 生成学习路径"""
        if not self.client:
            return MockAIService.generate_learning_path(topic, difficulty)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个教育专家。请为指定主题生成一个结构化的学习路径。
返回 JSON 格式，包含以下字段：
{
    "title": "学习路径标题",
    "description": "学习路径描述",
    "goal": "学习目标",
    "difficulty": "难度级别",
    "units": [
        {
            "title": "单元标题",
            "description": "单元描述",
            "duration_minutes": 预计时长（分钟）,
            "difficulty": "难度级别"
        }
    ]
}"""
                    },
                    {
                        "role": "user",
                        "content": f"请为主题 '{topic}' 生成一个{difficulty}级别的学习路径"
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"OpenAI API 错误: {e}")
            return MockAIService.generate_learning_path(topic, difficulty)


# 根据配置选择服务
def get_ai_service():
    """获取 AI 服务实例"""
    if settings.USE_MOCK_AI or not settings.OPENAI_API_KEY:
        return MockAIService()
    return OpenAIService()


ai_service = get_ai_service()
