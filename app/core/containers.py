from typing import Set

from dependency_injector import containers, providers

from app.plugins.http.http_client import http_client_session
from app.plugins.logger.logging_config import init_logging
from app.plugins.logger.settings import LoggerSettings
from app.plugins.postgres.plugin import PostgresPlugin
from app.plugins.postgres.settings import PostgresSettings
from app.services.auth.auth_service import AuthService
from app.services.crm.client import CRMClient
from app.services.update_files.service import UpdateFileService
from app.services.update_files.storage.file_info_repository import FileInfoRepository
from app.services.update_files.storage.file_repository import BLOBRepository
from app.services.update_manifest.service import UpdateManifestService
from app.services.update_manifest.storage.repository import UpdateManifestRepositoryDB
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

    crm_http_client = providers.Resource(
        http_client_session,
    )
    crm_client = providers.Factory(
        CRMClient,
        config=config.provided.app,
        http_client=crm_http_client,
        logger=logger,
    )
    auth_service = providers.Factory(
        AuthService,
        config=config.provided.app,
        crm_client=crm_client,
        logger=logger,
    )

    update_file_repository = providers.Factory(
        BLOBRepository,
        config=config.provided.app,
        logger=logger,
    )
    file_info_repository = providers.Factory(
        FileInfoRepository,
        db_session=db.provided.session,
        logger=logger,
    )
    update_file_service = providers.Factory(
        UpdateFileService,
        repository=update_file_repository,
        file_info_repository=file_info_repository,
        config=config.provided.app,
        logger=logger,
    )

    update_manifest_repository = providers.Factory(
        UpdateManifestRepositoryDB,
        db_session=db.provided.session,
        logger=logger,
    )
    update_manifest_service = providers.Factory(
        UpdateManifestService,
        repository=update_manifest_repository,
        logger=logger,
    )


modules: Set = set()
container = Container()


def inject_module(module_name: str):
    modules.add(module_name)


def provide_wire(*wires: list):
    container.wire(modules=modules)
