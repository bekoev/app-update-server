from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.core.containers import Container, inject_module
from app.models.update_manifest import UpdateManifest
from app.routers.auth_validation import check_client_app_access
from app.services.update_manifest.service import UpdateManifestService

inject_module(__name__)


update_manifest_router = APIRouter(
    tags=["update-files"],
    responses={404: {"messages": "Not found"}},
)


@update_manifest_router.get("/update-manifest")
@inject
async def get_update_manifest(
    auth_token: Annotated[str, Depends(check_client_app_access)],
    update_manifest_service: UpdateManifestService = Depends(
        Provide[Container.update_manifest_service]
    ),
) -> UpdateManifest:
    return await update_manifest_service.get()


@update_manifest_router.post("/update-manifest", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def set_update_manifest(
    manifest: UpdateManifest,
    update_manifest_service: UpdateManifestService = Depends(
        Provide[Container.update_manifest_service]
    ),
) -> None:
    await update_manifest_service.set(manifest)
