from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse

from app.core.containers import Container, inject_module
from app.routers.auth_validation import check_access_by_api_key
from app.services.update_files.service import UpdateFileService

inject_module(__name__)


update_files_router = APIRouter(
    responses={404: {"messages": "Not found"}},
)


@update_files_router.get(
    "/service/update-files",
    tags=["service-operations"],
)
@inject
async def get_update_file_infos(
    auth_token: Annotated[str, Depends(check_access_by_api_key)],
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> list[UUID]:
    return await update_file_service.get_all_ids()


@update_files_router.get(
    "/update-files/{id}",
    tags=["client-applications"],
)
@inject
async def get_update_file(
    id: UUID,
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> StreamingResponse:
    return StreamingResponse(
        await update_file_service.get_by_id(id),
        media_type="application/octet-stream",
    )


@update_files_router.post(
    "/service/update-files",
    tags=["service-operations"],
)
@inject
async def upload_update_file(
    auth_token: Annotated[str, Depends(check_access_by_api_key)],
    file: UploadFile,
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> UUID:
    return await update_file_service.create(file)
