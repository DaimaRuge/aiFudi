from .documents import router as documents
from .categories import router as categories
from .search import router as search
from .health import router as health
from .auth import router as auth
from .advanced_search import router as advanced_search
from .batch import router as batch
from .rag import router as rag
from .tasks import router as tasks
from .analytics import router as analytics
from .models import router as models

__all__ = [
    "documents", "categories", "search", "health", "auth",
    "advanced_search", "batch", "rag", "tasks", "analytics", "models"
]