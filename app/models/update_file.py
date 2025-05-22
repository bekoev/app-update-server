from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UpdateFileInfoToCreate(BaseModel):
    name: str | None = None
    size: int | None = None
    comment: str | None = None


class UpdateFileInfo(UpdateFileInfoToCreate):
    id: UUID
    created_at: datetime
