from abc import ABC, abstractmethod

from app.models.update_manifest import UpdateManifest


class UpdateManifestRepositoryInterface(ABC):
    @abstractmethod
    async def set(self, manifest: UpdateManifest) -> None: ...

    @abstractmethod
    async def get(self) -> UpdateManifest | None: ...
