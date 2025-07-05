from abc import ABC, abstractmethod


class Writer(ABC):
    """
    Standardized abstract base class for the writer interface.
    """

    @abstractmethod
    def __init__(self, folder: str, single_file: bool = True, export_intermediate_steps: bool = False) -> None:
        self.folder = folder
        self.single_file = single_file
        self.export_intermediate_steps = export_intermediate_steps

    @abstractmethod
    def write(self, date: str, summary_state: any) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
