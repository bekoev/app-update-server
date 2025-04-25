
from collections.abc import Iterable, Sequence
from logging import Logger
from typing import Any

from app.models.base import ModelBase, ModelStored
from app.services.base_repository import BaseRepository


class BaseService[Model: ModelBase, IdType]:
    """BaseService service for CRUD operations."""

    BoundModel: type[Model]

    def __init__(
        self,
        repository: BaseRepository[Model, IdType],
        config: Any | None = None,
        logger: Logger | None = None,
    ) -> None:
        self.config = config
        self.repository = repository
        self.logger = logger

    async def get_by_id(self, entity_id: IdType) -> Model:
        """Get one object by its ID."""
        return await self.repository.get_by_id(entity_id)

    async def get_all(self) -> Sequence[Model]:
        """Get all objects."""
        return await self.repository.get_all()

    async def create(self, object_to_create: Model) -> Model:
        """Create an object."""
        return await self.repository.create(object_to_create)

    async def bulk_create(self, items_to_create: Iterable[Model]) -> None:
        """Bulk create objects."""
        await self.repository.bulk_create(items_to_create)

    async def update(self, object_to_update: ModelStored) -> None:
        """Update the object."""
        await self.repository.update(object_to_update)
