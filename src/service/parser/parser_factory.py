from src.dto.enums.input_file_type import InputFileType
from src.service.parser.instagram_export import InstagramExport
from src.service.parser.parser import Parser


def parser_factory(config: dict, paths: list[str]) -> Parser:
    """
    Instantiates the parser for the provided file type from the dictionary and returns it.
    :param config: Dictionary containing the configuration of the application.
    :param paths: List of file paths.
    :return:
    """
    # get configs
    fileType = config.get('input', {}).get('file-type', InputFileType.INSTAGRAM_EXPORT)
    chat_sessions_enabled = config.get('parsing', {}).get('chat-sessions', {}).get('enabled', True)
    sleep_window_start = config.get('parsing', {}).get('chat-sessions', {}).get('sleep-window-start-hour', 2)
    sleep_window_end = config.get('parsing', {}).get('chat-sessions', {}).get('sleep-window-end-hour', 9)

    if fileType == InputFileType.INSTAGRAM_EXPORT:
        return InstagramExport(paths, chat_sessions_enabled, sleep_window_start, sleep_window_end)

    message = f"Input file type not supported, please choose one of the following: {[e for e in InputFileType]}"
    raise ValueError(message)
