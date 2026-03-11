"""
天一阁 - 业务服务层
"""

from .document_service import DocumentService, get_document_service
from .search_service import SearchService, get_search_service

__all__ = [
    "DocumentService",
    "get_document_service",
    "SearchService",
    "get_search_service",
]
