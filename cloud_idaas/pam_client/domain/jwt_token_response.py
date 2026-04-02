from dataclasses import dataclass

from .jwt_content import JwtContent


@dataclass
class JwtTokenResponse:
    """JWT token generation response.

    Contains the JWT token content along with authentication token metadata.
    """

    authentication_token_id: str
    consumer_type: str
    consumer_id: str
    jwt_content: JwtContent
