import os
import logging
from typing import List, Dict, Any, Optional
import httpx
from openai import OpenAI
import time

from models import ChatMessage
from vector_store import knowledge_retriever

logger = logging.getLogger(__name__)


class AIService:
    """AI服务，集成DeepSeek API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        
        if self.api_key:
            # 使用OpenAI兼容的客户端
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            logger.info("DeepSeek API客户端初始化成功")
        else:
            self.client = None
            logger.warning("未提供DeepSeek API密钥，将使用模拟响应")
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         temperature: float = 0.7) -> str:
        """生成AI响应"""
        if not self.client:
            # 模拟响应
            return "这是一个模拟响应。请设置DEEPSEEK_API_KEY环境变量以使用真实的DeepSeek API。"
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI响应生成失败: {e}")
            return f"抱歉，生成响应时出现错误: {str(e)}"
    
    def answer_with_context(self, question: str, context: str) -> str:
        """基于上下文回答问题"""
        system_prompt = """你是一个知识渊博的AI助手，基于提供的上下文信息回答问题。
        如果上下文中有相关信息，请基于上下文回答。
        如果上下文中没有相关信息，请基于你的知识回答，但要说明这不是基于提供的上下文。
        请保持回答准确、有帮助。"""
        
        user_prompt = f"""上下文信息：
{context}

问题：{question}

请基于上面的上下文信息回答问题："""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_response(messages)
    
    def rag_answer(self, question: str, max_context_chunks: int = 3) -> Dict[str, Any]:
        """检索增强生成（RAG）回答"""
        start_time = time.time()
        
        # 1. 检索相关文档分块
        relevant_chunks = knowledge_retriever.retrieve_relevant_chunks(
            question, 
            limit=max_context_chunks
        )
        
        # 2. 构建上下文
        context = knowledge_retriever.build_context(question, max_chunks=max_context_chunks)
        
        # 3. 生成回答
        answer = self.answer_with_context(question, context)
        
        processing_time = time.time() - start_time
        
        return {
            "answer": answer,
            "context": context,
            "sources": relevant_chunks,
            "processing_time": processing_time
        }
    
    def summarize_document(self, text: str, max_length: int = 500) -> str:
        """总结文档内容"""
        system_prompt = "你是一个专业的文档总结助手，请用简洁的语言总结文档的核心内容。"
        
        user_prompt = f"""请总结以下文档内容，总结长度不超过{max_length}字：

{text[:5000]}  # 限制输入长度

总结："""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_response(messages)
    
    def extract_key_points(self, text: str) -> List[str]:
        """提取关键点"""
        system_prompt = "你是一个信息提取专家，请从文档中提取关键点。"
        
        user_prompt = f"""请从以下文档中提取3-5个关键点，每个关键点用一句话描述：

{text[:3000]}

关键点："""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.generate_response(messages)
        
        # 解析响应为列表
        key_points = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                # 清理标记
                clean_line = line.lstrip('-• ').lstrip('1234567890. ')
                if clean_line:
                    key_points.append(clean_line)
        
        return key_points if key_points else [response]
    
    def chat_conversation(self, messages: List[ChatMessage], 
                         use_rag: bool = False) -> ChatMessage:
        """对话式交互"""
        # 转换为OpenAI格式
        openai_messages = []
        for msg in messages[-10:]:  # 只保留最近10条消息
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        if use_rag and messages:
            # 使用RAG增强最后一条用户消息
            last_user_message = None
            for msg in reversed(messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if last_user_message:
                rag_result = self.rag_answer(last_user_message)
                response_content = rag_result["answer"]
                
                # 创建助手消息
                assistant_message = ChatMessage(
                    role="assistant",
                    content=response_content
                )
                return assistant_message
        
        # 普通对话
        response_content = self.generate_response(openai_messages)
        
        # 创建助手消息
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content
        )
        
        return assistant_message


class MockAIService:
    """模拟AI服务，用于测试"""
    
    def __init__(self):
        logger.info("使用模拟AI服务")
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         temperature: float = 0.7) -> str:
        """生成模拟响应"""
        # 提取最后一条用户消息
        last_user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        responses = [
            f"我理解你想了解：{last_user_message}。基于我的知识，这是一个重要的学习主题。",
            "这是一个很好的问题！让我为你解释一下相关概念。",
            "根据你提供的上下文，我可以给出以下分析：这是一个值得深入研究的领域。",
            "我注意到你在询问关于学习系统的问题。终身学习确实非常重要。",
            "让我为你总结一下关键信息：持续学习是个人成长的关键。"
        ]
        
        import random
        return random.choice(responses)
    
    def rag_answer(self, question: str, max_context_chunks: int = 3) -> Dict[str, Any]:
        """模拟RAG回答"""
        return {
            "answer": f"基于检索到的信息，我对'{question}'的回答是：这是一个很好的学习主题，建议你深入研究相关文档。",
            "context": "模拟上下文信息",
            "sources": [
                {"text": "模拟文档内容1", "score": 0.95},
                {"text": "模拟文档内容2", "score": 0.88}
            ],
            "processing_time": 0.5
        }


# 根据是否配置API密钥选择服务
def get_ai_service() -> AIService:
    """获取AI服务实例"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        return AIService(api_key)
    else:
        # 返回模拟服务或真实服务（根据配置）
        return MockAIService()


# 单例实例
ai_service = get_ai_service()