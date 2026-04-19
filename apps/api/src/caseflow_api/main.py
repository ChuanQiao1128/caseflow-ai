from fastapi import FastAPI

from caseflow_api.api.routers import (
    approval_queue_router,
    checklists_router,
    email_drafts_router,
    extraction_router,
    health_router,
    organisations_router,
    retrieval_router,
    review_router,
)
from caseflow_api.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(organisations_router)
    app.include_router(retrieval_router)
    app.include_router(extraction_router)
    app.include_router(checklists_router)
    app.include_router(review_router)
    app.include_router(email_drafts_router)
    app.include_router(approval_queue_router)
    return app


app = create_app()
