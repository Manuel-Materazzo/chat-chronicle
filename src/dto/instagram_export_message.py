from typing import TypedDict


class InstagramExportMessage(TypedDict):
    sender_name: str
    timestamp_ms: int
    content: str
    call_duration: int
    reactions: list
    share: dict
    videos: list
    audio_files: list
    photos: list
    is_geoblocked_for_viewer: bool
    is_unsent_image_by_messenger_kid_parent: bool
