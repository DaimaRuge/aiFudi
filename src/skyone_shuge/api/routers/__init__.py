from .documents import router as documents
from .categories import router as categories
from .search import router as search
from .health import router as health
from .auth import router as auth

__all__ = ["documents", "categories", "search", "health", "auth"]
