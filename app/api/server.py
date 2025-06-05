from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exceptions import add_exceptions
from app.api.routers import add_routers
from app.core.containers import Container, provide_wire
from app.plugins.health_check import create_health_router
from app.settings import get_app_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initiate application startup and shutdown events.

    Note: Make sure that startup and shutdown are called on
          the same object, e.g. a singleton instance.
    """
    # container: Container = app.state.container

    yield
    # Clean up


@lru_cache
def create_app(container: Container):
    app_config = container.config().app
    app = FastAPI(
        title="app-update-service",
        lifespan=lifespan,
        root_path=app_config.root_path,
        openapi_url=app_config.openapi_url,
        version=get_app_version(),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    provide_wire()

    add_exceptions(app)
    add_routers(app)

    hc_router = create_health_router(
        title=app_config.name,
        health_checks=[container.db()],
        version=get_app_version(),
    )
    app.include_router(hc_router, prefix="/service")
    app.state.container = container

    return app
