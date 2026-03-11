"""
天一阁 - API Schemas
"""

from .auth import (
    Token,
    TokenData,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate
)

from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadRequest,
    ChunkResponse
)

from .category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse
)

from .search import (
    SearchType,
    SearchFilter,
    SearchQuery,
    SearchResult,
    SearchResponse,
    RAGQuery,
    RAGSource,
    RAGResponse,
    DocumentSuggestion,
    RelatedDocumentsResponse
)

from .health import (
    HealthStatus,
    HealthCheckResponse
)

__all__ = [
    # Auth
    "Token",
    "TokenData",
    "UserLogin",
    "UserRegister",
    "UserResponse",
    "UserUpdate",
    
    # Document
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentUploadRequest",
    "ChunkResponse",
    
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryTreeResponse",
    
    # Search
    "SearchType",
    "SearchFilter",
    "SearchQuery",
    "SearchResult",
    "SearchResponse",
    "RAGQuery",
    "RAGSource",
    "RAGResponse",
    "DocumentSuggestion",
    "RelatedDocumentsResponse",
    
    # Health
    "HealthStatus",
    "HealthCheckResponse",
]
