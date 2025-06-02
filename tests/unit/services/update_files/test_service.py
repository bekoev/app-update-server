from datetime import datetime
from io import BytesIO
from logging import Logger
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile

from app.api.errors import ApiNotFoundError
from app.models.update_file import UpdateFileInfo, UpdateFileInfoToCreate
from app.services.update_files.service import UpdateFileService
from app.services.update_files.storage.file_info_repository import FileInfoRepository
from app.services.update_files.storage.interfaces import BLOBRepositoryInterface
from app.settings import AppSettings


@pytest.fixture
def mock_blob_repository() -> AsyncMock:
    return AsyncMock(spec=BLOBRepositoryInterface)


@pytest.fixture
def mock_file_info_repository() -> AsyncMock:
    return AsyncMock(spec=FileInfoRepository)


@pytest.fixture
def mock_config() -> MagicMock:
    config = MagicMock(spec=AppSettings)
    config.file_storage_capacity = 5
    return config


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock(spec=Logger)


@pytest.fixture
def update_file_service(
    mock_blob_repository: AsyncMock,
    mock_file_info_repository: AsyncMock,
    mock_config: MagicMock,
    mock_logger: MagicMock,
) -> UpdateFileService:
    return UpdateFileService(
        repository=mock_blob_repository,
        file_info_repository=mock_file_info_repository,
        config=mock_config,
        logger=mock_logger,
    )


@pytest.fixture
def sample_file_info() -> UpdateFileInfo:
    return UpdateFileInfo(
        id="test-id",
        name="test-file.txt",
        size=100,
        comment="Test comment",
        created_at=datetime.fromisoformat("2023-01-01T00:00:00"),
    )


@pytest.fixture
def mock_upload_file() -> MagicMock:
    file = MagicMock(spec=UploadFile)
    file.filename = "test-file.txt"
    file.size = 100
    return file


class TestUpdateFileService:
    async def test_create_success(
        self,
        update_file_service: UpdateFileService,
        mock_blob_repository: AsyncMock,
        mock_file_info_repository: AsyncMock,
        mock_upload_file: MagicMock,
        sample_file_info: UpdateFileInfo,
    ) -> None:
        # Given
        mock_file_info_repository.create.return_value = sample_file_info

        # When
        result = await update_file_service.create(mock_upload_file, "Test comment")

        # Then
        mock_file_info_repository.create.assert_called_once_with(
            UpdateFileInfoToCreate(
                name="test-file.txt", size=100, comment="Test comment"
            )
        )
        mock_blob_repository.create.assert_called_once_with(
            object_id="test-id", file=mock_upload_file
        )
        assert result == sample_file_info

    async def test_create_with_blob_error(
        self,
        update_file_service: UpdateFileService,
        mock_blob_repository: AsyncMock,
        mock_file_info_repository: AsyncMock,
        mock_upload_file: MagicMock,
        sample_file_info: UpdateFileInfo,
    ) -> None:
        # Given
        mock_file_info_repository.create.return_value = sample_file_info
        mock_blob_repository.create.side_effect = Exception("Storage error")

        # When/Then
        with pytest.raises(Exception):
            await update_file_service.create(mock_upload_file, "Test comment")

        # Then the file info should be deleted
        mock_file_info_repository.delete.assert_called_once_with("test-id")

    async def test_get_all_infos(
        self,
        update_file_service: UpdateFileService,
        mock_file_info_repository: AsyncMock,
        sample_file_info: UpdateFileInfo,
    ) -> None:
        # Given
        mock_file_info_repository.get_all.return_value = [sample_file_info]

        # When
        result = await update_file_service.get_all_infos()

        # Then
        assert result == [sample_file_info]
        mock_file_info_repository.get_all.assert_called_once()

    async def test_get_file_success(
        self,
        update_file_service: UpdateFileService,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # Given
        file_content = BytesIO(b"test content")
        mock_blob_repository.get.return_value = file_content

        # When
        result = await update_file_service.get_file("test-id")

        # Then
        assert result == file_content
        mock_blob_repository.get.assert_called_once_with("test-id")

    async def test_get_file_not_found(
        self,
        update_file_service: UpdateFileService,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # Given
        mock_blob_repository.get.side_effect = FileNotFoundError

        # When/Then
        with pytest.raises(ApiNotFoundError):
            await update_file_service.get_file("non-existent-id")

    async def test_delete_file_success(
        self,
        update_file_service: UpdateFileService,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # When
        await update_file_service.delete_file("test-id")

        # Then
        mock_blob_repository.delete.assert_called_once_with("test-id")

    async def test_delete_file_not_found(
        self,
        update_file_service: UpdateFileService,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # Given
        mock_blob_repository.delete.side_effect = FileNotFoundError

        # When - trying to delete non-exstent file
        # Then - no exception is raised
        await update_file_service.delete_file("non-existent-id")

    async def test_ensure_capacity_under_limit(
        self,
        update_file_service: UpdateFileService,
        mock_file_info_repository: AsyncMock,
        sample_file_info: UpdateFileInfo,
    ) -> None:
        # Given
        mock_file_info_repository.get_all.return_value = [sample_file_info]

        # When
        await update_file_service._ensure_capacity()

        # Then - no deletions should occur
        mock_file_info_repository.delete.assert_not_called()

    async def test_ensure_capacity_at_exact_capacity(
        self,
        update_file_service: UpdateFileService,
        mock_file_info_repository: AsyncMock,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # Given - 5 files, capacity is 5 (exactly at capacity)
        files: list[UpdateFileInfo] = [
            UpdateFileInfo(
                id=f"id-{i}",
                name=f"file-{i}.txt",
                size=100,
                comment=None,
                created_at=datetime.fromisoformat(f"2023-01-{i + 1:02d}T00:00:00"),
            )
            for i in range(5)
        ]
        mock_file_info_repository.get_all.return_value = files

        # Reset any previous calls to the mock
        mock_blob_repository.reset_mock()
        mock_file_info_repository.reset_mock()

        # When
        await update_file_service._ensure_capacity()

        # Then - when exactly at capacity, should delete the oldest file to make space for a new one
        # files_to_remove = 5 - 5 + 1 = 1
        mock_blob_repository.delete.assert_called_once_with("id-4")
        mock_file_info_repository.delete.assert_called_once_with("id-4")

    async def test_ensure_capacity_over_limit(
        self,
        update_file_service: UpdateFileService,
        mock_file_info_repository: AsyncMock,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # Given - 6 files, capacity is 5
        files: list[UpdateFileInfo] = [
            UpdateFileInfo(
                id=f"id-{i}",
                name=f"file-{i}.txt",
                size=100,
                comment=None,
                created_at=datetime.fromisoformat(f"2023-01-{i + 1:02d}T00:00:00"),
            )
            for i in range(6)
        ]
        mock_file_info_repository.get_all.return_value = files

        # When
        await update_file_service._ensure_capacity()

        # Then - should delete the two oldest files to make space for one new file
        # files_to_remove = 6 - 5 + 1 = 2
        mock_blob_repository.delete.assert_called_with("id-5")
        mock_file_info_repository.delete.assert_called_with("id-5")

    async def test_ensure_capacity_with_missing_blob(
        self,
        update_file_service: UpdateFileService,
        mock_file_info_repository: AsyncMock,
        mock_blob_repository: AsyncMock,
    ) -> None:
        # Given - 6 files, capacity is 5, but the blob is missing
        files: list[UpdateFileInfo] = [
            UpdateFileInfo(
                id=f"id-{i}",
                name=f"file-{i}.txt",
                size=100,
                comment=None,
                created_at=datetime.fromisoformat(f"2023-01-{i + 1:02d}T00:00:00"),
            )
            for i in range(6)
        ]
        mock_file_info_repository.get_all.return_value = files
        mock_blob_repository.delete.side_effect = FileNotFoundError

        # When
        await update_file_service._ensure_capacity()

        # Then - should still delete the file info record
        mock_file_info_repository.delete.assert_called_with("id-5")
