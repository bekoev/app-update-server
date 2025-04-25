from fastapi import APIRouter, FastAPI

from app.routers.user_route import user_router


router = APIRouter(
    tags=["app-update-service"],
)


def add_routers(app: FastAPI):
    routers = [
        user_router,
    ]
    _add_routers(app, routers)


def _add_routers(app: FastAPI, routers: list[APIRouter]):
    for rout in routers:
        app.include_router(rout)
