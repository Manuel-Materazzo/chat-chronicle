import json

from abc import ABC
from src.service.logging_service import LoggingService
from src.service.reader.reader import Reader


class JsonReader(Reader, ABC):

    def __init__(self, logging_service: LoggingService, chars_per_token: float = 4.0):
        super().__init__(logging_service, ".json", chars_per_token=chars_per_token)

    def read(self, path: str) -> dict:
        """
        Reads a json file
        :param path:
        :return:
        """
        with open(path) as f:
            return json.load(f)
