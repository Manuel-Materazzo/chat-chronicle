from abc import ABC, abstractmethod


class Parser(ABC):
    """
    Standardized abstract base class for the parser interface.
    """

    @abstractmethod
    def get_messages_grouped(self) -> dict[str, list[str]]:
        """
        Returns a dictionary where each key is a date and each value is a list of messages.
        :return:
        """

    @abstractmethod
    def get_messages(self, date: str) -> list[str]:
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