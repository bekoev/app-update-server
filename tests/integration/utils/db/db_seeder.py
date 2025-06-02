from dataclasses import dataclass
from typing import Any

from app.plugins.postgres.plugin import PostgresPlugin


@dataclass
class EntityInfo:
    type: Any
    data: list[dict]


class DbTestDataHandler:
    """A class that would initialize a DB with test data, and clean it up afterwards."""

    def __init__(
        self,
        client_db: PostgresPlugin,
        entity_type: Any | None = None,
        entity_data: list[dict] | None = None,
    ):
        """Initialize the data handler.

        Also note the add_entity_info() possibility to handle a list of entities.
        """
        self._engine = client_db.engine
        self._db_session = client_db.session
        self._entity_info: list[EntityInfo] = []
        if entity_type is not None and entity_data is not None:
            self._entity_info.append(EntityInfo(entity_type, entity_data))

    def add_entity_info(self, entity_type, entity_data: list[dict]):
        """Add an entity to handle."""
        self._entity_info.append(EntityInfo(entity_type, entity_data))

    async def clear_database(self):
        """Clear the DB from any data for the entities being handled."""
        async with self._engine.begin() as connection:
            for entity_info in self._entity_info:
                await connection.run_sync(
                    entity_info.type.__table__.drop, checkfirst=True
                )

    async def seed_database(self):
        """Populate the DB with the initial data."""
        async with self._engine.begin() as connection:
            for entity_info in self._entity_info:
                await connection.run_sync(entity_info.type.__table__.create)

        async with self._db_session() as session:
            for entity_info in self._entity_info:
                for model in entity_info.data:
                    entity = entity_info.type(**model)
                    session.add(entity)
            await session.commit()
