from src.dto.enums.input_file_type import InputFileType
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
    chat_sessions_enabled = config.get('parsing', {}).get('chat-sessions', {}).get('enabled', True)
    sleep_window_start = config.get('parsing', {}).get('chat-sessions', {}).get('sleep-window-start-hour', 2)
    sleep_window_end = config.get('parsing', {}).get('chat-sessions', {}).get('sleep-window-end-hour', 9)
    ignore_chat_enabled = config.get('parsing', {}).get('ignore-chat', {}).get('enabled', False)
    ignore_chat_before = config.get('parsing', {}).get('ignore-chat', {}).get('ignore-before', "1990-01-01")
    ignore_chat_after = config.get('parsing', {}).get('ignore-chat', {}).get('ignore-after', "2150-01-01")
    token_per_chunk = config.get('parsing', {}).get('token-per-chunk', 4000)

    if fileType == InputFileType.INSTAGRAM_EXPORT:
        return InstagramExport(chat_sessions_enabled, sleep_window_start, sleep_window_end, ignore_chat_enabled,
                               ignore_chat_before, ignore_chat_after, token_per_chunk)
    elif fileType == InputFileType.WHATSAPP_EXPORT:
        return WhatsappExport(chat_sessions_enabled, sleep_window_start, sleep_window_end, ignore_chat_enabled,
                              ignore_chat_before, ignore_chat_after, token_per_chunk)

    message = f"Input file type not supported, please choose one of the following: {[e for e in InputFileType]}"
    raise ValueError(message)
