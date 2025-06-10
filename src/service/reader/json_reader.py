import json

from src.service.logging_service import LoggingService
from src.service.reader.reader import Reader


class JsonReader(Reader):

    def __init__(self, logging_service: LoggingService):
        super().__init__(logging_service, ".json")

    def read(self, path: str) -> list[dict]:
        """
        Reads a json file
        :param path:
        :return:
        """
        with open(path) as f:
            return json.load(f)
