import re
import json
from datetime import datetime

from src.dto.instagram_export_message import InstagramExportMessage
from src.service.parser.parser import Parser


class InstagramExport(Parser):

    def __init__(self, paths: list[str], system_messages: dict, chat_sessions_enabled: bool = False,
                 sleep_window_start: int = 2, sleep_window_end: int = 9, ignore_chat_enabled: bool = False,
                 ignore_chat_before: str = "2150-01-01", ignore_chat_after: str = "1990-01-01"):
        super().__init__(paths, system_messages, chat_sessions_enabled, sleep_window_start, sleep_window_end,
                         ignore_chat_enabled, ignore_chat_before, ignore_chat_after)

        # read files and load bucket
        for path in paths:
            raw = self.__read(path)
            self.__bucket_messages(raw)
            del raw

        self.sort_bucket()

    def __read(self, path: str) -> list[InstagramExportMessage]:
        """
        Reads instagram exported json
        :param path:
        :return:
        """
        with open(path) as f:
            data = json.load(f)
        messages = data["messages"]
        return messages

    def __bucket_messages(self, raw_messages: list[InstagramExportMessage]):
        """
        Parses messages, and groups them into a daily bucket
        :param raw_messages:
        :return:
        """
        for raw_message in raw_messages:
            # compute timestamp
            timestamp = datetime.fromtimestamp(raw_message.get("timestamp_ms") / 1000.0)

            day = timestamp.date()

            # ignore message if before or after set date
            if self.ignore_chat_enabled:
                if day < self.ignore_chat_before_date or day > self.ignore_chat_after_date:
                    continue

            day_string = day.isoformat()

            # fix semantics
            content = self.__get_message_content(raw_message)
            if len(content) == 0:
                continue
            sender = self.__remove_unicodes(raw_message.get("sender_name", "unknown"))
            # save message into bucket
            self.message_bucket[day_string].append({
                'sender_name': sender,
                'timestamp': timestamp,
                'content': content,
            })

    def __get_message_content(self, raw_message: InstagramExportMessage) -> str:
        """
        Gets a content for
        TODO: add reference for reactions?
        TODO: transcribe audio files?
        TODO: handle message editing
        :param raw_message:
        :return:
        """

        # handle reels
        if raw_message.get("share", None) is not None:
            return self.message_reel
        # handle videos
        if raw_message.get("videos", None) is not None:
            return self.message_video
        # handle photos
        if raw_message.get("photos", None) is not None:
            return self.message_photo
        # handle audios TODO: transcribe?
        if raw_message.get("audio_files", None) is not None:
            return self.message_audio

        content = raw_message.get("content", "")

        # handle message likes and reactions
        if content == self.message_like or self.message_reaction in content:
            return ""

        content = self.handle_newlines(content)
        return self.__fix_unicodes(content)

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
