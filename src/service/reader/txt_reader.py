from src.service.logging_service import LoggingService
from src.service.reader.reader import Reader


class TxtReader(Reader):

    def __init__(self, logging_service: LoggingService):
        super().__init__(logging_service, ".txt")

    def read(self, path: str) -> list[str]:
        """
        Reads a txt file
        :param path:
        :return:
        """
        with open(path, encoding="utf-8") as f:
            return f.readlines()
