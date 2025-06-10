import os
from abc import ABC, abstractmethod

from src.dto.message import Message
from src.service.logging_service import LoggingService


class Reader(ABC):

    def __init__(self, logging_service: LoggingService, extension: str):
        self.extension = extension
        self.logger = logging_service.get_logger(__name__)

    def get_extension(self):
        return self.extension

    def get_file_list(self, input_directory: bytes):
        """
        Get a list of all useful files in the input directory.
        :param input_directory:
        :return:
        """
        files = []
        for file in os.listdir(input_directory):
            filename = os.fsdecode(file)
            self.logger.debug(f'File or folder found: {filename}')
            if filename.lower().endswith(self.extension):
                self.logger.debug(f'Saving it as: {input_directory}/{filename}')
                files.append(f"{input_directory}/{filename}")

        if len(files) == 0:
            raise FileNotFoundError(f"No {self.extension} files found on {input_directory}")
        else:
            self.logger.info(f'Found {len(files)} files to process...')

        return files

    @abstractmethod
    def read(self, path: str) -> any:
        """
        Reads the provided file
        :return:
        """

    @abstractmethod
    def standardize_messages(self, lines: any) -> list[Message]:
        """
        Standardize the messages format.
        :return:
        """
