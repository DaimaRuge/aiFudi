"""
天一阁 - 机器学习模块
"""

from .embedding import (
    EmbeddingService,
    get_embedding_service
)

from .vector_db import (
    VectorDB,
    get_vector_db
)

from .llm import (
    LLMService,
    get_llm
)

from .rag import (
    RAGEngine,
    get_rag_engine,
    RAGResponse,
    RetrievedDocument,
    RetrievalStrategy,
    RerankStrategy
)

__all__ = [
    # Embedding
    "EmbeddingService",
    "get_embedding_service",
    
    # Vector DB
    "VectorDB",
    "get_vector_db",
    
    # LLM
    "LLMService",
    "get_llm",
    
    # RAG
    "RAGEngine",
    "get_rag_engine",
    "RAGResponse",
    "RetrievedDocument",
    "RetrievalStrategy",
    "RerankStrategy",
]
