from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.containers import Container, inject_module
from app.services.auth.auth_service import AuthService

inject_module(__name__)

security = HTTPBearer()


@inject
async def check_client_app_access(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> None:
    await auth_service.check_client_app_access(
        credentials.scheme, credentials.credentials
    )
