from logging import Logger
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from app.services.crm.client import CRMClient
from app.settings import AppSettings


@pytest.fixture
def mock_config() -> MagicMock:
    config = MagicMock(spec=AppSettings)
    config.crm_url_base = "http://crm-api.example.com"
    return config


@pytest.fixture
def mock_http_client() -> AsyncMock:
    return AsyncMock(spec=AsyncClient)


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock(spec=Logger)


@pytest.fixture
def crm_client(
    mock_config: MagicMock, mock_http_client: AsyncMock, mock_logger: MagicMock
) -> CRMClient:
    return CRMClient(
        config=mock_config,
        http_client=mock_http_client,
        logger=mock_logger,
    )


class TestCRMClient:
    async def test_check_token_valid(
        self, crm_client: CRMClient, mock_http_client: AsyncMock
    ) -> None:
        # Given
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = status.HTTP_200_OK
        mock_http_client.post.return_value = mock_response

        # When
        result = await crm_client.check_token("valid-token")

        # Then
        assert result is True
        mock_http_client.post.assert_called_once_with(
            "http://crm-api.example.com/1/validate-token",
            headers={"Authorization": "Bearer valid-token"},
        )

    async def test_check_token_invalid(
        self, crm_client: CRMClient, mock_http_client: AsyncMock
    ) -> None:
        # Given
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED
        mock_http_client.post.return_value = mock_response

        # When
        result = await crm_client.check_token("invalid-token")

        # Then
        assert result is False
        mock_http_client.post.assert_called_once_with(
            "http://crm-api.example.com/1/validate-token",
            headers={"Authorization": "Bearer invalid-token"},
        )

    async def test_check_token_server_error(
        self, crm_client: CRMClient, mock_http_client: AsyncMock
    ) -> None:
        # Given
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_http_client.post.return_value = mock_response

        # When
        result = await crm_client.check_token("any-token")

        # Then
        assert result is False
        mock_http_client.post.assert_called_once_with(
            "http://crm-api.example.com/1/validate-token",
            headers={"Authorization": "Bearer any-token"},
        )
