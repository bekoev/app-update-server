from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.containers import Container, inject_module
from app.models.update_file import UpdateFileInfo
from app.routers.auth_validation import check_access_by_api_key
from app.services.update_files.service import UpdateFileService

inject_module(__name__)


update_files_router = APIRouter(
    responses={404: {"messages": "Not found"}},
)


@update_files_router.get(
    "/service/update-files",
    tags=["service-operations"],
    dependencies=[Depends(check_access_by_api_key)],
)
@inject
async def get_update_file_infos(
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> list[UpdateFileInfo]:
    return await update_file_service.get_all_infos()


@update_files_router.get(
    "/update-files/{id}",
    tags=["client-applications"],
)
@inject
async def get_update_file(
    id: str,
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> StreamingResponse:
    return StreamingResponse(
        await update_file_service.get_file(id),
        media_type="application/octet-stream",
    )


@update_files_router.post(
    "/service/update-files",
    tags=["service-operations"],
    dependencies=[Depends(check_access_by_api_key)],
)
@inject
async def upload_update_file(
    file: UploadFile,
    comment: Annotated[str | None, Form()] = None,
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> UpdateFileInfo:
    return await update_file_service.create(file, comment=comment)


@update_files_router.delete(
    "/service/update-files/{id}",
    tags=["service-operations"],
    dependencies=[Depends(check_access_by_api_key)],
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_update_file(
    id: str,
    update_file_service: UpdateFileService = Depends(
        Provide[Container.update_file_service]
    ),
) -> None:
    await update_file_service.delete_file(id)
