from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.models.user import User
from app.services.user.user_service import UserService
from app.core.containers import inject_module


inject_module(__name__)


user_router = APIRouter(
    tags=["user"],
    responses={404: {"messages": "Not found"}},
)


@user_router.get(
    "/users",
    response_model=list[User],
)
@inject
async def get_users(
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    return await user_service.get_all()
