"""Unit tests for IDaaSPamClient class

This module contains comprehensive unit tests for the IDaaSPamClient class,
covering initialization, endpoint processing, API key retrieval, and builder pattern.
"""

from unittest.mock import Mock, patch

import pytest
from Tea.exceptions import TeaException

from cloud_idaas.core import (
    ClientException,
    ConfigException,
    HttpConstants,
    IDaaSUnexpectedException,
)
from cloud_idaas.pam_client.domain.pam_client_constants import PamClientConstants
from cloud_idaas.pam_client.idaas_pam_client import IDaaSPamClient


class TestIDaaSPamClientInitialization:
    """Test suite for IDaaSPamClient initialization"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_init_with_all_parameters(self, mock_client, mock_factory):
        """Test initialization with all parameters provided"""
        # Arrange
        endpoint = "test.endpoint.com"
        instance_id = "test_instance_id"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_token"

        # Act
        client = IDaaSPamClient(
            developer_api_endpoint=endpoint,
            idaas_instance_id=instance_id,
            credential_provider=mock_provider,
        )

        # Assert
        assert client._developer_api_endpoint == endpoint
        assert client._idaas_instance_id == instance_id
        assert client._credential_provider == mock_provider
        mock_client.assert_called_once()

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_init_without_endpoint_raises_exception(self, mock_client, mock_factory):
        """Test initialization without endpoint raises ConfigException"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = None

        # Act & Assert
        with pytest.raises(ConfigException) as exc_info:
            IDaaSPamClient(
                developer_api_endpoint=None,
                idaas_instance_id="test_instance",
                credential_provider=Mock(),
            )
        assert "DeveloperApiEndpoint can not be empty" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_init_without_instance_id_raises_exception(self, mock_client, mock_factory):
        """Test initialization without instance ID raises ConfigException"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = None

        # Act & Assert
        with pytest.raises(ConfigException) as exc_info:
            IDaaSPamClient(
                developer_api_endpoint="test.endpoint.com",
                idaas_instance_id=None,
                credential_provider=Mock(),
            )
        assert "IDaasInstanceId can not be empty" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_init_without_credential_provider_raises_exception(self, mock_client, mock_factory):
        """Test initialization without credential provider raises ConfigException"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider_by_scope.return_value = None

        # Act & Assert
        with pytest.raises(ConfigException) as exc_info:
            IDaaSPamClient(
                developer_api_endpoint="test.endpoint.com",
                idaas_instance_id="test_instance",
                credential_provider=None,
            )
        assert "CredentialProvider can not be empty" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_init_uses_factory_defaults_when_parameters_none(self, mock_client, mock_factory):
        """Test initialization uses factory defaults when parameters are None"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "default.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "default_instance"
        mock_provider = Mock()
        mock_factory.get_idaas_credential_provider_by_scope.return_value = mock_provider

        # Act
        client = IDaaSPamClient()

        # Assert
        assert client._developer_api_endpoint == "default.endpoint.com"
        assert client._idaas_instance_id == "default_instance"
        assert client._credential_provider == mock_provider
        mock_factory.get_idaas_credential_provider_by_scope.assert_called_once_with(PamClientConstants.SCOPE)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_init_client_creation_failure_raises_config_exception(self, mock_client, mock_factory):
        """Test initialization raises ConfigException when client creation fails"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()
        mock_client.side_effect = Exception("Client creation error")

        # Act & Assert
        with pytest.raises(ConfigException) as exc_info:
            IDaaSPamClient(
                developer_api_endpoint="test.endpoint.com",
                idaas_instance_id="test_instance",
                credential_provider=Mock(),
            )
        assert "Client creation error" in str(exc_info.value)


class TestGetDeveloperApiEndpoint:
    """Test suite for _get_developer_api_endpoint method"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_endpoint_removes_https_prefix(self, mock_client, mock_factory):
        """Test endpoint processing removes https:// prefix"""
        # Arrange
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        client = IDaaSPamClient(
            developer_api_endpoint="https://test.endpoint.com",
            idaas_instance_id="test_instance",
            credential_provider=Mock(),
        )

        # Assert
        assert client._developer_api_endpoint == "test.endpoint.com"

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_endpoint_removes_http_prefix(self, mock_client, mock_factory):
        """Test endpoint processing removes http:// prefix"""
        # Arrange
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        client = IDaaSPamClient(
            developer_api_endpoint="http://test.endpoint.com",
            idaas_instance_id="test_instance",
            credential_provider=Mock(),
        )

        # Assert
        assert client._developer_api_endpoint == "test.endpoint.com"

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_endpoint_preserves_endpoint_without_prefix(self, mock_client, mock_factory):
        """Test endpoint processing preserves endpoint without protocol prefix"""
        # Arrange
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        client = IDaaSPamClient(
            developer_api_endpoint="test.endpoint.com",
            idaas_instance_id="test_instance",
            credential_provider=Mock(),
        )

        # Assert
        assert client._developer_api_endpoint == "test.endpoint.com"

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_endpoint_returns_none_for_none_input(self, mock_client, mock_factory):
        """Test endpoint processing returns None for None input"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = None

        # Act & Assert
        with pytest.raises(ConfigException):
            IDaaSPamClient(
                developer_api_endpoint=None,
                idaas_instance_id="test_instance",
                credential_provider=Mock(),
            )

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_endpoint_uses_factory_when_parameter_none(self, mock_client, mock_factory):
        """Test endpoint processing uses factory when parameter is None"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "https://factory.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        client = IDaaSPamClient(
            developer_api_endpoint=None,
            idaas_instance_id="test_instance",
            credential_provider=Mock(),
        )

        # Assert
        assert client._developer_api_endpoint == "factory.endpoint.com"


class TestGetApiKey:
    """Test suite for get_api_key method"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_success(self, mock_client_class, mock_factory):
        """Test successful API key retrieval"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_api_key_content = Mock()
        mock_api_key_content.api_key = "test_api_key_12345"
        mock_credential_content = Mock()
        mock_credential_content.api_key_content = mock_api_key_content
        mock_response_body = Mock()
        mock_response_body.credential_content = mock_credential_content
        mock_response.body = mock_response_body

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act
        api_key = client.get_api_key("test_credential_identifier")

        # Assert
        assert api_key == "test_api_key_12345"
        mock_client_instance.obtain_credential_with_options.assert_called_once()

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_returns_none_when_api_key_content_none(self, mock_client_class, mock_factory):
        """Test get_api_key returns None when api_key_content is None"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock response with None api_key_content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_credential_content = Mock()
        mock_credential_content.api_key_content = None
        mock_response_body = Mock()
        mock_response_body.credential_content = mock_credential_content
        mock_response.body = mock_response_body

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act
        api_key = client.get_api_key("test_credential_identifier")

        # Assert
        assert api_key is None

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_returns_none_when_credential_content_none(self, mock_client_class, mock_factory):
        """Test get_api_key returns None when credential_content is None"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock response with None credential_content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response_body = Mock()
        mock_response_body.credential_content = None
        mock_response.body = mock_response_body

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act
        api_key = client.get_api_key("test_credential_identifier")

        # Assert
        assert api_key is None

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_raises_unexpected_exception_for_non_200_status(self, mock_client_class, mock_factory):
        """Test get_api_key raises IDaaSUnexpectedException for non-200 status code"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock response with 404 status
        mock_response = Mock()
        mock_response.status_code = 404

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act & Assert
        with pytest.raises(IDaaSUnexpectedException) as exc_info:
            client.get_api_key("test_credential_identifier")
        assert "status code: 404" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_raises_client_exception_for_4xx_error(self, mock_client_class, mock_factory):
        """Test get_api_key raises ClientException for 4xx errors"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock TeaException with 4xx error
        tea_exception = TeaException(
            {
                "code": 400,
                "data": {
                    "error": "invalid_request",
                    "error_description": "Invalid credential identifier",
                    "request_id": "req_123",
                },
            }
        )

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.side_effect = tea_exception
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.get_api_key("test_credential_identifier")
        assert "invalid_request" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_reraises_tea_exception_for_5xx_error(self, mock_client_class, mock_factory):
        """Test get_api_key re-raises TeaException for 5xx errors

        Note: The code at line 104 has `status_code >= 400 or status_code < 500`
        which is always True for any status_code, but when code >= 500,
        the elif at line 110 catches it and re-raises the original exception.
        """
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock TeaException with 5xx error
        tea_exception = TeaException({"code": 500, "data": {}})

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.side_effect = tea_exception
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act & Assert - The exception is re-raised
        with pytest.raises(TeaException) as exc_info:
            client.get_api_key("test_credential_identifier")
        assert exc_info.value.code == 500

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_raises_unexpected_exception_for_general_error(self, mock_client_class, mock_factory):
        """Test get_api_key raises IDaaSUnexpectedException for general errors"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider.return_value = mock_provider

        # Mock general exception
        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act & Assert
        with pytest.raises(IDaaSUnexpectedException) as exc_info:
            client.get_api_key("test_credential_identifier")
        assert "Network error" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_get_api_key_sets_correct_authorization_header(self, mock_client_class, mock_factory):
        """Test get_api_key sets correct authorization header"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()
        mock_provider.get_bearer_token.return_value = "test_bearer_token"
        mock_factory.get_idaas_credential_provider_by_scope.return_value = mock_provider

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_api_key_content = Mock()
        mock_api_key_content.api_key = "test_api_key"
        mock_credential_content = Mock()
        mock_credential_content.api_key_content = mock_api_key_content
        mock_response_body = Mock()
        mock_response_body.credential_content = mock_credential_content
        mock_response.body = mock_response_body

        mock_client_instance = Mock()
        mock_client_instance.obtain_credential_with_options.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = IDaaSPamClient()

        # Act
        client.get_api_key("test_credential_identifier")

        # Assert
        call_args = mock_client_instance.obtain_credential_with_options.call_args
        headers = call_args[0][2]  # Third argument is headers
        expected_auth = f"{HttpConstants.BEARER}{HttpConstants.SPACE}test_bearer_token"
        assert headers.authorization == expected_auth


class TestIDaaSPamClientBuilder:
    """Test suite for IDaaSPamClientBuilder"""

    def test_builder_creation(self):
        """Test builder can be created"""
        builder = IDaaSPamClient.builder()
        assert isinstance(builder, IDaaSPamClient.IDaaSPamClientBuilder)

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_builder_with_developer_api_endpoint(self, mock_client, mock_factory):
        """Test builder with developer API endpoint"""
        # Arrange
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        builder = IDaaSPamClient.builder()
        builder.developer_api_endpoint("test.endpoint.com")
        client = builder.build()

        # Assert
        assert client._developer_api_endpoint == "test.endpoint.com"

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_builder_with_idaas_instance_id(self, mock_client, mock_factory):
        """Test builder with IDaaS instance ID"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        builder = IDaaSPamClient.builder()
        builder.idaas_instance_id("custom_instance_id")
        client = builder.build()

        # Assert
        assert client._idaas_instance_id == "custom_instance_id"

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_builder_with_credential_provider(self, mock_client, mock_factory):
        """Test builder with credential provider"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_provider = Mock()

        # Act
        builder = IDaaSPamClient.builder()
        builder.credential_provider(mock_provider)
        client = builder.build()

        # Assert
        assert client._credential_provider == mock_provider

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_builder_method_chaining(self, mock_client, mock_factory):
        """Test builder supports method chaining"""
        # Arrange
        mock_provider = Mock()

        # Act
        builder = (
            IDaaSPamClient.builder()
            .developer_api_endpoint("test.endpoint.com")
            .idaas_instance_id("test_instance")
            .credential_provider(mock_provider)
        )
        client = builder.build()

        # Assert
        assert client._developer_api_endpoint == "test.endpoint.com"
        assert client._idaas_instance_id == "test_instance"
        assert client._credential_provider == mock_provider

    @patch("cloud_idaas.pam_client.idaas_pam_client.IDaaSCredentialProviderFactory")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_builder_build_creates_client_instance(self, mock_client, mock_factory):
        """Test builder build method creates IDaaSPamClient instance"""
        # Arrange
        mock_factory.get_developer_api_endpoint.return_value = "test.endpoint.com"
        mock_factory.get_idaas_instance_id.return_value = "test_instance"
        mock_factory.get_idaas_credential_provider.return_value = Mock()

        # Act
        builder = IDaaSPamClient.builder()
        client = builder.build()

        # Assert
        assert isinstance(client, IDaaSPamClient)


def _make_oauth_client(mock_client_class):
    """Build an IDaaSPamClient with a mocked Tea Client and a fixed bearer token."""
    mock_provider = Mock()
    mock_provider.get_bearer_token.return_value = "test_bearer_token"
    mock_client_instance = mock_client_class.return_value
    client = IDaaSPamClient("test.endpoint.com", "test_instance", mock_provider)
    return client, mock_client_instance


def _mock_fetch_response(has_token=False, has_session=False):
    response = Mock()
    response.status_code = 200
    body = Mock()
    body.oauth_access_token_content = None
    body.oauth_authorization_session = None
    if has_token:
        token_content = Mock()
        token_content.access_token_value = "at_value"
        token_content.token_type = "Bearer"
        token_content.scope = "scope1"
        body.oauth_access_token_content = token_content
    if has_session:
        session = Mock()
        session.session_id = "sid"
        session.session_uri = "urn:ietf:params:oauth:request_uri:sid"
        session.authorization_url = "https://auth.example.com/authorize"
        session.session_status = "pending"
        body.oauth_authorization_session = session
    response.body = body
    return response


def _mock_session_response(status, **kwargs):
    response = Mock()
    response.status_code = 200
    body = Mock()
    body.session_status = status
    body.authorization_url = kwargs.get("authorization_url")
    body.authentication_token_id = kwargs.get("authentication_token_id")
    body.error_code = kwargs.get("error_code")
    body.error_description = kwargs.get("error_description")
    response.body = body
    return response


class TestFetchOAuthAuthenticationTokenV2:
    """Test suite for fetch_oauth_authentication_token_v2"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_m2m_returns_access_token_content(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_token=True
        )

        # Act
        result = client.fetch_oauth_authentication_token_v2(
            "provider-1", PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M
        )

        # Assert
        assert result.has_oauth_access_token_content() is True
        assert result.has_oauth_authorization_session() is False
        assert result.oauth_access_token_content.access_token_value == "at_value"
        assert result.oauth_access_token_content.token_type == "Bearer"
        assert result.oauth_access_token_content.scope == "scope1"

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_user_federation_unauthorized_returns_session(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )

        # Act
        result = client.fetch_oauth_authentication_token_v2(
            "provider-1", PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION
        )

        # Assert
        assert result.has_oauth_authorization_session() is True
        assert result.has_oauth_access_token_content() is False
        assert result.oauth_authorization_session.session_status == "pending"
        assert result.oauth_authorization_session.authorization_url == "https://auth.example.com/authorize"

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_user_federation_authorized_returns_token(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_token=True
        )

        # Act
        result = client.fetch_oauth_authentication_token_v2(
            "provider-1", PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION
        )

        # Assert
        assert result.has_oauth_access_token_content() is True

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_m2m_but_session_returned_raises_client_exception(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.fetch_oauth_authentication_token_v2("provider-1", PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M)
        assert "authorization_flow_mismatch" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_invalid_flow_raises_client_exception(self, mock_client_class):
        # Arrange
        client, _ = _make_oauth_client(mock_client_class)

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.fetch_oauth_authentication_token_v2("provider-1", "bad_flow")
        assert "invalid_authorization_flow" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_force_authentication_and_custom_parameters_written_to_request(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_token=True
        )

        # Act
        client.fetch_oauth_authentication_token_v2(
            "provider-1",
            PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
            scope="s1 s2",
            force_authentication=True,
            custom_parameters={"access_type": "offline"},
        )

        # Assert
        call_args = mock_client_instance.fetch_oauth_authentication_token_with_options.call_args
        request = call_args[0][1]
        headers = call_args[0][2]
        assert request.force_authentication is True
        assert request.custom_parameters == {"access_type": "offline"}
        assert request.scope == "s1 s2"
        expected_auth = f"{HttpConstants.BEARER}{HttpConstants.SPACE}test_bearer_token"
        assert headers.authorization == expected_auth

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_raises_client_exception_for_4xx(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.side_effect = TeaException(
            {"code": 400, "data": {"error": "credential_provider_not_enabled", "request_id": "r1"}}
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.fetch_oauth_authentication_token_v2(
                "provider-1", PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION
            )
        assert "credential_provider_not_enabled" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_raises_unexpected_exception_for_general_error(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.side_effect = Exception("Network error")

        # Act & Assert
        with pytest.raises(IDaaSUnexpectedException) as exc_info:
            client.fetch_oauth_authentication_token_v2(
                "provider-1", PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION
            )
        assert "Network error" in str(exc_info.value)


class TestGetOAuthAuthorizationSession:
    """Test suite for get_oauth_authorization_session"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_pending_returns_authorization_url(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "pending", authorization_url="https://auth.example.com/authorize"
        )

        # Act
        result = client.get_oauth_authorization_session("urn:sid")

        # Assert
        assert result.session_status == "pending"
        assert result.authorization_url == "https://auth.example.com/authorize"

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_completed_returns_authentication_token_id(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "completed", authentication_token_id="tok-1"
        )

        # Act
        result = client.get_oauth_authorization_session("urn:sid")

        # Assert
        assert result.session_status == "completed"
        assert result.authentication_token_id == "tok-1"

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_failed_returns_error_info(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "failed", error_code="access_denied", error_description="user denied"
        )

        # Act
        result = client.get_oauth_authorization_session("urn:sid")

        # Assert
        assert result.session_status == "failed"
        assert result.error_code == "access_denied"
        assert result.error_description == "user denied"

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_not_found_raises_client_exception(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.get_oauth_authorization_session_with_options.side_effect = TeaException(
            {"code": 404, "data": {"error": "oauth_session_not_found", "request_id": "r1"}}
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.get_oauth_authorization_session("urn:missing")
        assert "oauth_session_not_found" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_sets_bearer_authorization_header(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "pending"
        )

        # Act
        client.get_oauth_authorization_session("urn:sid")

        # Assert
        call_args = mock_client_instance.get_oauth_authorization_session_with_options.call_args
        headers = call_args[0][2]
        expected_auth = f"{HttpConstants.BEARER}{HttpConstants.SPACE}test_bearer_token"
        assert headers.authorization == expected_auth

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_raises_unexpected_exception_for_general_error(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.get_oauth_authorization_session_with_options.side_effect = Exception("Network error")

        # Act & Assert
        with pytest.raises(IDaaSUnexpectedException) as exc_info:
            client.get_oauth_authorization_session("urn:sid")
        assert "Network error" in str(exc_info.value)


class TestPollOAuthAuthenticationToken:
    """Test suite for poll_oauth_authentication_token"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_token_available_returns_without_callback_or_polling(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_token=True
        )
        callback = Mock()

        # Act
        result = client.poll_oauth_authentication_token("provider-1", callback)

        # Assert
        assert result.has_oauth_access_token_content() is True
        callback.assert_not_called()
        mock_client_instance.get_oauth_authorization_session_with_options.assert_not_called()

    @patch("cloud_idaas.pam_client.idaas_pam_client.time")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_authorize_then_poll_until_completed(self, mock_client_class, mock_time):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_time.monotonic.side_effect = [0, 1, 2, 3, 4]
        mock_client_instance.fetch_oauth_authentication_token_with_options.side_effect = [
            _mock_fetch_response(has_session=True),
            _mock_fetch_response(has_token=True),
        ]
        mock_client_instance.get_oauth_authorization_session_with_options.side_effect = [
            _mock_session_response("pending"),
            _mock_session_response("completed", authentication_token_id="tok-1"),
        ]
        callback = Mock()

        # Act
        result = client.poll_oauth_authentication_token("provider-1", callback)

        # Assert
        callback.assert_called_once_with("https://auth.example.com/authorize")
        assert result.has_oauth_access_token_content() is True
        # second fetch must not carry force_authentication (Java-aligned: no options)
        fetch_calls = mock_client_instance.fetch_oauth_authentication_token_with_options.call_args_list
        second_fetch_request = fetch_calls[1][0][1]
        assert second_fetch_request.force_authentication is None

    @patch("cloud_idaas.pam_client.idaas_pam_client.time")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_session_failed_raises_client_exception(self, mock_client_class, mock_time):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_time.monotonic.side_effect = [0, 1, 2]
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "failed", error_code="access_denied", error_description="user denied"
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.poll_oauth_authentication_token("provider-1", Mock())
        assert "user denied" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.time")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_session_expired_raises_client_exception(self, mock_client_class, mock_time):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_time.monotonic.side_effect = [0, 1, 2]
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "expired"
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.poll_oauth_authentication_token("provider-1", Mock())
        assert "expired" in str(exc_info.value)

    @patch("cloud_idaas.pam_client.idaas_pam_client.time")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_polling_retries_exhausted_raises_timeout(self, mock_client_class, mock_time):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_time.monotonic.side_effect = [0, 1, 2, 3, 4]
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )
        mock_client_instance.get_oauth_authorization_session_with_options.return_value = _mock_session_response(
            "pending"
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.poll_oauth_authentication_token("provider-1", Mock(), max_polling_retries=2)
        assert "timed out" in str(exc_info.value).lower()

    @patch("cloud_idaas.pam_client.idaas_pam_client.time")
    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_hard_timeout_stops_before_retries(self, mock_client_class, mock_time):
        # Arrange: deadline = 0 + 180; first loop check sees 200 >= 180
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_time.monotonic.side_effect = [0, 200]
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )

        # Act & Assert
        with pytest.raises(ClientException) as exc_info:
            client.poll_oauth_authentication_token("provider-1", Mock(), max_polling_retries=60)
        assert "timed out" in str(exc_info.value).lower()
        mock_client_instance.get_oauth_authorization_session_with_options.assert_not_called()

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_callback_exception_propagates(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_session=True
        )
        callback = Mock(side_effect=ValueError("boom"))

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            client.poll_oauth_authentication_token("provider-1", callback)
        assert "boom" in str(exc_info.value)


class TestFetchOAuthAuthenticationTokenDeprecation:
    """Test suite for the deprecated fetch_oauth_authentication_token"""

    @patch("cloud_idaas.pam_client.idaas_pam_client.Client")
    def test_emits_deprecation_warning_and_returns_token(self, mock_client_class):
        # Arrange
        client, mock_client_instance = _make_oauth_client(mock_client_class)
        mock_client_instance.fetch_oauth_authentication_token_with_options.return_value = _mock_fetch_response(
            has_token=True
        )

        # Act & Assert
        with pytest.warns(DeprecationWarning):
            token = client.fetch_oauth_authentication_token("provider-1")
        assert token == "at_value"
