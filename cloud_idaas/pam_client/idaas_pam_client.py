import logging
from typing import Optional

from alibabacloud_eiam_developerapi20220225 import models as eiam_models
from alibabacloud_eiam_developerapi20220225.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from darabonba.runtime import RuntimeOptions
from Tea.exceptions import TeaException

from cloud_idaas.core import (
    ClientException,
    ConfigException,
    HttpConstants,
    IDaaSCredentialProvider,
    IDaaSCredentialProviderFactory,
    IDaaSUnexpectedException,
)

from .domain.authentication_token import AuthenticationToken
from .domain.jwt_content import JwtContent
from .domain.jwt_token_response import JwtTokenResponse
from .domain.next_token_pageable_response import NextTokenPageableResponse
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

    def _handle_tea_exception(self, e: TeaException, operation: str):
        # Extract status code from e.code or e.data.statusCode
        status_code = 0
        if e.code:
            try:
                status_code = int(e.code)
            except (ValueError, TypeError):
                status_code = 0
        elif e.data and "statusCode" in e.data:
            try:
                status_code = int(e.data["statusCode"])
            except (ValueError, TypeError):
                status_code = 0

        if status_code >= 400 and status_code < 500:
            error_code = e.data.get("error") if e.data else None
            error_description = e.data.get("error_description") if e.data else None
            request_id = e.data.get("request_id") if e.data else None
            message = f"Error code: {error_code}, error description: {error_description}, request id: {request_id}"
            raise ClientException(error_code, message, request_id) from e
        elif status_code >= 500:
            logging.error(f"Server Error Message: {e}")
            raise e
        else:
            logging.error(f"Error occurred while {operation}: {e}")
            raise e

    def _handle_exception(self, e: Exception, operation: str):
        logger.error(f"Error occurred while {operation}: {e}")
        raise IDaaSUnexpectedException(str(e), e) from e

    def get_api_key(self, credential_identifier: str) -> Optional[str]:
        try:
            request = eiam_models.ObtainCredentialRequest()
            request.credential_identifier = credential_identifier
            headers = eiam_models.ObtainCredentialHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
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
                            "The credential retrieval operation using the CredentialIdentifier was successful; "
                            "however, the ApiContent field returned null, suggesting that an incorrect API method "
                            "may have been invoked."
                        )
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "obtaining credential")
        except Exception as e:
            self._handle_exception(e, "obtaining credential")

    def fetch_oauth_authentication_token(
        self,
        credential_provider_identifier: str,
        scope: str = None,
    ) -> Optional[str]:
        try:
            request = eiam_models.FetchOAuthAuthenticationTokenRequest()
            request.credential_provider_identifier = credential_provider_identifier
            request.scope = scope
            headers = eiam_models.FetchOAuthAuthenticationTokenHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            response = self._client.fetch_oauth_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                if response_body is not None:
                    oauth_access_token_content = response_body.oauth_access_token_content
                    if oauth_access_token_content is not None:
                        return oauth_access_token_content.access_token_value
                    else:
                        logger.info(
                            "The OAuth authentication token fetch was successful; however, "
                            + "the OAuthAccessTokenContent field returned null."
                        )
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "fetching OAuth authentication token")
        except Exception as e:
            self._handle_exception(e, "fetching OAuth authentication token")

    def generate_jwt_authentication_token(
        self,
        credential_provider_identifier: str,
        subject: str,
        audiences: list,
        issuer: str = None,
        custom_claims: dict = None,
        expiration: int = None,
        include_derived_short_token: bool = None,
    ) -> Optional[JwtTokenResponse]:
        try:
            request = eiam_models.GenerateJwtAuthenticationTokenRequest()
            request.credential_provider_identifier = credential_provider_identifier
            request.subject = subject
            request.audiences = audiences
            request.issuer = issuer
            request.custom_claims = custom_claims
            request.expiration = expiration
            request.include_derived_short_token = include_derived_short_token
            headers = eiam_models.GenerateJwtAuthenticationTokenHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            response = self._client.generate_jwt_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                if response_body is not None:
                    jwt_content = response_body.jwt_content
                    if jwt_content is not None:
                        jwt_content_obj = JwtContent(
                            jwt_value=jwt_content.jwt_value,
                            derived_short_token=jwt_content.derived_short_token,
                        )
                        return JwtTokenResponse(
                            authentication_token_id=response_body.authentication_token_id,
                            consumer_type=response_body.consumer_type,
                            consumer_id=response_body.consumer_id,
                            jwt_content=jwt_content_obj,
                        )
                    else:
                        logger.info(
                            "The JWT authentication token generation was successful; however, "
                            + "the JwtContent field returned null."
                        )
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "generating JWT authentication token")
        except Exception as e:
            self._handle_exception(e, "generating JWT authentication token")

    def obtain_jwt_authentication_token(
        self,
        consumer_id: str,
        authentication_token_id: str,
    ) -> Optional[JwtContent]:
        """Obtain JWT authentication token by consumer ID and authentication token ID.

        Args:
            consumer_id: The consumer ID
            authentication_token_id: The authentication token ID

        Returns:
            JwtContent if successful, None otherwise
        """
        try:
            request = eiam_models.ObtainJwtAuthenticationTokenRequest()
            request.consumer_id = consumer_id
            request.authentication_token_id = authentication_token_id
            headers = eiam_models.ObtainJwtAuthenticationTokenHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            response = self._client.obtain_jwt_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                if response_body is not None:
                    jwt_content = response_body.jwt_content
                    if jwt_content is not None:
                        return JwtContent(
                            jwt_value=jwt_content.jwt_value,
                            derived_short_token=jwt_content.derived_short_token,
                        )
                    else:
                        logger.info(
                            "The JWT authentication token retrieval was successful; however, "
                            + "the JwtContent field returned null."
                        )
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "obtaining JWT authentication token")
        except Exception as e:
            self._handle_exception(e, "obtaining JWT authentication token")

    def obtain_jwt_authentication_token_by_derived_short_token(
        self,
        derived_short_token: str,
    ) -> Optional[JwtContent]:
        try:
            request = eiam_models.ObtainJwtAuthenticationTokenByDerivedShortTokenRequest()
            request.derived_short_token = derived_short_token
            response = self._client.obtain_jwt_authentication_token_by_derived_short_token_with_options(
                self._idaas_instance_id,
                request,
                {},
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                if response_body is not None:
                    jwt_content = response_body.jwt_content
                    if jwt_content is not None:
                        return JwtContent(
                            jwt_value=jwt_content.jwt_value,
                            derived_short_token=jwt_content.derived_short_token,
                        )
                    else:
                        logger.info(
                            "The JWT authentication token retrieval by derived short token was successful; however, "
                            + "the JwtContent field returned null."
                        )
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "obtaining JWT authentication token by derived short token")
        except Exception as e:
            self._handle_exception(e, "obtaining JWT authentication token by derived short token")

    def list_authentication_tokens(
        self,
        consumer_id: str,
        credential_provider_identifier: str,
        next_token: str = None,
        max_results: int = None,
        revoked: bool = None,
        expired: bool = None,
    ) -> Optional[NextTokenPageableResponse[AuthenticationToken]]:
        try:
            request = eiam_models.ListAuthenticationTokensRequest()
            request.credential_provider_identifier = credential_provider_identifier
            request.consumer_id = consumer_id
            request.next_token = next_token
            request.max_results = max_results
            request.revoked = revoked
            request.expired = expired
            headers = eiam_models.ListAuthenticationTokensHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            response = self._client.list_authentication_tokens_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                entities = [
                    AuthenticationToken(
                        instance_id=e.instance_id,
                        authentication_token_id=e.authentication_token_id,
                        authentication_token_type=e.authentication_token_type,
                        credential_provider_id=e.credential_provider_id,
                        creator_type=e.creator_type,
                        creator_id=e.creator_id,
                        consumer_type=e.consumer_type,
                        consumer_id=e.consumer_id,
                        revoked=e.revoked,
                        create_time=e.create_time,
                        update_time=e.update_time,
                        expiration_time=e.expiration_time,
                    )
                    for e in (response_body.entities or [])
                ]
                return NextTokenPageableResponse(
                    entities=entities,
                    total_count=response_body.total_count,
                    max_results=response_body.max_results,
                    next_token=response_body.next_token,
                )
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "listing authentication tokens")
        except Exception as e:
            self._handle_exception(e, "listing authentication tokens")

    def reinstate_authentication_token(self, token: str, token_type_hint: str = None) -> None:
        try:
            request = eiam_models.ReinstateAuthenticationTokenRequest()
            request.token = token
            request.token_type_hint = token_type_hint
            headers = eiam_models.ReinstateAuthenticationTokenHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            self._client.reinstate_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
        except TeaException as e:
            self._handle_tea_exception(e, "reinstating authentication token")
        except Exception as e:
            self._handle_exception(e, "reinstating authentication token")

    def reinstate_authentication_token_by_consumer(
        self,
        consumer_id: str,
        credential_provider_identifier: str,
    ) -> None:
        try:
            request = eiam_models.ReinstateAuthenticationTokenByConsumerRequest()
            request.consumer_id = consumer_id
            request.credential_provider_identifier = credential_provider_identifier
            headers = eiam_models.ReinstateAuthenticationTokenByConsumerHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            self._client.reinstate_authentication_token_by_consumer_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
        except TeaException as e:
            self._handle_tea_exception(e, "reinstating authentication token by consumer")
        except Exception as e:
            self._handle_exception(e, "reinstating authentication token by consumer")

    def revoke_authentication_token(self, token: str, token_type_hint: str = None) -> None:
        try:
            request = eiam_models.RevokeAuthenticationTokenRequest()
            request.token = token
            request.token_type_hint = token_type_hint
            headers = eiam_models.RevokeAuthenticationTokenHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            self._client.revoke_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
        except TeaException as e:
            self._handle_tea_exception(e, "revoking authentication token")
        except Exception as e:
            self._handle_exception(e, "revoking authentication token")

    def revoke_authentication_token_by_consumer(
        self,
        consumer_id: str,
        credential_provider_identifier: str,
    ) -> None:
        try:
            request = eiam_models.RevokeAuthenticationTokenByConsumerRequest()
            request.consumer_id = consumer_id
            request.credential_provider_identifier = credential_provider_identifier
            headers = eiam_models.RevokeAuthenticationTokenByConsumerHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            self._client.revoke_authentication_token_by_consumer_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
        except TeaException as e:
            self._handle_tea_exception(e, "revoking authentication token by consumer")
        except Exception as e:
            self._handle_exception(e, "revoking authentication token by consumer")

    def validate_authentication_token(self, token: str, token_type_hint: str = None) -> Optional[bool]:
        try:
            request = eiam_models.ValidateAuthenticationTokenRequest()
            request.token = token
            request.token_type_hint = token_type_hint
            response = self._client.validate_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                {},
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                if response_body is not None:
                    return response_body.active
            return None
        except TeaException as e:
            self._handle_tea_exception(e, "validating authentication token")
        except Exception as e:
            self._handle_exception(e, "validating authentication token")

    @staticmethod
    def builder():
        return IDaaSPamClient.IDaaSPamClientBuilder()

    class IDaaSPamClientBuilder:
        def __init__(self):
            self._developer_api_endpoint = None
            self._idaas_instance_id = None
            self._credential_provider = None

        def developer_api_endpoint(self, developer_api_endpoint: str):
            self._developer_api_endpoint = developer_api_endpoint
            return self

        def idaas_instance_id(self, idaas_instance_id: str):
            self._idaas_instance_id = idaas_instance_id
            return self

        def credential_provider(self, credential_provider: IDaaSCredentialProvider):
            self._credential_provider = credential_provider
            return self

        def build(self):
            return IDaaSPamClient(self._developer_api_endpoint, self._idaas_instance_id, self._credential_provider)
