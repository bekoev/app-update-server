from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import EntityBase


class UpdateManifestEntity(EntityBase):
    __tablename__ = "update_manifests"

    version: Mapped[str] = mapped_column(String, primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
