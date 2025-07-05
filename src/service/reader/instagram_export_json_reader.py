from datetime import datetime

from src.dto.instagram_export_message import InstagramExportMessage
from src.dto.message import Message
from src.service.logging_service import LoggingService
from src.service.reader.json_reader import JsonReader
from langchain_core.messages.utils import count_tokens_approximately


class InstagramExportJsonReader(JsonReader):

    def __init__(self, system_messages: dict, logging_service: LoggingService, chars_per_token: float = 4.0):
        super().__init__(logging_service, chars_per_token=chars_per_token)
        # get messages from configs
        self.message_like = system_messages.get("user-interactions", {}).get("message-like", "")
        self.message_reaction = system_messages.get("user-interactions", {}).get("message-reaction", "Added reaction")
        self.call_started_message = system_messages.get("user-interactions", {}).get("call-start", "Started a call")
        self.message_reel = system_messages.get("user-content", {}).get("posts-and-reels", "[Shared an internet video]")
        self.message_video = system_messages.get("user-content", {}).get("video-uploads", "[Sent a video of himself]")
        self.message_photo = system_messages.get("user-content", {}).get("photo-uploads", "[Sent a photo of himself]")
        self.message_audio = system_messages.get("user-content", {}).get("audio-messages", "[Sent an audio message]")
        self.call_start = system_messages.get("user-content", {}).get("call-start", "[Call started]")
        self.call_end = system_messages.get("user-content", {}).get("call-end", "[Call ended]")

    def standardize_messages(self, lines: dict) -> list[Message]:
        messages: list[Message] = []

        for raw_message in lines.get("messages", []):
            # compute timestamp
            timestamp = datetime.fromtimestamp(raw_message.get("timestamp_ms", 1000) / 1000.0)

            content = self.__get_message_content(raw_message)
            sender = raw_message.get("sender_name", "unknown")
            token_count = count_tokens_approximately([sender, content], chars_per_token=self.chars_per_token)
            messages.append({
                'sender_name': sender,
                'timestamp': timestamp,
                'content': content,
                'token_count': token_count
            })

        return messages

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
        # handle calls
        if raw_message.get("call_duration", None) is not None:
            return self.call_end
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

        # handle call start
        if content == self.call_started_message:
            return self.call_start

        # handle message likes and reactions
        if content == self.message_like or self.message_reaction in content:
            return ""

        return content
