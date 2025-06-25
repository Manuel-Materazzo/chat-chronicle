from datetime import datetime
from typing import TypedDict


class Chunk(TypedDict):
    content: str
    messages_count: int
    start_timestamp: datetime
    end_timestamp: datetime
    token_count: int
