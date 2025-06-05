from src.service.writer.writer import Writer


class TxtWriter(Writer):

    def __init__(self, folder: str, single_file: bool = True, export_chat: bool = False) -> None:
        super().__init__(folder, single_file, export_chat)

    def write(self, date: str, chat: str, summary: str) -> None:

        # Compose file path, whether there is an append or a create operation
        if self.single_file:
            file_path = f"{self.folder}/{self.single_file_name}"
        else:
            file_path = f"{self.folder}/{date}_chronicle.txt"

        # Write the daily log
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"[{date}]\n\n")
            f.write(f"Diary Entry: \n{summary}\n\n\n")
            if self.export_chat:
                f.write(f"Chat History: \n{chat}\n\n\n")

