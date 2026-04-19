from caseflow_api.api.routers.checklists import router as checklists_router
from caseflow_api.api.routers.extraction import router as extraction_router
from caseflow_api.api.routers.health import router as health_router
from caseflow_api.api.routers.organisations import router as organisations_router
from caseflow_api.api.routers.retrieval import router as retrieval_router
from caseflow_api.api.routers.review import router as review_router

__all__ = [
    "checklists_router",
    "extraction_router",
    "health_router",
    "organisations_router",
    "retrieval_router",
    "review_router",
]
