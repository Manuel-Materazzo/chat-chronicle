import re
import json
from collections import defaultdict
from datetime import datetime

from src.dto.instagram_export_message import InstagramExportMessage


class InstagramExport:

    def __init__(self, path: str):
        raw = self.__read(path)
        self.message_bucket = self.__parse_and_group(raw)
        del raw

    def get_messages_grouped(self) -> dict[str, list[str]]:
        return self.message_bucket

    def get_messages(self, date: str) -> list[str]:
        return self.message_bucket.get(date, [])

    def get_available_days(self) -> list[str]:
        return list(self.message_bucket.keys())

    def get_diary_record(self, date: str):
        messages = self.get_messages(date)
        return "\n".join(messages)

    def __read(self, path: str) -> list[InstagramExportMessage]:
        """
        Reads instagram exported json
        :param path:
        :return:
        """
        with open(path) as f:
            data = json.load(f)
        messages = data["messages"]
        messages.reverse()
        return messages

    def __parse_and_group(self, raw_messages: list[InstagramExportMessage]) -> dict[str, list[str]]:
        """
        Parses messages, and groups them into a daily bucket
        :param raw_messages:
        :return:
        """
        bucket = defaultdict(list[str])
        for raw_message in raw_messages:
            # compute timestamp
            timestamp = datetime.fromtimestamp(raw_message.get("timestamp_ms") / 1000.0)
            day_string = timestamp.date().isoformat()
            time_string = f"{timestamp.hour}:{timestamp.minute}"
            # fix semantics
            content = self.__get_message_content(raw_message)
            if len(content) == 0:
                continue
            sender = self.__remove_unicodes(raw_message.get("sender_name", "unknown"))
            # save message into bucket
            message = f"[{time_string}] {sender}: {content}"
            bucket[day_string].append(message)

        return bucket

    def __get_message_content(self, raw_message: InstagramExportMessage) -> str:
        """
        Gets a content for
        TODO: add reference for reactions?
        TODO: transcribe audio files?
        TODO: handle message editing
        :param raw_message:
        :return:
        """

        #TODO: localize

        # handle reels
        if raw_message.get("share", None) is not None:
            return "[Shared an internet video]"
        # handle videos
        if raw_message.get("share", None) is not None:
            return "[Shared an internet video]"
        # handle audios TODO: transcribe?
        if raw_message.get("audio_files", None) is not None:
            return "[Sent an audio message]"
        # handle photos
        if raw_message.get("photos", None) is not None:
            return "[Sent a photo of himself]"

        content = raw_message.get("content", "");

        # handle message likes
        # TODO: localize
        if content == "Ha messo \"Mi piace\" a un messaggio" or "Ha aggiunto la reazione" in content:
            return ""

        #TODO: handle newlines on messages
        return self.__fix_unicodes(raw_message.get("content", ""))

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
