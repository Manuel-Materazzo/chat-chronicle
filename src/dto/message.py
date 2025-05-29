from datetime import datetime
from typing import TypedDict


class Message(TypedDict):
    sender_name: str
    timestamp: datetime
    content: str
