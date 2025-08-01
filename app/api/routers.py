from fastapi import APIRouter, FastAPI

from app.routers.update_files import update_files_router
from app.routers.update_manifest import update_manifest_router

router = APIRouter(
    tags=["app-update-service"],
)


def add_routers(app: FastAPI):
    routers = [
        update_files_router,
        update_manifest_router,
    ]
    _add_routers(app, routers)


def _add_routers(app: FastAPI, routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)
