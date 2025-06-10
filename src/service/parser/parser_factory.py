from src.dto.enums.input_file_type import InputFileType
from src.service.parser.instagram_export import InstagramExport
from src.service.parser.parser import Parser
from src.service.parser.whatsapp_export import WhatsappExport


def parser_factory(config: dict, paths: list[str]) -> Parser:
    """
    Instantiates the parser for the provided file type from the dictionary and returns it.
    :param config: Dictionary containing the configuration of the application.
    :param paths: List of file paths.
    :return:
    """
    # get configs
    fileType = config.get('batch', {}).get('input', {}).get('type', InputFileType.INSTAGRAM_EXPORT)
    chat_sessions_enabled = config.get('parsing', {}).get('chat-sessions', {}).get('enabled', True)
    sleep_window_start = config.get('parsing', {}).get('chat-sessions', {}).get('sleep-window-start-hour', 2)
    sleep_window_end = config.get('parsing', {}).get('chat-sessions', {}).get('sleep-window-end-hour', 9)
    system_messages = config.get('parsing', {}).get('messages', {})
    ignore_chat_enabled = config.get('parsing', {}).get('ignore-chat', {}).get('enabled', False)
    ignore_chat_before = config.get('parsing', {}).get('ignore-chat', {}).get('ignore-before', "1990-01-01")
    ignore_chat_after = config.get('parsing', {}).get('ignore-chat', {}).get('ignore-after', "2150-01-01")

    if fileType == InputFileType.INSTAGRAM_EXPORT:
        return InstagramExport(paths, system_messages, chat_sessions_enabled, sleep_window_start, sleep_window_end,
                               ignore_chat_enabled, ignore_chat_before, ignore_chat_after)
    elif fileType == InputFileType.WHATSAPP_EXPORT:
        return WhatsappExport(paths, system_messages, chat_sessions_enabled, sleep_window_start, sleep_window_end,
                              ignore_chat_enabled, ignore_chat_before, ignore_chat_after)

    message = f"Input file type not supported, please choose one of the following: {[e for e in InputFileType]}"
    raise ValueError(message)
