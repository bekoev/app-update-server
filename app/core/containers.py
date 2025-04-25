from typing import Set

from dependency_injector import containers, providers

from app.plugins.logger.logging_config import init_logging
from app.plugins.logger.settings import LoggerSettings
from app.plugins.postgres.plugin import PostgresPlugin
from app.plugins.postgres.settings import PostgresSettings
from app.services.update_files.service import UpdateFileService
from app.services.update_files.storage.repository_inmemory import UpdateFileRepository
from app.services.user.user_repository import UserRepository
from app.services.user.user_service import UserService
from app.settings import AppSettings, MainSettings


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(
        MainSettings,
        db=PostgresSettings(),
        logger=LoggerSettings(),
        app=AppSettings(),
    )

    logger = providers.Resource(
        init_logging,
        app_settings=config.provided,
    )
    db = providers.Singleton(
        PostgresPlugin,
        logger=logger,
        config=config.provided.db,
    )
    user_repository = providers.Factory(
        UserRepository,
        db_session=db.provided.session,
        logger=logger,
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository,
        logger=logger,
    )

    update_file_repository = providers.Factory(
        UpdateFileRepository,
    )
    update_file_service = providers.Factory(
        UpdateFileService,
        repository=update_file_repository,
        logger=logger,
    )


modules: Set = set()
container = Container()


def inject_module(module_name: str):
    modules.add(module_name)


def provide_wire(*wires: list):
    container.wire(modules=modules)
