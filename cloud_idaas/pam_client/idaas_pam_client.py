import logging
import time
import warnings
from typing import Callable, Optional

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
from .domain.oauth_access_token_content import OAuthAccessTokenContent
from .domain.oauth_authentication_token_response import OAuthAuthenticationTokenResponse
from .domain.oauth_authorization_session import OAuthAuthorizationSession
from .domain.oauth_authorization_session_response import OAuthAuthorizationSessionResponse
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
            raise IDaaSUnexpectedException(f"Failed to obtain credential, status code: {response.status_code}")
        except TeaException as e:
            self._handle_tea_exception(e, "obtaining credential")
        except IDaaSUnexpectedException:
            raise
        except Exception as e:
            self._handle_exception(e, "obtaining credential")

    def fetch_oauth_authentication_token(
        self,
        credential_provider_identifier: str,
        scope: str = None,
    ) -> Optional[str]:
        """.. deprecated:: Use :meth:`fetch_oauth_authentication_token_v2` instead.

        This 2LO-only method returns a plain access token string. The new
        ``fetch_oauth_authentication_token_v2`` covers both 2LO and 3LO and returns a rich
        ``OAuthAuthenticationTokenResponse``. The signature and return type are kept unchanged
        for backward compatibility.
        """
        warnings.warn(
            "fetch_oauth_authentication_token is deprecated; use fetch_oauth_authentication_token_v2 instead.",
            DeprecationWarning,
            stacklevel=2,
        )
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
            raise IDaaSUnexpectedException(
                f"Failed to fetch OAuth authentication token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "fetching OAuth authentication token")
        except IDaaSUnexpectedException:
            raise
        except Exception as e:
            self._handle_exception(e, "fetching OAuth authentication token")

    def _build_oauth_authentication_token_response(self, response_body) -> OAuthAuthenticationTokenResponse:
        result = OAuthAuthenticationTokenResponse(
            instance_id=response_body.instance_id,
            authentication_token_id=response_body.authentication_token_id,
            credential_provider_id=response_body.credential_provider_id,
            authentication_token_type=response_body.authentication_token_type,
            revoked=response_body.revoked,
            creator_type=response_body.creator_type,
            creator_id=response_body.creator_id,
            consumer_type=response_body.consumer_type,
            consumer_id=response_body.consumer_id,
            create_time=response_body.create_time,
            update_time=response_body.update_time,
            expiration_time=response_body.expiration_time,
        )
        oauth_access_token_content = response_body.oauth_access_token_content
        if oauth_access_token_content is not None:
            result.oauth_access_token_content = OAuthAccessTokenContent(
                access_token_value=oauth_access_token_content.access_token_value,
                token_type=oauth_access_token_content.token_type,
                scope=oauth_access_token_content.scope,
            )
        oauth_authorization_session = response_body.oauth_authorization_session
        if oauth_authorization_session is not None:
            result.oauth_authorization_session = OAuthAuthorizationSession(
                session_id=oauth_authorization_session.session_id,
                session_uri=oauth_authorization_session.session_uri,
                authorization_url=oauth_authorization_session.authorization_url,
                session_status=oauth_authorization_session.session_status,
            )
        return result

    def fetch_oauth_authentication_token_v2(
        self,
        credential_provider_identifier: str,
        authorization_flow: str,
        scope: Optional[str] = None,
        force_authentication: Optional[bool] = None,
        custom_parameters: Optional[dict] = None,
    ) -> Optional[OAuthAuthenticationTokenResponse]:
        """Fetch an OAuth authentication token, covering both 2LO and 3LO flows.

        The authorization_flow argument (PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M or
        OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION) is used for SDK-side validation only and is
        NOT sent to the server; the server determines the actual flow by CredentialProvider config.
        """
        if authorization_flow not in (
            PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M,
            PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
        ):
            raise ClientException(
                "invalid_authorization_flow",
                "authorization_flow must be either 'm2m' or 'user_federation'",
            )
        try:
            request = eiam_models.FetchOAuthAuthenticationTokenRequest()
            request.credential_provider_identifier = credential_provider_identifier
            request.scope = scope
            request.force_authentication = force_authentication
            request.custom_parameters = custom_parameters
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
                    result = self._build_oauth_authentication_token_response(response_body)
                    if (
                        authorization_flow == PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M
                        and result.has_oauth_authorization_session()
                    ):
                        raise ClientException(
                            "authorization_flow_mismatch",
                            "authorization_flow 'm2m' does not match the CredentialProvider "
                            "configuration, which requires user authorization (user_federation)",
                        )
                    logger.info(
                        f"Fetched OAuth authentication token, "
                        f"has_access_token={result.has_oauth_access_token_content()}, "
                        f"has_authorization_session={result.has_oauth_authorization_session()}"
                    )
                    return result
                return None
            raise IDaaSUnexpectedException(
                f"Failed to fetch OAuth authentication token, status code: {response.status_code}"
            )
        except ClientException:
            raise
        except TeaException as e:
            self._handle_tea_exception(e, "fetching OAuth authentication token v2")
        except IDaaSUnexpectedException:
            raise
        except Exception as e:
            self._handle_exception(e, "fetching OAuth authentication token v2")

    def _build_oauth_authorization_session_response(self, response_body) -> OAuthAuthorizationSessionResponse:
        return OAuthAuthorizationSessionResponse(
            instance_id=response_body.instance_id,
            session_id=response_body.session_id,
            session_uri=response_body.session_uri,
            session_status=response_body.session_status,
            credential_provider_identifier=response_body.credential_provider_identifier,
            consumer_type=response_body.consumer_type,
            consumer_id=response_body.consumer_id,
            creator_type=response_body.creator_type,
            creator_id=response_body.creator_id,
            authorization_url=response_body.authorization_url,
            expiration_time=response_body.expiration_time,
            authentication_token_id=response_body.authentication_token_id,
            error_code=response_body.error_code,
            error_description=response_body.error_description,
        )

    def get_oauth_authorization_session(
        self,
        session_uri: str,
    ) -> Optional[OAuthAuthorizationSessionResponse]:
        """Query the current status of an OAuth authorization session by its session URI."""
        try:
            request = eiam_models.GetOAuthAuthorizationSessionRequest()
            request.session_uri = session_uri
            headers = eiam_models.GetOAuthAuthorizationSessionHeaders()
            headers.authorization = (
                HttpConstants.BEARER + HttpConstants.SPACE + self._credential_provider.get_bearer_token()
            )
            response = self._client.get_oauth_authorization_session_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                response_body = response.body
                if response_body is not None:
                    result = self._build_oauth_authorization_session_response(response_body)
                    logger.info(f"Queried OAuth authorization session, session_status={result.session_status}")
                    return result
                return None
            raise IDaaSUnexpectedException(
                f"Failed to get OAuth authorization session, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "getting OAuth authorization session")
        except IDaaSUnexpectedException:
            raise
        except Exception as e:
            self._handle_exception(e, "getting OAuth authorization session")

    def poll_oauth_authentication_token(
        self,
        credential_provider_identifier: str,
        on_authorization_url: Callable[[str], None],
        scope: Optional[str] = None,
        force_authentication: Optional[bool] = None,
        custom_parameters: Optional[dict] = None,
        max_polling_retries: Optional[int] = None,
    ) -> Optional[OAuthAuthenticationTokenResponse]:
        """End-to-end 3LO helper: initiate authorization, notify the authorization URL via a
        callback, poll until completion, then fetch and return the token.

        This method blocks the calling thread while polling. On success the returned response
        always contains oauth_access_token_content and never oauth_authorization_session.
        """
        result = self.fetch_oauth_authentication_token_v2(
            credential_provider_identifier,
            PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
            scope=scope,
            force_authentication=force_authentication,
            custom_parameters=custom_parameters,
        )
        # Token already available: return directly without callback or polling.
        if result is None or result.has_oauth_access_token_content():
            return result
        session = result.oauth_authorization_session
        if session is None or session.session_uri is None:
            raise IDaaSUnexpectedException("Authorization session is missing from the fetch response")
        # Notify the caller of the authorization URL; callback exceptions propagate unchanged.
        on_authorization_url(session.authorization_url)
        self._poll_until_completed(session.session_uri, max_polling_retries)
        # Session completed: fetch the now-available token (no options, matching the server-stored token).
        final_response = self.fetch_oauth_authentication_token_v2(
            credential_provider_identifier,
            PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
            scope=scope,
            custom_parameters=custom_parameters,
        )
        if final_response is None or not final_response.has_oauth_access_token_content():
            raise IDaaSUnexpectedException("Authorization session completed but no access token was returned")
        return final_response

    def _poll_until_completed(self, session_uri: str, max_polling_retries: Optional[int]) -> None:
        interval = PamClientConstants.DEFAULT_POLLING_INTERVAL_SECONDS
        max_retries = (
            max_polling_retries if max_polling_retries is not None else PamClientConstants.DEFAULT_MAX_POLLING_RETRIES
        )
        deadline = time.monotonic() + PamClientConstants.MAX_POLLING_DURATION_SECONDS
        for _ in range(max_retries):
            if time.monotonic() + interval > deadline:
                raise ClientException(
                    "polling_timeout",
                    "Polling for OAuth authorization timed out after "
                    f"{PamClientConstants.MAX_POLLING_DURATION_SECONDS} seconds",
                )
            time.sleep(interval)
            session_response = self.get_oauth_authorization_session(session_uri)
            status = session_response.session_status if session_response is not None else None
            if status == PamClientConstants.SESSION_STATUS_COMPLETED:
                return
            if status == PamClientConstants.SESSION_STATUS_FAILED:
                raise ClientException(
                    session_response.error_code if session_response.error_code is not None else "authorization_failed",
                    session_response.error_description
                    if session_response.error_description is not None
                    else "OAuth authorization failed",
                )
            if status == PamClientConstants.SESSION_STATUS_EXPIRED:
                raise ClientException(
                    "authorization_session_expired",
                    "The OAuth authorization session has expired",
                )
            # pending / callback_received: continue polling
        raise ClientException(
            "polling_timeout",
            f"Polling for OAuth authorization timed out after {max_retries} retries",
        )

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
            raise IDaaSUnexpectedException(
                f"Failed to generate JWT authentication token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "generating JWT authentication token")
        except IDaaSUnexpectedException:
            raise
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
            raise IDaaSUnexpectedException(
                f"Failed to obtain JWT authentication token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "obtaining JWT authentication token")
        except IDaaSUnexpectedException:
            raise
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
            raise IDaaSUnexpectedException(
                f"Failed to obtain JWT authentication token by derived short token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "obtaining JWT authentication token by derived short token")
        except IDaaSUnexpectedException:
            raise
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
            raise IDaaSUnexpectedException(f"Failed to list authentication tokens, status code: {response.status_code}")
        except TeaException as e:
            self._handle_tea_exception(e, "listing authentication tokens")
        except IDaaSUnexpectedException:
            raise
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
            response = self._client.reinstate_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                return
            raise IDaaSUnexpectedException(
                f"Failed to reinstate authentication token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "reinstating authentication token")
        except IDaaSUnexpectedException:
            raise
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
            response = self._client.reinstate_authentication_token_by_consumer_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                return
            raise IDaaSUnexpectedException(
                f"Failed to reinstate authentication token by consumer, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "reinstating authentication token by consumer")
        except IDaaSUnexpectedException:
            raise
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
            response = self._client.revoke_authentication_token_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                return
            raise IDaaSUnexpectedException(
                f"Failed to revoke authentication token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "revoking authentication token")
        except IDaaSUnexpectedException:
            raise
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
            response = self._client.revoke_authentication_token_by_consumer_with_options(
                self._idaas_instance_id,
                request,
                headers,
                RuntimeOptions(),
            )
            if response.status_code == PamClientConstants.STATUS_CODE_200:
                return
            raise IDaaSUnexpectedException(
                f"Failed to revoke authentication token by consumer, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "revoking authentication token by consumer")
        except IDaaSUnexpectedException:
            raise
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
            raise IDaaSUnexpectedException(
                f"Failed to validate authentication token, status code: {response.status_code}"
            )
        except TeaException as e:
            self._handle_tea_exception(e, "validating authentication token")
        except IDaaSUnexpectedException:
            raise
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
