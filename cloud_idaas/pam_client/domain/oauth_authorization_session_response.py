from dataclasses import dataclass
from typing import Optional


@dataclass
class OAuthAuthorizationSessionResponse:
    """Full response of GetOAuthAuthorizationSession."""

    instance_id: Optional[str] = None
    session_id: Optional[str] = None
    session_uri: Optional[str] = None
    session_status: Optional[str] = None
    credential_provider_identifier: Optional[str] = None
    consumer_type: Optional[str] = None
    consumer_id: Optional[str] = None
    creator_type: Optional[str] = None
    creator_id: Optional[str] = None
    authorization_url: Optional[str] = None  # returned when status=pending
    expiration_time: Optional[int] = None
    authentication_token_id: Optional[str] = None  # returned when status=completed
    error_code: Optional[str] = None  # returned when status=failed
    error_description: Optional[str] = None  # returned when status=failed
