"""Unit tests for IDaaSPamClient class

This module contains comprehensive unit tests for the IDaaSPamClient class,
covering initialization, endpoint processing, API key retrieval, and builder pattern.
"""

from unittest.mock import Mock, patch

import pytest
from cloud_idaas.core import ClientException, ConfigException, CredentialException, HttpConstants
from Tea.exceptions import TeaException

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
    def test_get_api_key_returns_none_for_non_200_status(self, mock_client_class, mock_factory):
        """Test get_api_key returns None for non-200 status code"""
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

        # Act
        api_key = client.get_api_key("test_credential_identifier")

        # Assert
        assert api_key is None

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
        tea_exception = TeaException({
            "code": 400,
            "data": {
                "error": "invalid_request",
                "error_description": "Invalid credential identifier",
                "request_id": "req_123",
            },
        })

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
    def test_get_api_key_raises_credential_exception_for_general_error(self, mock_client_class, mock_factory):
        """Test get_api_key raises CredentialException for general errors"""
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
        with pytest.raises(CredentialException) as exc_info:
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
        builder.developerApiEndpoint("test.endpoint.com")
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
        builder.idaasInstanceId("custom_instance_id")
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
        builder.credentialProvider(mock_provider)
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
            .developerApiEndpoint("test.endpoint.com")
            .idaasInstanceId("test_instance")
            .credentialProvider(mock_provider)
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
