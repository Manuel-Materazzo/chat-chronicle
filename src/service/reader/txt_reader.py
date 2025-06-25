from src.service.logging_service import LoggingService
from src.service.reader.reader import Reader
from abc import ABC


class TxtReader(Reader, ABC):

    def __init__(self, logging_service: LoggingService, chars_per_token: float = 4.0):
        super().__init__(logging_service, ".txt", chars_per_token=chars_per_token)

    def read(self, path: str) -> list[str]:
        """
        Reads a txt file
        :param path:
        :return:
        """
        with open(path, encoding="utf-8") as f:
            return f.readlines()
