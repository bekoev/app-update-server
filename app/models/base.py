from typing import TYPE_CHECKING, Union

from pydantic import BaseModel, ConfigDict, model_validator

from app.api.errors import MissDataError

if TYPE_CHECKING:
    from app.entities.base import EntityBase


class ModelBase(BaseModel):
    @classmethod
    def from_model(cls, model: BaseModel):
        return cls(**model.model_dump())

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
    )


class ModelStored[IdType](ModelBase):
    id: IdType

    @model_validator(mode="before")
    @classmethod
    def check_has_values(
        cls, values: Union[dict, "EntityBase"]
    ) -> Union[dict, "EntityBase"]:
        # TODO: Support another model as `values`

        # values can be a dict or a pydantic.utils.GetterDict, or EntityBase
        if isinstance(values, dict):
            field_values = [v for k, v in values.items() if k != "id"]
        else:
            # Try the EntityBase interface
            try:
                field_values = [v for k, v in values.to_values().items() if k != "id"]
            except AttributeError:
                field_values = []

        if not any(field_values):
            raise MissDataError("At least one field should have a value")
        return values
