import re
import json
from collections import defaultdict
from datetime import datetime

from src.dto.instagram_export_message import InstagramExportMessage
from src.dto.message import Message
from src.service.parser.parser import Parser


class InstagramExport(Parser):

    def __init__(self, paths: list[str]):
        self.message_bucket = defaultdict(list[Message])
        # read files and load bucket
        for path in paths:
            raw = self.__read(path)
            self.__bucket_messages(raw)
            del raw
        # sort bucket messages
        for day in list(self.message_bucket.keys()):
            messages = self.message_bucket.get(day)
            sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
            self.message_bucket[day] = sorted_messages

    def get_messages_grouped(self) -> dict[str, list[Message]]:
        return self.message_bucket

    def get_messages(self, date: str) -> list[Message]:
        return self.message_bucket.get(date, [])

    def get_available_days(self) -> list[str]:
        return list(self.message_bucket.keys())

    def get_diary_record(self, date: str) -> str:
        messages = self.get_messages(date)
        diary = ""
        for message in messages:
            timestamp = message.get("timestamp")
            time_string = f"{timestamp.hour:02}:{timestamp.minute:02}"
            diary = diary + f"[{time_string}] {message.get('sender_name')}: {message.get('content')}\n"
        return diary

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
            day_string = timestamp.date().isoformat()
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
