from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped

from app.models.base import ModelBase


class EntityBase[Model: ModelBase, IdType](DeclarativeBase):
    model: type[Model]  # Runtime access to Model's class methods
    update_ignore_fields = {"id", "updated_at"}

    id: Mapped[IdType]  # To be assigned in derived classes

    @classmethod
    def from_model(cls, model: ModelBase) -> EntityBase[Model, IdType]:
        """Create an entity instance from arbitrary Pydantic model"""

        return cls(**model.model_dump())

    def to_model(self) -> Model:
        """Export entity to the corresponding Pydantic model"""

        return self.model.model_validate(self)

    @classmethod
    def values_from_model(cls, model: ModelBase) -> dict:
        """Retrieve entity-related values from arbitrary Pydantic model"""

        data_values = {}
        colls = inspect(cls).mapper.column_attrs
        update_ignore_fields = cls.update_ignore_fields
        for coll in colls:
            value = getattr(model, coll.key, None)
            if value is not None and coll.key not in update_ignore_fields:
                data_values[coll.key] = value
        return data_values

    def to_values(self) -> dict:
        """Export entity values"""

        data_values = {}
        colls = inspect(self).mapper.column_attrs
        for coll in colls:
            col_name = coll.key
            if col_name in self.update_ignore_fields:
                continue
            data_values[col_name] = getattr(self, col_name)
        return data_values
