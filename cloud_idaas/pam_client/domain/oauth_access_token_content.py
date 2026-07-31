from dataclasses import dataclass
from typing import Optional


@dataclass
class OAuthAccessTokenContent:
    """OAuth Access Token content."""

    access_token_value: Optional[str] = None  # access_token value (sensitive; never log in plaintext)
    token_type: Optional[str] = None  # token_type, usually Bearer
    scope: Optional[str] = None  # authorization scope
