from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import timedelta, time

from src.dto.message import Message


class Parser(ABC):
    """
    Standardized abstract base class for the parser interface.
    """

    @abstractmethod
    def __init__(self, paths: list[str], system_messages: dict, chat_sessions_enabled: bool = False, sleep_window_start: int = 2,
                 sleep_window_end: int = 9) -> None:
        self.message_bucket = defaultdict(list[Message])
        self.gap_threshold = timedelta(hours=3)
        self.chat_sessions_enabled = chat_sessions_enabled
        self.sleep_window_start = time(sleep_window_start, 0)
        self.sleep_window_end = time(sleep_window_end, 0)

        # get messages from configs
        self.message_like = system_messages.get("user-interactions", {}).get("message-like", "")
        self.message_reaction = system_messages.get("user-interactions", {}).get("message-reaction", "Added reaction")
        self.message_reel = system_messages.get("user-content", {}).get("posts-and-reels", "[Shared an internet video]")
        self.message_video = system_messages.get("user-content", {}).get("video-uploads", "[Sent a video of himself]")
        self.message_photo = system_messages.get("user-content", {}).get("photo-uploads", "[Sent a photo of himself]")
        self.message_audio = system_messages.get("user-content", {}).get("audio-messages", "[Sent an audio message]")

    def sort_bucket(self):
        """
        Sorts the message bucket.
        :return:
        """
        for day in self.get_available_days():
            messages = self.message_bucket.get(day)
            sorted_messages = sorted(messages, key=lambda x: x['timestamp'])

            # usually conversations don't end precisely at midnight, we need to end the day when there is a "sleep" gap.
            # we will detect that gap in a plausible sleep window, and carry the messages back to the prev day.
            if self.chat_sessions_enabled:
                sorted_messages = self.extract_chat_sessions(sorted_messages)

            self.message_bucket[day] = sorted_messages

    def extract_chat_sessions(self, sorted_messages) -> list[dict[str, str]]:
        """
        Extracts the chat sessions and puts them in the previous day.
        :param sorted_messages:
        :return:
        """
        prev_timestamp = sorted_messages[0]['timestamp']
        previous_day_carry_over = []
        for i, msg in enumerate(sorted_messages):

            timestamp_time = msg['timestamp'].time()

            # if message is after sleep window end (09:00), there is no carry over
            if timestamp_time > self.sleep_window_end:
                break

            # if the message is between sleep window start (02:00) and end (09:00)
            if self.sleep_window_start <= msg['timestamp'].time():
                gap = msg['timestamp'] - prev_timestamp
                # and has a significant gap from the previous message
                if gap > self.gap_threshold:
                    # remove messages from today's list, and add them to yesterday's carryover list
                    previous_day_carry_over = sorted_messages[:i]
                    sorted_messages = sorted_messages[i:]
                    break
            # update last timestamp
            prev_timestamp = msg['timestamp']

        # add carryover to the previous day
        prev_day = prev_timestamp - timedelta(days=1)
        prev_day_string = prev_day.date().isoformat()
        self.message_bucket[prev_day_string].extend(previous_day_carry_over)

        return sorted_messages

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
    def get_chat_log(self, date: str) -> str:
        """
        Returns a list of days with messages available.
        :return:
        """
