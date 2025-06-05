from src.dto.enums.writer_type import WriterType
from src.service.writer.txt_writer import TxtWriter
from src.service.writer.writer import Writer


def writer_factory(config: dict) -> Writer:
    """
    Instantiates the writer of the right type from the dictionary and returns it.
    :param config: Dictionary containing the configuration of the application.
    :return:
    """
    # get configs
    output_path = config.get('output', {}).get('path', './')
    file_type = config.get('output', {}).get('type', WriterType.TXT)
    single_file = config.get('output', {}).get('merge-to-one-file', True)

    if file_type == WriterType.TXT:
        return TxtWriter(output_path, single_file)

    message = f"Output Writer type not supported, please choose one of the following: {[e for e in WriterType]}"
    raise ValueError(message)
