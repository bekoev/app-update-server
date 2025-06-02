import pytest
from fastapi import status
from httpx import AsyncClient

from app.settings import AppSettings


@pytest.mark.parametrize(
    "current_version,expected_status",
    [
        pytest.param("1.0.0", status.HTTP_200_OK, id="lower_version"),
        pytest.param("1.2.0", status.HTTP_404_NOT_FOUND, id="same_version"),
        pytest.param("2.0.0", status.HTTP_404_NOT_FOUND, id="newer_version"),
        pytest.param(
            "invalid", status.HTTP_422_UNPROCESSABLE_ENTITY, id="invalid_version"
        ),
        pytest.param(None, status.HTTP_422_UNPROCESSABLE_ENTITY, id="no_version"),
    ],
)
async def test_get_update_manifest(
    app_client: AsyncClient,
    app_config: AppSettings,
    update_manifest: dict,
    current_version: str,
    expected_status: int,
):
    """Test getting an update manifest."""

    # Test with API key authentication
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    response = await app_client.get(
        f"/update-manifest?currentVersion={current_version}", headers=headers
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        result = response.json()
        assert result["version"] == update_manifest["version"]
        assert result["url"] == update_manifest["url"]


async def test_get_update_manifest_unauthorized(app_client: AsyncClient):
    """Test getting an update manifest without authorization."""

    current_version = "1.0.0"

    # Without API key
    response = await app_client.get(
        f"/update-manifest?currentVersion={current_version}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_update_manifest_with_wrong_api_key(app_client: AsyncClient):
    """Test getting an update manifest with wrong API key."""

    current_version = "1.0.0"

    headers = {"Authorization": "Bearer wrong-api-key"}
    response = await app_client.get(
        f"/update-manifest?currentVersion={current_version}", headers=headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_update_manifest_with_crm_token(
    app_client: AsyncClient, update_manifest: dict
):
    """Test getting an update manifest with CRM token."""

    current_version = "1.0.0"

    headers = {"Authorization": "Bearer crm-token-123"}
    response = await app_client.get(
        f"/update-manifest?currentVersion={current_version}", headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["version"] == update_manifest["version"]
    assert result["url"] == update_manifest["url"]


@pytest.mark.parametrize(
    "manifest_data,expected_status",
    [
        pytest.param(
            {"version": "2.0.0", "url": "https://example.com/downloads/app-2.0.0.zip"},
            status.HTTP_204_NO_CONTENT,
            id="higher_version",
        ),
        pytest.param(
            {"version": "1.0.0", "url": "https://example.com/downloads/app-1.0.0.zip"},
            status.HTTP_403_FORBIDDEN,
            id="lower_version",
        ),
        pytest.param(
            {
                "version": "invalid",
                "url": "https://example.com/downloads/app-invalid.zip",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            id="invalid_version",
        ),
    ],
)
async def test_set_update_manifest(
    app_client: AsyncClient,
    app_config: AppSettings,
    manifest_data: dict,
    expected_status: int,
):
    """Test setting an update manifest."""

    headers = {"Authorization": f"Bearer {app_config.api_key}"}

    response = await app_client.post(
        "/service/update-manifest",
        headers=headers,
        json=manifest_data,
    )

    assert response.status_code == expected_status

    if expected_status == status.HTTP_204_NO_CONTENT:
        # Verify the manifest was set correctly
        get_response = await app_client.get(
            "/update-manifest?currentVersion=1.0.0", headers=headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        result = get_response.json()
        assert result["version"] == manifest_data["version"]
        assert result["url"] == manifest_data["url"]


async def test_set_update_manifest_unauthorized(app_client: AsyncClient):
    """Test setting an update manifest without authorization."""

    manifest_data = {
        "version": "2.0.0",
        "url": "https://example.com/downloads/app-2.0.0.zip",
    }

    # Without API key
    response = await app_client.post(
        "/service/update-manifest",
        json=manifest_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # With wrong API key
    headers = {"Authorization": "Bearer wrong-api-key"}
    response = await app_client.post(
        "/service/update-manifest",
        headers=headers,
        json=manifest_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_update_manifest(app_client: AsyncClient, app_config: AppSettings):
    """Test deleting an update manifest."""
    headers = {"Authorization": f"Bearer {app_config.api_key}"}

    # Verify the manifest is there
    get_response = await app_client.get(
        "/update-manifest?currentVersion=1.0.0", headers=headers
    )
    assert get_response.status_code == status.HTTP_200_OK

    # Delete the manifest
    delete_response = await app_client.delete(
        "/service/update-manifest", headers=headers
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the manifest was deleted
    get_response = await app_client.get(
        "/update-manifest?currentVersion=1.0.0", headers=headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_update_manifest_unauthorized(app_client: AsyncClient):
    """Test deleting an update manifest without authorization."""

    # Without API key
    response = await app_client.delete("/service/update-manifest")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # With wrong API key - mock the response
    headers = {"Authorization": "Bearer wrong-api-key"}
    response = await app_client.delete(
        "/service/update-manifest",
        headers=headers,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
