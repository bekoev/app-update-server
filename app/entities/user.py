import uuid

from sqlalchemy import UUID, Column, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import EntityBase
from app.models.user import User


class UserEntity(EntityBase[User, uuid.UUID]):
    __tablename__ = "users"
    model = User

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    created_at = Column(DateTime, nullable=False)
