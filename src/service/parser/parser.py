from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import timedelta, time, datetime

from src.dto.chunk import Chunk
from src.dto.message import Message


def get_chat_log(messages: list[Message]) -> str:
    """
    Returns a chat log for the provided message list, each message is formatted as follows: [HH:mm] name: message.
    :return:
    """
    diary = ""
    for message in messages:
        timestamp = message.get("timestamp")
        time_string = f"{timestamp.hour:02}:{timestamp.minute:02}"
        diary = diary + f"[{time_string}] {message.get('sender_name')}: {message.get('content')}\n"
    return diary


def get_daily_chat_log_chunked(messages: list[Message], token_per_chunk: int) -> list[Chunk]:
    """
    Returns a chat log for the provided messages list, divided into slightly overlapping chunks.
    Each message is formatted as follows: [HH:mm] name: message.
    :return:
    """
    diary: list[Chunk] = []
    chunk = Chunk(content="", messages_count=0, start_timestamp=None, end_timestamp=None, token_count=0)
    content = []

    for message in messages:
        # prepare message
        timestamp = message.get("timestamp")
        time_string = f"{timestamp.hour:02}:{timestamp.minute:02}"
        formatted_message = f"[{time_string}] {message.get('sender_name')}: {message.get('content')}\n"
        content.append(formatted_message)

        # counts
        tokens = message.get("token_count")
        chunk["token_count"] += tokens
        chunk["messages_count"] += 1

        # start time for the chunk
        if chunk["start_timestamp"] is None:
            chunk["start_timestamp"] = timestamp

        # when reaching the soft token limit (with a min of 3 messages, to allow extra-long ones)
        if chunk["messages_count"] > 6 and chunk["token_count"] > token_per_chunk:
            # append the chunk and start a new one
            chunk["content"] = "".join(content)
            chunk["end_timestamp"] = timestamp
            diary.append(chunk)

            chunk = Chunk(content="", messages_count=0, start_timestamp=None, end_timestamp=None, token_count=0)
            content = content[-3:]  # overlapping chunks content, more context for the AI

    return diary


class Parser(ABC):
    """
    Standardized abstract base class for the parser interface.
    """

    @abstractmethod
    def __init__(self, chat_sessions_enabled: bool = False, sleep_window_start: int = 2, sleep_window_end: int = 9,
                 ignore_chat_enabled: bool = False, ignore_chat_before: str = "2150-01-01",
                 ignore_chat_after: str = "1990-01-01") -> None:
        self.message_bucket = defaultdict(list[Message])
        self.gap_threshold = timedelta(hours=3)

        self.chat_sessions_enabled = chat_sessions_enabled
        self.sleep_window_start = time(sleep_window_start, 0)
        self.sleep_window_end = time(sleep_window_end, 0)

        self.ignore_chat_enabled = ignore_chat_enabled
        if ignore_chat_enabled and len(ignore_chat_before) > 0 and len(ignore_chat_after) > 0:
            # parse dates
            self.ignore_chat_before_date = datetime.strptime(ignore_chat_before, '%Y-%m-%d').date()
            self.ignore_chat_after_date = datetime.strptime(ignore_chat_after, '%Y-%m-%d').date()

    @abstractmethod
    def parse(self, messages: list[Message]) -> None:
        """
            Parse the messages given and add them to the message bucket.
        """

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

    def handle_newlines(self, text: str) -> str:
        """
        Handles newlines on messages to reduce AI confusion.
        :param text:
        :return:
        """
        # replace newlines keeping punctuation semantics
        for p in [":", ";", ",", "."]:
            text = text.replace(f"{p}\n", f"{p} ")
        return text.replace("\n", ". ")

    def extract_chat_sessions(self, sorted_messages) -> list[dict[str, str]]:
        """
        Extracts the chat sessions and puts them in the previous day.
        :param sorted_messages:
        :return:
        """
        if len(sorted_messages) == 0:
            return []
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
        if len(previous_day_carry_over) > 0:
            prev_day = prev_timestamp - timedelta(days=1)
            prev_day_string = prev_day.date().isoformat()
            self.message_bucket[prev_day_string].extend(previous_day_carry_over)

        return sorted_messages

    def get_messages_grouped(self) -> dict[str, list[Message]]:
        """
        Returns a dictionary where each key is a date and each value is a list of messages.
        :return:
        """
        return self.message_bucket

    def get_messages(self, date: str) -> list[Message]:
        """
        Returns list of messages sent on the provided date.
        :param date:
        :return:
        """
        return self.message_bucket.get(date, [])

    def get_available_days(self) -> list[str]:
        """
        Returns a list of days with messages available.
        :return:
        """
        return list(self.message_bucket.keys())
