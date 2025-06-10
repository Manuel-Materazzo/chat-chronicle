from src.dto.enums.input_file_type import InputFileType
from src.service.logging_service import LoggingService
from src.service.reader.instagram_export_json_reader import InstagramExportJsonReader
from src.service.reader.reader import Reader
from src.service.reader.whatsapp_txt_reader import WhatsappTxtReader


def reader_factory(config: dict) -> Reader:
    """
    Returns the correct reader for the file type.
    :param config:
    :return:
    """
    # get configs
    fileType = config.get('batch', {}).get('input', {}).get('type', InputFileType.INSTAGRAM_EXPORT)
    system_messages = config.get('parsing', {}).get('messages', {})
    logging_service = LoggingService(config)

    if fileType == InputFileType.INSTAGRAM_EXPORT:
        return InstagramExportJsonReader(system_messages, logging_service)
    elif fileType == InputFileType.WHATSAPP_EXPORT:
        return WhatsappTxtReader(logging_service)
