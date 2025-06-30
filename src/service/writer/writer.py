from abc import ABC, abstractmethod

from src.dto.message import Message


class Writer(ABC):
    """
    Standardized abstract base class for the writer interface.
    """

    @abstractmethod
    def __init__(self, folder: str, single_file: bool = True, export_chat: bool = False) -> None:
        self.folder = folder
        self.single_file = single_file
        self.export_chat = export_chat

    @abstractmethod
    def write(self, date: str, messages: list[Message], summary: str) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass