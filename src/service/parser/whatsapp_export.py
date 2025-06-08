import re
from datetime import datetime

from src.service.parser.parser import Parser


class WhatsappExport(Parser):

    def __init__(self, paths: list[str], system_messages: dict, chat_sessions_enabled: bool = False,
                 sleep_window_start: int = 2, sleep_window_end: int = 9, ignore_chat_enabled: bool = False,
                 ignore_chat_before: str = "2150-01-01", ignore_chat_after: str = "1990-01-01"):
        super().__init__(paths, system_messages, chat_sessions_enabled, sleep_window_start, sleep_window_end,
                         ignore_chat_enabled, ignore_chat_before, ignore_chat_after)
        # compile regexp for semantic extraction
        self.message_regex = re.compile(
            r'^(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - ([^:]+): (.*)', re.DOTALL
        )

        # read files and load bucket
        for path in paths:
            raw = self.__read(path)
            self.__bucket_messages(raw)
            del raw

        self.sort_bucket()

    def __read(self, path: str) -> list[str]:
        """
        Reads whatsapp exported json
        :param path:
        :return:
        """
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        messages = []
        current_message = ""

        # WhatsApp message regex: e.g., "07/06/2025, 13:21 - Name: ..."
        pattern = re.compile(r'^\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - ')

        for line in lines:
            if pattern.match(line):
                if current_message:
                    messages.append(current_message.strip())
                current_message = line.strip()
            else:
                current_message += "\n" + line.strip()

        if current_message:
            messages.append(current_message.strip())

        return messages

    def __bucket_messages(self, raw_messages: list[str]):
        """
        Parses messages, and groups them into a daily bucket
        :param raw_messages:
        :return:
        """
        for raw_message in raw_messages:
            # compute timestamp

            match = self.message_regex.match(raw_message)

            if not match:
                continue

            date_str, time_str, sender, content = match.groups()
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")

            day = timestamp.date()

            # ignore message if before or after set date
            if self.ignore_chat_enabled:
                if day < self.ignore_chat_before_date or day > self.ignore_chat_after_date:
                    continue

            day_string = day.isoformat()

            # fix semantics
            content = self.handle_newlines(content.strip())
            if len(content) == 0:
                continue
            # save message into bucket
            self.message_bucket[day_string].append({
                'sender_name': sender,
                'timestamp': timestamp,
                'content': content,
            })

