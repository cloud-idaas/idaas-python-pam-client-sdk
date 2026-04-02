from dataclasses import dataclass
from typing import Optional


@dataclass
class JwtContent:
    jwt_value: str
    derived_short_token: Optional[str] = None
