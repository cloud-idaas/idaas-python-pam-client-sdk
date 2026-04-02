from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class NextTokenPageableResponse(Generic[T]):
    entities: list[T]
    total_count: int
    max_results: int
    next_token: Optional[str] = None
