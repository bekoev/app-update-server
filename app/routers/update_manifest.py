from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from app.core.containers import Container, inject_module
from app.models.update_manifest import UpdateManifest
from app.routers.auth_validation import (
    check_access_by_crm_token,
)
from app.services.update_manifest.service import UpdateManifestService

inject_module(__name__)


update_manifest_router = APIRouter(
    responses={404: {"messages": "Not found"}},
)


@update_manifest_router.get(
    "/update-manifest",
    tags=["update-manifest"],
)
@inject
async def get_update_manifest(
    auth_token: Annotated[str, Depends(check_access_by_crm_token)],
    current_version: Annotated[str, Query(alias="currentVersion")],
    update_manifest_service: UpdateManifestService = Depends(
        Provide[Container.update_manifest_service]
    ),
) -> UpdateManifest:
    return await update_manifest_service.get(current_version)


@update_manifest_router.post(
    "/dev/update-manifest",
    tags=["development"],
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def set_update_manifest(
    manifest: UpdateManifest,
    update_manifest_service: UpdateManifestService = Depends(
        Provide[Container.update_manifest_service]
    ),
) -> None:
    await update_manifest_service.set(manifest)
