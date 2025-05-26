from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict


def str_from_uuid(value: Any) -> Any:
    if isinstance(value, UUID):
        return value.hex
    else:
        return value


class UpdateFileInfoToCreate(BaseModel):
    name: str | None = None
    size: int | None = None
    comment: str | None = None


class UpdateFileInfo(UpdateFileInfoToCreate):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[str, BeforeValidator(str_from_uuid)]
    created_at: datetime
