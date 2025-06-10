from src.dto.enums.writer_type import WriterType
from src.service.writer.json_writer import JsonWriter
from src.service.writer.ndjson_writer import NdJsonWriter
from src.service.writer.txt_writer import TxtWriter
from src.service.writer.writer import Writer


def writer_factory(config: dict) -> Writer:
    """
    Instantiates the writer of the right type from the dictionary and returns it.
    :param config: Dictionary containing the configuration of the application.
    :return:
    """
    # get configs
    output_path = config.get('batch', {}).get('output', {}).get('path', './')
    file_type = config.get('batch', {}).get('output', {}).get('type', WriterType.TXT)
    single_file = config.get('batch', {}).get('output', {}).get('merge-to-one-file', True)
    export_chat = config.get('batch', {}).get('output', {}).get('export-chat-log', False)

    if file_type == WriterType.TXT:
        return TxtWriter(output_path, single_file, export_chat)
    elif file_type == WriterType.NDJSON:
        return NdJsonWriter(output_path, single_file, export_chat)
    elif file_type == WriterType.JSON:
        return JsonWriter(output_path, single_file, export_chat)

    message = f"Output Writer type not supported, please choose one of the following: {[e for e in WriterType]}"
    raise ValueError(message)
