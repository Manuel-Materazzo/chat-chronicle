from src.service.writer.writer import Writer


class TxtWriter(Writer):

    def __init__(self, folder: str) -> None:
        super().__init__(folder)

    def write(self, date: str, chat: str, summary: str) -> None:

        # TODO: handle missing trailing slash
        file_path = f"{self.folder}/{date}.txt"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"[{date}]\n\n")
            f.write(f"Diary Entry: \n{summary}\n\n\n")
            f.write(f"Chat History: \n{chat}\n")

