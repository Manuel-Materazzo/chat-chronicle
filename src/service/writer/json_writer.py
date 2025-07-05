import json
from datetime import datetime

from src.service.writer.writer import Writer


class JsonWriter(Writer):

    def __init__(self, folder: str, single_file: bool = True, export_intermediate_steps: bool = False) -> None:
        super().__init__(folder, single_file, export_intermediate_steps)
        self.single_file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_full-chronicle.json"
        self.first_line = True

        # write first line: the json array open
        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("[\n")

    def write(self, date: str, summary_state: any) -> None:
        entry = {
            "date": date,
            "summary": str(summary_state.get('summary', '')),
        }
        if self.export_intermediate_steps:
            del summary_state["summary"]
            del summary_state["ai_chat"]
            entry["intermediate_steps"] = summary_state

        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
        else:
            file_path = f"{self.folder}/{date}_chronicle.json"

        with open(file_path, "a", encoding="utf-8") as f:
            if self.first_line:
                f.write(json.dumps(entry, ensure_ascii=False, default=str))
                self.first_line = False
                return
            f.write(",\n" + json.dumps(entry, ensure_ascii=False, default=str))

    def close(self) -> None:
        # write last line: the json array close
        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("\n]")
