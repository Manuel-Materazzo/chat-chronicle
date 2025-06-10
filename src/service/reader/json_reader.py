import json

from abc import ABC
from src.service.logging_service import LoggingService
from src.service.reader.reader import Reader


class JsonReader(Reader, ABC):

    def __init__(self, logging_service: LoggingService):
        super().__init__(logging_service, ".json")

    def read(self, path: str) -> dict:
        """
        Reads a json file
        :param path:
        :return:
        """
        with open(path) as f:
            return json.load(f)
