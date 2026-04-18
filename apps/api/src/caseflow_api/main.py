from fastapi import FastAPI

from caseflow_api.api.routers import health_router
from caseflow_api.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    return app


app = create_app()
