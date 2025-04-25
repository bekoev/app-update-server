import uuid

from app.entities.base import EntityBase
from app.entities.user import UserEntity
from app.models.user import User
from app.services.base_repository import BaseRepository


class UserRepository(BaseRepository[User, uuid.UUID]):
    BoundModel: type[User] = User
    BoundEntity: type[EntityBase] = UserEntity
