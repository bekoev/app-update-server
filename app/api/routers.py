from fastapi import APIRouter, FastAPI

from app.routers.user_route import user_router


router = APIRouter(
    # TODO: Change template to a specific name
    tags=["template-backend"],
)


def add_routers(app: FastAPI):
    routers = [
        user_router,
    ]
    _add_routers(app, routers)


def _add_routers(app: FastAPI, routers: list[APIRouter]):
    for rout in routers:
        app.include_router(rout)
