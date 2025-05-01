from app.models.update_manifest import UpdateManifest
from app.services.update_manifest.storage.interface import (
    UpdateManifestRepositoryInterface,
)

manifest: UpdateManifest | None = None


class UpdateManifestRepository(UpdateManifestRepositoryInterface):
    async def set(self, new_manifest: UpdateManifest) -> None:
        global manifest
        manifest = new_manifest

    async def get(self) -> UpdateManifest | None:
        if manifest is None:
            return None
        return manifest.model_copy(deep=True)
