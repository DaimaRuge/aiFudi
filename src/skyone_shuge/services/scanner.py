"""
天一阁 - 文档扫描服务

扫描文件系统，检测文档变更，提取元数据
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import fitz  # PyMuPDF
import docx
from ..models import Document
from ..core.config import settings


class DocumentScanner:
    """文档扫描服务"""
    
    # 支持的扩展名
    SUPPORTED_EXTENSIONS = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".ppt": "application/vnd.ms-powerpoint",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
    }
    
    def __init__(self):
        pass
    
    def is_supported(self, extension: str) -> bool:
        """检查是否支持该扩展名"""
        return extension.lower() in self.SUPPORTED_EXTENSIONS
    
    def scan_directory(
        self,
        path: str,
        recursive: bool = True,
        extensions: List[str] = None
    ) -> List[Dict]:
        """
        扫描目录
        
        Args:
            path: 目录路径
            recursive: 是否递归扫描
            extensions: 扫描的扩展名列表
            
        Returns:
            List[Dict]: 扫描结果
        """
        
        results = []
        base_path = Path(path)
        
        if not base_path.exists():
            return results
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                if self.is_supported(ext):
                    if extensions is None or ext in extensions:
                        results.append(self._scan_file(file_path))
        
        return results
    
    def _scan_file(self, file_path: Path) -> Dict:
        """扫描单个文件"""
        
        file_stat = file_path.stat()
        
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_stat.st_size,
            "extension": file_path.suffix.lower(),
            "file_type": self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower()),
            "modified_at": datetime.fromtimestamp(file_path.st_mtime),
            "metadata": self._extract_metadata(file_path)
        }
    
    def _extract_metadata(self, file_path: Path) -> Dict:
        """提取文件元数据"""
        
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            return self._extract_pdf_metadata(file_path)
        elif ext == ".docx":
            return self._extract_docx_metadata(file_path)
        elif ext == ".md":
            return self._extract_markdown_metadata(file_path)
        else:
            return {"title": file_path.stem}
    
    def _extract_pdf_metadata(self, file_path: Path) -> Dict:
        """提取 PDF 元数据"""
        
        try:
            doc = fitz.open(str(file_path))
            metadata = doc.metadata
            
            # 提取文本
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            
            doc.close()
            
            return {
                "title": metadata.get("title") or file_path.stem,
                "authors": [metadata.get("author")] if metadata.get("author") else [],
                "page_count": len(doc) if 'doc' in locals() else 0,
                "content_text": text_content.strip()[:50000]
            }
        except Exception as e:
            return {"title": file_path.stem}
    
    def _extract_docx_metadata(self, file_path: Path) -> Dict:
        """提取 DOCX 元数据"""
        
        try:
            doc = docx.Document(str(file_path))
            
            # 提取段落
            paragraphs = [p.text for p in doc.paragraphs]
            text_content = "\n".join(paragraphs)
            
            # 属性
            core_props = doc.core_properties
            
            return {
                "title": core_props.title or file_path.stem,
                "authors": [core_props.author] if core_props.author else [],
                "content_text": text_content.strip()[:50000]
            }
        except Exception as e:
            return {"title": file_path.stem}
    
    def _extract_markdown_metadata(self, file_path: Path) -> Dict:
        """提取 Markdown 元数据"""
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取标题 (第一个 # 开头的内容)
            title = file_path.stem
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            
            return {
                "title": title,
                "content_text": content[:50000]
            }
        except Exception as e:
            return {"title": file_path.stem}
    
    @staticmethod
    def compute_hash(file_path: str) -> str:
        """计算文件 SHA-256 哈希"""
        
        sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
