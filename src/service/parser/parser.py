from abc import ABC, abstractmethod
from collections import defaultdict

from src.dto.message import Message


class Parser(ABC):
    """
    Standardized abstract base class for the parser interface.
    """

    @abstractmethod
    def __init__(self, paths: list[str]):
        self.message_bucket = defaultdict(list[Message])

    def sort_bucket(self):
        """
        Sorts the message bucket.
        :return:
        """
        for day in self.get_available_days():
            messages = self.message_bucket.get(day)
            sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
            self.message_bucket[day] = sorted_messages
            # TODO: move messages back a day if they are from the previous session

    @abstractmethod
    def get_messages_grouped(self) -> dict[str, list[Message]]:
        """
        Returns a dictionary where each key is a date and each value is a list of messages.
        :return:
        """

    @abstractmethod
    def get_messages(self, date: str) -> list[Message]:
        """
        Returns list of messages sent on the provided date.
        :param date:
        :return:
        """

    @abstractmethod
    def get_available_days(self) -> list[str]:
        """
        Returns a list of days with messages available.
        :return:
        """

    @abstractmethod
    def get_diary_record(self, date: str) -> str:
        """
        Returns a list of days with messages available.
        :return:
        """