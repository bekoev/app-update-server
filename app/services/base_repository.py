from collections.abc import Iterable, Sequence
from contextlib import AbstractAsyncContextManager
from logging import Logger
from typing import TYPE_CHECKING, Any, Callable, cast

from pydantic import TypeAdapter
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.errors import EntityNotFound
from app.entities.base import EntityBase
from app.models.base import ModelBase, ModelStored


class BaseRepository[Model: ModelBase, IdType]:
    BoundModel = ModelBase  # Runtime access to Model's class methods
    BoundEntity = EntityBase  # Runtime access to Model's class methods

    def __init__(
        self,
        db_session: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.db_session = db_session
        self.logger = logger

    async def create(self, object: ModelBase) -> Model:
        """Add a new object to the repo.

        Args:
            object: The object to add. Must be compatible with
                the bound entity of the repo, see BoundEntity.

        Returns:
            Model: The resulted object, possibly with some fields filled by
                the repository, e.g. IDs or generated timestamps.
        """
        async with self.db_session() as session:
            db_object: EntityBase = self.BoundEntity.from_model(object)
            session.add(db_object)
            await session.commit()
            await session.refresh(db_object)
            return cast(Model, db_object.to_model())

    async def bulk_create(self, objects: Iterable[ModelBase]) -> None:
        """Add several objects to the repo.

        Args:
            objects: The objects to add. Must be compatible with
                the bound entity of the repo, see BoundEntity.
        """
        async with self.db_session() as session:
            db_objects: tuple[EntityBase, ...] = tuple(
                map(self.BoundEntity.from_model, objects)
            )
            session.add_all(db_objects)
            await session.commit()

    async def update(self, object: ModelStored) -> None:
        """Update an object in the repo.

        Args:
            object: The object to update. Must be convertible to the bound
                entity of the repo, see BoundEntity.
        """
        async with self.db_session() as session:
            await self._update_entity_in_transaction(session=session, object=object)
            await session.commit()

    async def bulk_update(self, objects: list[ModelStored]) -> None:
        """Update several objects in the repo.

        Args:
            objects: The objects to update. Each item must be
                convertible to the bound entity of the repo, see BoundEntity.
        """
        async with self.db_session() as session:
            for object in objects:
                await self._update_entity_in_transaction(session=session, object=object)
            await session.commit()

    async def get_by_id(self, object_id: IdType) -> Model:
        """Get the object from the repo by the object ID.

        Args:
            object_id (Any): The object ID of the type specified by the Model.

        Raises:
            EntityNotFound: The object not found by the ID.

        Returns:
            Model: The object found.
        """
        async with self.db_session() as session:
            query = select(self.BoundEntity).filter_by(id=object_id)
            db_object = await session.scalar(query)
            if not db_object:
                self.logger.exception(
                    msg=f"The requested object of Entity {self.BoundModel.__name__} "
                    "not found"
                )
                raise EntityNotFound(self.BoundModel.__name__)
            return cast(Model, self.BoundModel.model_validate(db_object))

    async def get_all(self) -> Sequence[Model]:
        """Get all objects from the repo.

        Returns:
            list[Model]: The list of objects.
        """
        async with self.db_session() as session:
            entities = (await session.execute(select(self.BoundEntity))).scalars().all()
            if TYPE_CHECKING:
                ta: TypeAdapter[Sequence[Model]] = TypeAdapter(list[ModelBase])
            else:
                ta = TypeAdapter(list[self.BoundModel])
            return ta.validate_python(entities)

    async def delete_by_id(self, object_id: Any) -> None:
        """Delete the object from the repo by the object ID.

        Args:
            object_id (Any): The object ID of the type specified by the Model.
        """
        async with self.db_session() as session:
            await session.execute(delete(self.BoundEntity).filter_by(id=object_id))
            await session.commit()

    @classmethod
    async def _update_entity_in_transaction(
        cls, session: AsyncSession, object: ModelStored
    ) -> None:
        """Update the object without a commit."""
        await session.execute(
            update(cls.BoundEntity)
            .filter_by(id=object.id)
            .values(cls.BoundEntity.values_from_model(object))
        )
