from datetime import datetime
from uuid import UUID

from app.models.base import ModelBase, ModelStored


class UserBase(ModelBase):
    created_at: datetime


class User(ModelStored[UUID], UserBase):
    pass


class UserToCreate(UserBase):
    pass
