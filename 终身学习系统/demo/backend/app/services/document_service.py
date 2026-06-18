"""文档处理服务"""
import os
import re
from typing import Optional, List
from pathlib import Path
import aiofiles
from PyPDF2 import PdfReader
from docx import Document
import chardet

from app.core.config import settings


class DocumentService:
    """文档处理服务"""

    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """检查文件类型是否允许"""
        ext = Path(filename).suffix.lower()
        return ext in cls.ALLOWED_EXTENSIONS

    @classmethod
    def get_file_extension(cls, filename: str) -> str:
        """获取文件扩展名"""
        return Path(filename).suffix.lower()

    @classmethod
    async def parse_pdf(cls, file_path: str) -> str:
        """解析 PDF 文件"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF 解析失败: {str(e)}")

    @classmethod
    async def parse_txt(cls, file_path: str) -> str:
        """解析 TXT 文件"""
        try:
            # 检测编码
            async with aiofiles.open(file_path, 'rb') as f:
                raw_data = await f.read()

            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8') or 'utf-8'

            try:
                text = raw_data.decode(encoding)
            except UnicodeDecodeError:
                text = raw_data.decode('utf-8', errors='ignore')

            return text.strip()
        except Exception as e:
            raise ValueError(f"TXT 解析失败: {str(e)}")

    @classmethod
    async def parse_docx(cls, file_path: str) -> str:
        """解析 DOCX 文件"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX 解析失败: {str(e)}")

    @classmethod
    async def parse_document(cls, file_path: str, file_ext: str) -> str:
        """根据文件类型解析文档"""
        if file_ext == ".pdf":
            return await cls.parse_pdf(file_path)
        elif file_ext == ".txt":
            return await cls.parse_txt(file_path)
        elif file_ext == ".docx":
            return await cls.parse_docx(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")

    @classmethod
    def count_words(cls, text: str) -> int:
        """统计字数（支持中英文）"""
        # 移除空白字符
        text = text.strip()
        if not text:
            return 0

        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

        # 统计英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))

        return chinese_chars + english_words

    @classmethod
    def split_into_chunks(cls, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """将文本分割成块"""
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            # 如果不是最后一块，尝试在句子边界分割
            if end < text_length:
                # 查找最近的句号、问号或感叹号
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '。！？.!?\n':
                        end = i + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap if end < text_length else text_length

        return chunks

    @classmethod
    def estimate_page_count(cls, text: str) -> int:
        """估算页数（假设每页约 500 字）"""
        word_count = cls.count_words(text)
        return max(1, word_count // 500)

    @classmethod
    def generate_summary(cls, text: str, max_length: int = 200) -> str:
        """生成简单摘要（取前 N 个字符）"""
        if not text:
            return ""

        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) <= max_length:
            return text

        # 在句子边界截断
        truncated = text[:max_length]
        for i in range(len(truncated) - 1, max(0, len(truncated) - 50), -1):
            if truncated[i] in '。！？.!?' and i > max_length * 0.5:
                return truncated[:i + 1] + "..."

        return truncated + "..."


# 创建实例
document_service = DocumentService()
