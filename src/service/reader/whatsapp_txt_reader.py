import re
from datetime import datetime

from src.dto.message import Message
from src.service.logging_service import LoggingService
from src.service.reader.txt_reader import TxtReader
from langchain_core.messages.utils import count_tokens_approximately


class WhatsappTxtReader(TxtReader):

    def __init__(self, logging_service: LoggingService, chars_per_token: float = 4.0):
        super().__init__(logging_service, chars_per_token=chars_per_token)
        self.message_regex = re.compile(
            r'^(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - ([^:]+): (.*)', re.DOTALL
        )

    def standardize_messages(self, lines: list[str]) -> list[Message]:
        messages: list[Message] = []

        timestamp: datetime = None
        sender: str = ""
        current_content: str = ""

        for line in lines:
            match = self.message_regex.match(line)

            if match:
                # when there is a match, push the previous line (if any, the first line won't have a prev line)
                if current_content:
                    token_count = count_tokens_approximately(current_content, chars_per_token=self.chars_per_token)
                    messages.append({
                        'sender_name': sender,
                        'timestamp': timestamp,
                        'content': current_content.strip(),
                        'token_count': token_count
                    })
                # save sender, timestamp and message for the current line
                date_str, time_str, sender, content = match.groups()
                timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                current_content = content.strip()

            else:
                # if no match, we are still on the previous line, add the content
                current_content += "\n" + line.strip()

        # push the last leftover line
        if current_content:
            token_count = count_tokens_approximately(current_content, chars_per_token=self.chars_per_token)
            messages.append({
                'sender_name': sender,
                'timestamp': timestamp,
                'content': current_content.strip(),
                'token_count': token_count
            })

        return messages
