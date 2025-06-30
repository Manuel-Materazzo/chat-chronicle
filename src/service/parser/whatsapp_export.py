from src.dto.message import Message
from src.service.parser.parser import Parser


class WhatsappExport(Parser):

    def __init__(self, chat_sessions_enabled: bool = False, sleep_window_start: int = 2, sleep_window_end: int = 9,
                 ignore_chat_enabled: bool = False, ignore_chat_before: str = "2150-01-01",
                 ignore_chat_after: str = "1990-01-01"):
        super().__init__(chat_sessions_enabled, sleep_window_start, sleep_window_end,
                         ignore_chat_enabled, ignore_chat_before, ignore_chat_after)

    def parse(self, messages: list[Message]) -> None:
        for message in messages:
            day = message.get("timestamp").date()
            # ignore message if before or after set date
            if self.ignore_chat_enabled:
                if day < self.ignore_chat_before_date or day > self.ignore_chat_after_date:
                    continue

            day_string = day.isoformat()

            # fix semantics
            content = self.handle_newlines(message.get("content", ""))
            if len(content) == 0:
                continue

            # save message into bucket
            message["content"] = content
            self.message_bucket[day_string].append(message)
