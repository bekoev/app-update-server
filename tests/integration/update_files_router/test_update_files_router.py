import io
from datetime import datetime
from unittest import mock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.settings import AppSettings


async def test_getting_update_file_infos(
    app_client: AsyncClient, app_config: AppSettings, update_files: list[dict]
):
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == 200
    result = response.json()
    fields = ("name", "size", "comment")
    for resulted, expected in zip(
        sorted(result, key=lambda x: x["name"]),
        sorted(update_files, key=lambda x: x["name"]),
    ):
        assert all((resulted.get(f) == expected.get(f) for f in fields))
        assert datetime.fromisoformat(resulted["created_at"]) == expected["created_at"]


async def test_get_update_file(app_client: AsyncClient, app_config: AppSettings):
    """Test downloading a specific update file."""

    # Get available update files to retrieve ID
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == 200
    file_list = response.json()

    if not file_list:
        pytest.skip("No files available for testing")

    # Get the file by ID - use only first file since second might not exist
    file_id = file_list[0]["id"] if file_list else None
    if not file_id:
        pytest.skip("No file ID available for testing")

    # Mock the file retrieval
    with mock.patch(
        "app.services.update_files.storage.file_repository.aiofiles.open"
    ) as mock_open:
        # Setup the mock
        mock_file = mock.AsyncMock()
        mock_file.__aenter__.return_value.read = mock.AsyncMock(
            return_value=b"test content"
        )
        mock_open.return_value = mock_file

        # Test the endpoint
        download_response = await app_client.get(f"/update-files/{file_id}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/octet-stream"


async def test_get_update_file_not_found(app_client: AsyncClient):
    """Test downloading a non-existent file."""

    non_existent_id = "non-existent-id"
    response = await app_client.get(f"/update-files/{non_existent_id}")
    assert response.status_code == 404


async def test_getting_update_file_infos_unauthorized(app_client: AsyncClient):
    """Test getting file info without authorization."""

    response = await app_client.get("/service/update-files")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    headers = {"Authorization": "Bearer wrong-api-key"}
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "filename,comment,expected_status",
    [
        pytest.param("valid.bin", "Valid comment", 200, id="valid_comment"),
        pytest.param("valid.bin", None, 200, id="no_comment"),
    ],
)
@mock.patch("app.services.update_files.storage.file_repository.aiofiles.open")
async def test_upload_update_file_parametrized(
    mock_open,
    app_client: AsyncClient,
    app_config: AppSettings,
    filename: str,
    comment: str | None,
    expected_status: int,
):
    """Test uploading files."""

    # Mock the file operations
    mock_file = mock.AsyncMock()
    mock_file.__aenter__.return_value.write = mock.AsyncMock()
    mock_open.return_value = mock_file

    # Create directory path mock
    with mock.patch(
        "app.services.update_files.storage.file_repository.Path.mkdir",
        return_value=None,
    ):
        with mock.patch(
            "app.services.update_files.storage.file_repository.Path.exists",
            return_value=True,
        ):
            content = b"Test file content"
            file = io.BytesIO(content)
            headers = {"Authorization": f"Bearer {app_config.api_key}"}

            data = {}
            if comment is not None:
                data["comment"] = comment

            response = await app_client.post(
                "/service/update-files",
                headers=headers,
                files={"file": (filename, file)},
                data=data,
            )

            assert response.status_code == expected_status
            if expected_status == 200:
                result = response.json()
                assert result["name"] == filename
                assert result["comment"] == comment
                assert "created_at" in result
                assert "id" in result


@mock.patch("app.services.update_files.storage.file_repository.aiofiles.open")
async def test_upload_file_when_capacity_reached(
    mock_open, app_client: AsyncClient, app_config: AppSettings
):
    """Test that the oldest file is deleted when capacity is reached."""
    # Mock the file operations
    mock_file = mock.AsyncMock()
    mock_file.__aenter__.return_value.write = mock.AsyncMock()
    mock_open.return_value = mock_file

    # Check current file count
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == 200
    current_files = response.json()

    # If already at capacity, we can test the rotation, otherwise skip
    capacity = app_config.file_storage_capacity
    if len(current_files) < capacity:
        # Upload files until we're at capacity
        with mock.patch(
            "app.services.update_files.storage.file_repository.Path.mkdir",
            return_value=None,
        ):
            with mock.patch(
                "app.services.update_files.storage.file_repository.Path.exists",
                return_value=True,
            ):
                for i in range(capacity - len(current_files)):
                    content = b"Test file content"
                    file = io.BytesIO(content)

                    response = await app_client.post(
                        "/service/update-files",
                        headers=headers,
                        files={"file": (f"fill_capacity_{i}.bin", file)},
                    )
                    assert response.status_code == 200

    # Get the current list of files (now at capacity)
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == 200
    files_at_capacity = response.json()
    assert len(files_at_capacity) == capacity

    # Sort files by creation date to find the oldest
    sorted_files = sorted(files_at_capacity, key=lambda x: x["created_at"])
    oldest_file_id = sorted_files[0]["id"]

    # Upload a new file with remove mocked
    with (
        mock.patch(
            "app.services.update_files.storage.file_repository.Path.mkdir",
            return_value=None,
        ),
        mock.patch(
            "app.services.update_files.storage.file_repository.Path.exists",
            return_value=True,
        ),
        mock.patch(
            "app.services.update_files.storage.file_repository.aiofiles.os.remove",
            return_value=None,
        ),
    ):
        content = b"New file that should trigger oldest deletion"
        file = io.BytesIO(content)

        response = await app_client.post(
            "/service/update-files",
            headers=headers,
            files={"file": ("capacity_test.bin", file)},
        )
        assert response.status_code == 200
        new_file_data = response.json()

        # Check if the total count remains at capacity
        response = await app_client.get("/service/update-files", headers=headers)
        assert response.status_code == 200
        updated_files = response.json()
        assert len(updated_files) == capacity

        # Check if the oldest file was deleted
        file_ids = [f["id"] for f in updated_files]
        assert oldest_file_id not in file_ids

        # Verify the new file is in the list
        assert new_file_data["id"] in file_ids


async def test_upload_update_file_unauthorized(app_client: AsyncClient):
    """Test uploading a file without authorization."""

    content = b"Test file content"
    file = io.BytesIO(content)

    # Without API key
    response = await app_client.post(
        "/service/update-files", files={"file": ("test_file.bin", file)}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # With wrong API key
    headers = {"Authorization": "Bearer wrong-api-key"}
    response = await app_client.post(
        "/service/update-files",
        headers=headers,
        files={"file": ("test_file.bin", file)},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_update_file(app_client: AsyncClient, app_config: AppSettings):
    """Test deleting an update file that exists in the database."""

    # Get available update files
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == 200
    files_list = response.json()

    if not files_list:
        pytest.skip("No files available to test deletion")

    original_count = len(files_list)
    # Delete an existing file
    file_id = files_list[0]["id"]
    with (
        mock.patch(
            "app.services.update_files.storage.file_repository.aiofiles.os.remove",
            return_value=None,
        ),
    ):
        delete_response = await app_client.delete(
            f"/update-files/{file_id}", headers=headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        response = await app_client.get("/service/update-files", headers=headers)
        assert response.status_code == 200
        files_list = response.json()
        assert len(files_list) == original_count - 1


async def test_delete_update_file_not_found(
    app_client: AsyncClient, app_config: AppSettings
):
    """Test deleting a non-existent file."""
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    non_existent_id = "non-existent-id"

    response = await app_client.delete(
        f"/update-files/{non_existent_id}", headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_update_file_unauthorized(
    app_client: AsyncClient, app_config: AppSettings
):
    """Test deleting a file without authorization."""
    # Get ID to test with
    non_existent_id = "test-id-123"

    # Try to delete without API key
    response = await app_client.delete(f"/update-files/{non_existent_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete with wrong API key
    wrong_headers = {"Authorization": "Bearer wrong-api-key"}
    response = await app_client.delete(
        f"/update-files/{non_existent_id}", headers=wrong_headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
