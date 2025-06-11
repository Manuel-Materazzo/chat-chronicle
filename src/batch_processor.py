import os

from src.dto.enums.input_file_type import InputFileType
from src.service.ai_service import AiService
from src.service.logging_service import LoggingService
from src.service.parser.parser_factory import parser_factory
from src.service.reader.reader_factory import reader_factory
from src.service.writer.writer_factory import writer_factory


def process_all(config: dict):
    # generate loggers
    logging_service = LoggingService(config)
    logger = logging_service.get_logger(__name__)

    # read configs
    input_file_type = config.get('batch', {}).get('input', {}).get('type', InputFileType.INSTAGRAM_EXPORT)
    input_path = config.get('batch', {}).get('input', {}).get('path', './')
    logger.debug(f'input_path: {input_path}')
    input_directory = os.fsencode(input_path)
    logger.debug(f'Input directory: {input_directory}')

    # instantiate reader
    reader = reader_factory(input_file_type, config)

    # generate files list
    logger.debug(f'Listing files with {reader.get_extension()} extension...')
    files = reader.get_file_list(input_directory)

    # initialize parser
    logger.debug('Initializing parser...')
    parser = parser_factory(input_file_type, config)

    # read and parse files
    for file in files:
        logger.debug(f'Reading {file}...')
        raw_messages = reader.read(file)
        logger.debug(f'Standardizing {file}...')
        standardized_messages = reader.standardize_messages(raw_messages)
        logger.debug(f'Parsing {file}...')
        parser.parse(standardized_messages)

    # sort bucket
    logger.debug('Sorting parser bucket...')
    parser.sort_bucket()

    day_list = parser.get_available_days()
    logger.info(f'Found {len(day_list)} days of messages...')

    # instantiate writer
    writer = writer_factory(config)

    # create AI service
    ai_service = AiService(config)

    done_count = 1

    # get summary and write each day diary
    for day in day_list:
        # get chat log
        logger.debug(f'Getting chat log for {day}...')
        chat_log = parser.get_chat_log(day)
        # compute summary
        logger.debug(f'Generating summary for {day}...')
        summary = ai_service.get_summary_sync(chat_log)
        # write to file
        logger.debug(f'Writing file for {day}...')
        writer.write(day, chat_log, summary)

        logger.info(f'{done_count}/{len(day_list)} done!')
        done_count = done_count + 1

    writer.close()
