import re
from src.dto.message import Message
from src.service.parser.parser import Parser


class InstagramExport(Parser):

    def __init__(self, chat_sessions_enabled: bool = False, sleep_window_start: int = 2, sleep_window_end: int = 9,
                 ignore_chat_enabled: bool = False, ignore_chat_before: str = "2150-01-01",
                 ignore_chat_after: str = "1990-01-01", token_per_chunk: int = 4000):
        super().__init__(chat_sessions_enabled, sleep_window_start, sleep_window_end,
                         ignore_chat_enabled, ignore_chat_before, ignore_chat_after, token_per_chunk)

    def parse(self, messages: list[Message]) -> None:
        for message in messages:
            day = message.get("timestamp").date()
            # ignore message if before or after set date
            if self.ignore_chat_enabled:
                if day < self.ignore_chat_before_date or day > self.ignore_chat_after_date:
                    continue

            day_string = day.isoformat()

            # fix semantics
            content = self.__fix_unicodes(message.get("content", ""))
            content = self.handle_newlines(content)
            if len(content) == 0:
                continue
            sender = self.__remove_unicodes(message.get("sender_name", "unknown"))

            # save message into bucket
            message["content"] = content
            message["sender_name"] = sender
            self.message_bucket[day_string].append(message)

    def __fix_unicodes(self, text: str) -> str:
        """
        Fixes double encoded instagram messages
        :param text:
        :return:
        """
        return text.encode('latin1').decode('utf8')

    def __remove_unicodes(self, text: str) -> str:
        """
        Removes double encoded unicodes from a text
        :param text:
        :return:
        """

        return re.sub(r'[^\x00-\x7F]+', '', text)
