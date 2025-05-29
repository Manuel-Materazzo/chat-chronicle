from src.dto.enums.input_file_type import InputFileType
from src.service.parser.instagram_export import InstagramExport
from src.service.parser.parser import Parser


def parser_factory(fileType: InputFileType, path: str) -> Parser:
    """
    Instantiates the parser for the provided file type from the dictionary and returns it.
    :param fileType:
    :param path:
    :return:
    """
    if fileType == InputFileType.INSTAGRAM_EXPORT:
        return InstagramExport(path)

    message = f"Input file type not supported, please choose one of the following: {[e.value for e in InputFileType]}"
    raise ValueError(message)
