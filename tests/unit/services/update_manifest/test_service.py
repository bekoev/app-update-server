from logging import Logger
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.errors import ApiForbiddenError, ApiNotFoundError, WrongDataError
from app.models.update_manifest import UpdateManifest
from app.services.update_manifest.service import UpdateManifestService
from app.services.update_manifest.storage.interface import (
    UpdateManifestRepositoryInterface,
)


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=UpdateManifestRepositoryInterface)


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock(spec=Logger)


@pytest.fixture
def update_manifest_service(
    mock_repository: AsyncMock, mock_logger: MagicMock
) -> UpdateManifestService:
    return UpdateManifestService(
        repository=mock_repository,
        logger=mock_logger,
    )


@pytest.fixture
def sample_manifest() -> UpdateManifest:
    return UpdateManifest(
        version="1.0.0",
        url="https://example.com/app-1.0.0.zip",
    )


@pytest.fixture
def newer_manifest() -> UpdateManifest:
    return UpdateManifest(
        version="1.1.0",
        url="https://example.com/app-1.1.0.zip",
    )


class TestUpdateManifestService:
    async def test_set_first_manifest(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        sample_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = None

        # When
        await update_manifest_service.set(sample_manifest)

        # Then
        mock_repository.set.assert_called_once_with(sample_manifest)

    async def test_set_newer_version(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        sample_manifest: UpdateManifest,
        newer_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = sample_manifest

        # When
        await update_manifest_service.set(newer_manifest)

        # Then
        mock_repository.set.assert_called_once_with(newer_manifest)

    async def test_set_older_version(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        sample_manifest: UpdateManifest,
        newer_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = newer_manifest

        # When/Then
        with pytest.raises(ApiForbiddenError):
            await update_manifest_service.set(sample_manifest)

        # Then
        mock_repository.set.assert_not_called()

    async def test_set_invalid_version(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
    ) -> None:
        # Given
        invalid_manifest = UpdateManifest(
            version="not.a.version",
            url="https://example.com/app.zip",
        )

        # When/Then
        with pytest.raises(WrongDataError):
            await update_manifest_service.set(invalid_manifest)

        # Then
        mock_repository.set.assert_not_called()

    async def test_get_manifest(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        sample_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = sample_manifest

        # When
        result = await update_manifest_service.get(None)

        # Then
        assert result == sample_manifest

    async def test_get_manifest_not_found(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
    ) -> None:
        # Given
        mock_repository.get.return_value = None

        # When/Then
        with pytest.raises(ApiNotFoundError):
            await update_manifest_service.get(None)

    async def test_get_manifest_current_version_up_to_date(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        sample_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = sample_manifest

        # When/Then
        with pytest.raises(ApiNotFoundError):
            await update_manifest_service.get("1.0.0")

    async def test_get_manifest_current_version_newer(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        sample_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = sample_manifest

        # When/Then
        with pytest.raises(ApiNotFoundError):
            await update_manifest_service.get("1.1.0")

    async def test_get_manifest_current_version_older(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
        newer_manifest: UpdateManifest,
    ) -> None:
        # Given
        mock_repository.get.return_value = newer_manifest

        # When
        result = await update_manifest_service.get("1.0.0")

        # Then
        assert result == newer_manifest

    async def test_delete(
        self,
        update_manifest_service: UpdateManifestService,
        mock_repository: AsyncMock,
    ) -> None:
        # When
        await update_manifest_service.delete()

        # Then
        mock_repository.delete.assert_called_once()
