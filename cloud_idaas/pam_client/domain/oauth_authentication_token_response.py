from dataclasses import dataclass
from typing import Optional

from .oauth_access_token_content import OAuthAccessTokenContent
from .oauth_authorization_session import OAuthAuthorizationSession


@dataclass
class OAuthAuthenticationTokenResponse:
    """Rich response of FetchOAuthAuthenticationToken (2LO + 3LO).

    oauth_access_token_content and oauth_authorization_session are mutually
    exclusive and never present at the same time.
    """

    instance_id: Optional[str] = None
    authentication_token_id: Optional[str] = None
    credential_provider_id: Optional[str] = None
    authentication_token_type: Optional[str] = None
    revoked: Optional[bool] = None
    creator_type: Optional[str] = None
    creator_id: Optional[str] = None
    consumer_type: Optional[str] = None
    consumer_id: Optional[str] = None
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    expiration_time: Optional[int] = None
    oauth_access_token_content: Optional[OAuthAccessTokenContent] = None
    oauth_authorization_session: Optional[OAuthAuthorizationSession] = None

    def has_oauth_access_token_content(self) -> bool:
        """Whether the token is already available."""
        return self.oauth_access_token_content is not None

    def has_oauth_authorization_session(self) -> bool:
        """Whether user authorization is required."""
        return self.oauth_authorization_session is not None
