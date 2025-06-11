import asyncio
import os

from src.dto.enums.input_file_type import InputFileType
from src.service.ai_service import AiService
from src.service.logging_service import LoggingService
from src.service.parser.parser_factory import parser_factory
from src.service.reader.reader_factory import reader_factory
from src.service.writer.writer_factory import writer_factory


done_count = 1
total = 0

async def process_single_day(day: str, parser, ai_service, writer, logger):
    """
    Processes the diary entry of a single day.
    :param day:
    :param parser:
    :param ai_service:
    :param writer:
    :param logger:
    :return:
    """
    global done_count
    global total
    try:
        # get chat log
        logger.debug(f'Getting chat log for {day}...')
        chat_log = parser.get_chat_log(day)

        # compute summary (con controllo concorrenza automatico)
        logger.debug(f'Generating summary for {day}...')
        summary = await ai_service.get_summary_async(chat_log)

        # write to file
        logger.debug(f'Writing file for {day}...')
        writer.write(day, chat_log, summary)

        logger.debug(f'Completed processing for {day}')
        logger.info(f'{done_count}/{total} done!')
        done_count = done_count + 1
        return day

    except Exception as e:
        logger.error(f'Error processing {day}: {e}')
        raise


async def batch_process_days(day_list: list[str], parser, ai_service, writer, logger):
    """
    Processes the diary entry of  multiple days with concurrent processing.
    """
    global total
    total = len(day_list)
    # Create a task for every day
    tasks = [process_single_day(day, parser, ai_service, writer, logger) for day in day_list]

    # Execute tasks with parallel processing
    completed_days = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    for i, result in enumerate(completed_days):
        if isinstance(result, Exception):
            logger.error(f'Failed to process {day_list[i]}: {result}')

    return completed_days


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

    # get summary and write each day diary
    asyncio.run(batch_process_days(day_list, parser, ai_service, writer, logger))

    writer.close()
