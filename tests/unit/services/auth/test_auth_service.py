import pytest
from logging import Logger
from unittest.mock import AsyncMock, MagicMock

from app.api.errors import ApiUnauthorizedError
from app.services.auth.auth_service import AuthService
from app.services.crm.client import CRMClient
from app.settings import AppSettings


@pytest.fixture
def mock_config() -> MagicMock:
    config = MagicMock(spec=AppSettings)
    config.api_key = "test-api-key"
    return config


@pytest.fixture
def mock_crm_client() -> AsyncMock:
    return AsyncMock(spec=CRMClient)


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock(spec=Logger)


@pytest.fixture
def auth_service(
    mock_config: MagicMock, mock_crm_client: AsyncMock, mock_logger: MagicMock
) -> AuthService:
    return AuthService(
        config=mock_config,
        crm_client=mock_crm_client,
        logger=mock_logger,
    )


class TestAuthService:
    async def test_check_access_by_api_key_valid(
        self, auth_service: AuthService
    ) -> None:
        # When using the correct scheme and token
        await auth_service.check_access_by_api_key("Bearer", "test-api-key")
        # Then the function should return None (success)

    async def test_check_access_by_api_key_invalid_scheme(
        self, auth_service: AuthService
    ) -> None:
        # When using an incorrect scheme
        with pytest.raises(ApiUnauthorizedError):
            await auth_service.check_access_by_api_key("Basic", "test-api-key")

    async def test_check_access_by_api_key_invalid_token(
        self, auth_service: AuthService
    ) -> None:
        # When using an incorrect token
        with pytest.raises(ApiUnauthorizedError):
            await auth_service.check_access_by_api_key("Bearer", "wrong-api-key")

    async def test_check_access_by_crm_token_valid(
        self, auth_service: AuthService, mock_crm_client: AsyncMock
    ) -> None:
        # Given the CRM client validates the token
        mock_crm_client.check_token.return_value = True
        # When checking access with a valid token
        await auth_service.check_access_by_crm_token("Bearer", "valid-crm-token")
        # Then the CRM client should be called with the token
        mock_crm_client.check_token.assert_called_once_with("valid-crm-token")

    async def test_check_access_by_crm_token_invalid_scheme(
        self, auth_service: AuthService
    ) -> None:
        # When using an incorrect scheme
        with pytest.raises(ApiUnauthorizedError):
            await auth_service.check_access_by_crm_token("Basic", "any-token")
        # Then the CRM client should not be called

    async def test_check_access_by_crm_token_invalid_token(
        self, auth_service: AuthService, mock_crm_client: AsyncMock
    ) -> None:
        # Given the CRM client invalidates the token
        mock_crm_client.check_token.return_value = False
        # When checking access with an invalid token
        with pytest.raises(ApiUnauthorizedError):
            await auth_service.check_access_by_crm_token("Bearer", "invalid-crm-token")
        # Then the CRM client should be called with the token
        mock_crm_client.check_token.assert_called_once_with("invalid-crm-token")
