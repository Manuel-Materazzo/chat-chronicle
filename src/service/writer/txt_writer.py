from datetime import datetime

from src.service.parser.parser import get_chat_log
from src.service.writer.writer import Writer


class TxtWriter(Writer):

    def __init__(self, folder: str, single_file: bool = True, export_intermediate_steps: bool = False) -> None:
        super().__init__(folder, single_file, export_intermediate_steps)
        self.single_file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_full-chronicle.txt"

    def write(self, date: str, summary_state: any) -> None:

        # Compose file path, whether there is an append or a create operation
        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
        else:
            file_path = f"{self.folder}/{date}_chronicle.txt"

        # Write the daily log
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"[{date}]\n\n")
            f.write(f"Diary Entry: \n{str(summary_state.get('summary', ''))}\n\n\n")
            if self.export_intermediate_steps:
                del summary_state["summary"]
                del summary_state["ai_chat"]
                chat = get_chat_log(summary_state.get('messages', ''))
                f.write(f"Chat History: \n{chat}\n\n\n")
                del summary_state["messages"]
                for element in summary_state:
                    f.write(f"{element}: \n{summary_state[element]}\n\n\n")

    def close(self) -> None:
        pass
