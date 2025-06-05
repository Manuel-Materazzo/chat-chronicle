from abc import ABC, abstractmethod
from datetime import datetime


class Writer(ABC):
    """
    Standardized abstract base class for the writer interface.
    """

    @abstractmethod
    def __init__(self, folder: str, single_file: bool = True) -> None:
        self.folder = folder
        self.single_file = single_file
        self.single_file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-')}_full-chronicle.txt"

    @abstractmethod
    def write(self, date: str, chat: str, summary: str) -> None:
        pass
