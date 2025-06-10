import re
from datetime import datetime

from src.dto.message import Message
from src.service.logging_service import LoggingService
from src.service.reader.txt_reader import TxtReader


class WhatsappTxtReader(TxtReader):

    def __init__(self, logging_service: LoggingService):
        super().__init__(logging_service)
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
                    messages.append({
                        'sender_name': sender,
                        'timestamp': timestamp,
                        'content': current_content.strip()
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
            messages.append({
                'sender_name': sender,
                'timestamp': timestamp,
                'content': current_content.strip()
            })

        return messages
