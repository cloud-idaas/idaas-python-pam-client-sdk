from dataclasses import dataclass


@dataclass
class AuthenticationToken:
    instance_id: str
    authentication_token_id: str
    authentication_token_type: str
    credential_provider_id: str
    creator_type: str
    creator_id: str
    consumer_type: str
    consumer_id: str
    revoked: bool
    create_time: int
    update_time: int
    expiration_time: int
