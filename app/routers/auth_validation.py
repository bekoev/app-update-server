from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.errors import ApiUnauthorizedError
from app.core.containers import Container, inject_module
from app.services.auth.auth_service import AuthService

inject_module(__name__)

security = HTTPBearer()


@inject
async def check_access_by_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> None:
    await auth_service.check_access_by_api_key(
        credentials.scheme, credentials.credentials
    )


@inject
async def check_access_by_crm_token_or_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> None:
    try:
        await auth_service.check_access_by_api_key(
            credentials.scheme, credentials.credentials
        )
    except ApiUnauthorizedError:
        await auth_service.check_access_by_crm_token(
            credentials.scheme, credentials.credentials
        )
