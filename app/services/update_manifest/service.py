from logging import Logger

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
        return await self.repository.set(manifest)

    async def get(self) -> UpdateManifest:
        return await self.repository.get()
