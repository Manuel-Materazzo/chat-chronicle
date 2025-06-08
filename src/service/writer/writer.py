from abc import ABC, abstractmethod


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
    def write(self, date: str, chat: str, summary: str) -> None:
        pass
