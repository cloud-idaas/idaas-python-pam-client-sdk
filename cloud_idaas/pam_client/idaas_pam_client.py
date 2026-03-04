import logging
from typing import Optional

from alibabacloud_eiam_developerapi20220225 import models as eiam_models
from alibabacloud_eiam_developerapi20220225.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from cloud_idaas.core import (
    ClientException,
    ConfigException,
    CredentialException,
    HttpConstants,
)
from cloud_idaas.core.factory.idaas_credential_provider_factory import IDaaSCredentialProviderFactory
from cloud_idaas.core.provider.idaas_credential_provider import IDaaSCredentialProvider
from darabonba.runtime import RuntimeOptions
from Tea.exceptions import TeaException

from .domain.pam_client_constants import PamClientConstants

logger = logging.getLogger(__name__)

class IDaaSPamClient:

    def __init__(
        self,
        developer_api_endpoint: Optional[str] = None,
        idaas_instance_id: Optional[str] = None,
        credential_provider: Optional[IDaaSCredentialProvider] = None,
    ):
        self._developer_api_endpoint = self._get_developer_api_endpoint(developer_api_endpoint)
        if self._developer_api_endpoint is None:
            raise ConfigException("DeveloperApiEndpoint can not be empty")
        self._idaas_instance_id = (
            idaas_instance_id
            if idaas_instance_id is not None
            else IDaaSCredentialProviderFactory.get_idaas_instance_id()
        )
        if self._idaas_instance_id is None:
            raise ConfigException("IDaasInstanceId can not be empty")
        self._credential_provider = (
            credential_provider
            if credential_provider is not None
            else IDaaSCredentialProviderFactory.get_idaas_credential_provider_by_scope(PamClientConstants.SCOPE)
        )
        if self._credential_provider is None:
            raise ConfigException("CredentialProvider can not be empty")

        try:
            config = open_api_models.Config()
            config.endpoint = self._developer_api_endpoint
            self._client = Client(config)
        except Exception as e:
            logger.error(f"Error occurred while creating IDaaSPamClient: {e}")
            raise ConfigException(str(e)) from e

    def _get_developer_api_endpoint(self, developer_api_endpoint: Optional[str]) -> Optional[str]:
        real_endpoint = (
            developer_api_endpoint
            if developer_api_endpoint is not None
            else IDaaSCredentialProviderFactory.get_developer_api_endpoint()
        )

        if real_endpoint is None or real_endpoint.strip() == "":
            return real_endpoint

        if real_endpoint.startswith("https://"):
            real_endpoint = real_endpoint[8:]
        elif real_endpoint.startswith("http://"):
            real_endpoint = real_endpoint[7:]

        return real_endpoint

    def get_api_key(self, credential_identifier: str) -> Optional[str]:
        try:
            request = eiam_models.ObtainCredentialRequest()
            request.credential_identifier = credential_identifier
            headers = eiam_models.ObtainCredentialHeaders()
            headers.authorization = (
                HttpConstants.BEARER
                + HttpConstants.SPACE
                + self._credential_provider.get_bearer_token()
            )
            response = self._client.obtain_credential_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                credential_content = response_body.credential_content
                if credential_content is not None:
                    api_key_content = credential_content.api_key_content
                    if api_key_content is not None:
                        return api_key_content.api_key
                    else:
                        logger.info(
                            "The credential retrieval operation using the CredentialIdentifier was successful; however, "
                            + "the ApiContent field returned null, suggesting that an incorrect API method may have been invoked."
                        )
            return None
        except TeaException as e:
            status_code = e.code
            if status_code >= 400 and status_code < 500:
                error_code = e.data.get("error")
                error_description = e.data.get("error_description")
                request_id = e.data.get("request_id")
                message = f"Error code: {error_code}, error description: {error_description}, request id: {request_id}"
                raise ClientException(error_code, message, request_id) from e
            elif status_code >= 500:
                logging.error(f"Server Error Message: {e}")
                raise e
            else:
                logging.error(f"Error occurred while obtaining credential: {e}")
                raise e
        except Exception as e:
            logger.error(f"Error occurred while obtaining credential: {e}")
            raise CredentialException(str(e), e) from e

    @staticmethod
    def builder():
        return IDaaSPamClient.IDaaSPamClientBuilder()

    class IDaaSPamClientBuilder:
        def __init__(self):
            self._developer_api_endpoint = None
            self._idaas_instance_id = None
            self._credential_provider = None

        def developerApiEndpoint(self, developer_api_endpoint: str):
            self._developer_api_endpoint = developer_api_endpoint
            return self

        def idaasInstanceId(self, idaas_instance_id: str):
            self._idaas_instance_id = idaas_instance_id
            return self

        def credentialProvider(self, credential_provider: IDaaSCredentialProvider):
            self._credential_provider = credential_provider
            return self

        def build(self):
            return IDaaSPamClient(self._developer_api_endpoint, self._idaas_instance_id, self._credential_provider)
