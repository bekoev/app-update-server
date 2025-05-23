from logging import Logger

from packaging.version import InvalidVersion, Version

from app.api.errors import ApiForbiddenError, ApiNotFoundError, WrongDataError
from app.models.update_manifest import UpdateManifest
from app.services.update_manifest.storage.interface import (
    UpdateManifestRepositoryInterface,
)


class UpdateManifestService:
    def __init__(
        self,
        repository: UpdateManifestRepositoryInterface,
        logger: Logger,
    ) -> None:
        self.repository = repository
        self.logger = logger

    async def set(self, manifest: UpdateManifest) -> None:
        try:
            new_version = Version(manifest.version)
        except InvalidVersion:
            raise WrongDataError(loc="version", message="Invalid version")

        current_manifest = await self.repository.get()

        if not current_manifest or Version(current_manifest.version) < new_version:
            await self.repository.set(manifest)
        else:
            raise ApiForbiddenError(
                "Automatic version downgrade is not supported, remove current manifest explicitly"
            )

    async def get(self, current_version: str | None) -> UpdateManifest:
        current_manifest = await self.repository.get()
        if not current_manifest:
            raise ApiNotFoundError

        manifest_version = Version(current_manifest.version)
        if current_version and manifest_version <= Version(current_version):
            raise ApiNotFoundError

        return current_manifest

    async def delete(self) -> None:
        await self.repository.delete()
