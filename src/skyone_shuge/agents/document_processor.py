"""
天一阁 - 文档处理 Agent
"""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import hashlib
import mimetypes

from . import BaseAgent, AgentType, register_agent
from ..core.config import settings

logger = logging.getLogger(__name__)


@register_agent
class DocumentProcessorAgent(BaseAgent):
    """
    文档处理 Agent
    
    负责文档的解析、文本提取和预处理。
    """
    
    name = "document_processor"
    description = "文档解析和预处理 Agent"
    agent_type = AgentType.PROCESSING
    version = "3.0.1"
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = settings.ALLOWED_EXTENSIONS
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文档处理
        
        Args:
            input_data: 包含 file_path 的字典
            
        Returns:
            处理结果
        """
        file_path = input_data.get("file_path")
        if not file_path:
            raise ValueError("缺少 file_path 参数")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"开始处理文档: {file_path}")
        
        # 1. 计算文件哈希
        file_hash = self._compute_file_hash(file_path)
        
        # 2. 获取文件信息
        file_info = self._get_file_info(file_path, file_hash)
        
        # 3. 提取文本内容
        content = await self._extract_content(file_path, file_info["extension"])
        
        # 4. 提取元数据
        metadata = self._extract_metadata(file_path, file_info, content)
        
        result = {
            "success": True,
            "file_info": file_info,
            "content": content,
            "metadata": metadata,
        }
        
        logger.info(f"文档处理完成: {file_path}")
        return result
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_file_info(self, file_path: Path, file_hash: str) -> Dict[str, Any]:
        """获取文件基本信息"""
        stat = file_path.stat()
        extension = file_path.suffix.lower().lstrip(".")
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            "file_path": str(file_path.absolute()),
            "file_name": file_path.name,
            "file_hash": file_hash,
            "file_size": stat.st_size,
            "extension": extension,
            "mime_type": mime_type or "application/octet-stream",
        }
    
    async def _extract_content(self, file_path: Path, extension: str) -> Dict[str, Any]:
        """
        提取文档内容
        
        根据文件类型选择合适的解析器
        """
        # 这里简化处理，实际项目中需要根据不同文件类型使用不同的解析库
        # 比如: PyPDF2 用于 PDF, python-docx 用于 Word 等
        
        content_text = ""
        content_html = ""
        
        try:
            if extension == "txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content_text = f.read()
            elif extension == "md":
                with open(file_path, "r", encoding="utf-8") as f:
                    content_text = f.read()
                    # 简单的 Markdown 转 HTML（实际项目可以使用 markdown 库）
                    content_html = f"<pre>{content_text}</pre>"
            else:
                # 其他文件类型暂时读取为二进制或使用占位符
                content_text = f"[Binary file: {extension}]"
                
        except Exception as e:
            logger.warning(f"内容提取失败，使用默认处理: {e}")
            content_text = f"[Content extraction failed: {str(e)}]"
        
        return {
            "text": content_text,
            "html": content_html,
        }
    
    def _extract_metadata(
        self, 
        file_path: Path, 
        file_info: Dict[str, Any], 
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        提取元数据
        
        包括标题、作者、关键词等
        """
        # 简单的元数据提取
        text = content.get("text", "")
        title = file_info["file_name"]
        
        # 尝试从文件名中提取标题
        if "." in title:
            title = ".".join(title.split(".")[:-1])
        
        # 简单的关键词提取（按词频）
        keywords = self._extract_keywords(text)
        
        return {
            "title": title,
            "authors": [],
            "abstract": text[:500] if text else "",
            "keywords": keywords,
            "language": "zh" if any("\u4e00" <= c <= "\u9fff" for c in text[:100]) else "en",
        }
    
    def _extract_keywords(self, text: str, max_count: int = 10) -> List[str]:
        """简单的关键词提取"""
        if not text or len(text) < 10:
            return []
        
        # 这里简化处理，实际项目可以使用 jieba, spaCy 等 NLP 库
        # 暂时返回空列表
        return []
