from abc import ABC, abstractmethod


class Writer(ABC):
    """
    Standardized abstract base class for the writer interface.
    """

    @abstractmethod
    def __init__(self, folder: str) -> None:
        self.folder = folder

    @abstractmethod
    def write(self, date: str, chat: str, summary: str) -> None:
        pass
