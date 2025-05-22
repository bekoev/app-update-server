from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UpdateFileInfoToCreate(BaseModel):
    comment: str | None = None


class UpdateFileInfo(UpdateFileInfoToCreate):
    id: UUID
    created_at: datetime
