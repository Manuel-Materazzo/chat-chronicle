import json
from datetime import datetime

from src.dto.message import Message
from src.service.parser.parser import get_chat_log
from src.service.writer.writer import Writer


class JsonWriter(Writer):

    def __init__(self, folder: str, single_file: bool = True, export_chat: bool = False) -> None:
        super().__init__(folder, single_file, export_chat)
        self.single_file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_full-chronicle.json"
        self.first_line = True

        # write first line: the json array open
        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("[\n")

    def write(self, date: str, messages: list[Message], summary: str) -> None:
        entry = {
            "date": date,
            "summary": str(summary),
        }
        if self.export_chat:
            chat = get_chat_log(messages)
            entry["chat"] = chat

        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
        else:
            file_path = f"{self.folder}/{date}_chronicle.json"

        with open(file_path, "a", encoding="utf-8") as f:
            if self.first_line:
                f.write(json.dumps(entry, ensure_ascii=False))
                self.first_line = False
            f.write(",\n" + json.dumps(entry, ensure_ascii=False))

    def close(self) -> None:
        # write last line: the json array close
        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("\n]")
