from dataclasses import dataclass
from typing import Optional


@dataclass
class OAuthAuthorizationSession:
    """OAuth authorization session info (returned when user authorization is required)."""

    session_id: Optional[str] = None
    session_uri: Optional[str] = None  # urn:ietf:params:oauth:request_uri:{sessionId}
    authorization_url: Optional[str] = None  # URL to guide the user through authorization
    session_status: Optional[str] = None  # e.g. pending
