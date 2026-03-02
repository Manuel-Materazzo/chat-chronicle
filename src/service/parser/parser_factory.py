from src.dto.enums.input_file_type import InputFileType
from src.service.config_service import get_nested
from src.service.parser.instagram_export import InstagramExport
from src.service.parser.parser import Parser
from src.service.parser.whatsapp_export import WhatsappExport


def parser_factory(fileType: InputFileType, config: dict) -> Parser:
    """
    Instantiates the parser for the provided file type from the dictionary and returns it.
    :param fileType:
    :param config: Dictionary containing the configuration of the application.
    :return:
    """
    # get configs
    chat_sessions_enabled = get_nested(config, 'parsing.chat-sessions.enabled', True)
    sleep_window_start = get_nested(config, 'parsing.chat-sessions.sleep-window-start-hour', 2)
    sleep_window_end = get_nested(config, 'parsing.chat-sessions.sleep-window-end-hour', 9)
    ignore_chat_enabled = get_nested(config, 'parsing.ignore-chat.enabled', False)
    ignore_chat_before = get_nested(config, 'parsing.ignore-chat.ignore-before', "1990-01-01")
    ignore_chat_after = get_nested(config, 'parsing.ignore-chat.ignore-after', "2150-01-01")

    if fileType == InputFileType.INSTAGRAM_EXPORT:
        return InstagramExport(chat_sessions_enabled, sleep_window_start, sleep_window_end, ignore_chat_enabled,
                               ignore_chat_before, ignore_chat_after)
    elif fileType == InputFileType.WHATSAPP_EXPORT:
        return WhatsappExport(chat_sessions_enabled, sleep_window_start, sleep_window_end, ignore_chat_enabled,
                              ignore_chat_before, ignore_chat_after)

    message = f"Input file type not supported, please choose one of the following: {[e for e in InputFileType]}"
    raise ValueError(message)
