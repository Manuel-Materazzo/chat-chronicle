import asyncio
import os

from src.dto.enums.input_file_type import InputFileType
from src.service.ai_processor.ai_processor import AiProcessor
from src.service.ai_processor.ai_processor_factory import ai_processor_factory
from src.service.config_service import get_nested
from src.service.logging_service import LoggingService
from src.service.parser.parser import Parser
from src.service.parser.parser_factory import parser_factory
from src.service.reader.reader_factory import reader_factory
from src.service.writer.writer import Writer
from src.service.writer.writer_factory import writer_factory

def process_all(config: dict):
    # generate loggers
    logging_service = LoggingService(config)
    logger = logging_service.get_logger(__name__)

    # read configs
    input_file_type = get_nested(config, 'batch.input.type', InputFileType.INSTAGRAM_EXPORT)
    input_path = get_nested(config, 'batch.input.path', './')
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
        # validate input file is not empty
        if os.path.getsize(file) == 0:
            logger.warning(f'Skipping empty file: {file}')
            continue
        try:
            logger.debug(f'Reading {file}...')
            raw_messages = reader.read(file)
        except Exception as e:
            logger.error(f'Failed to read {file}: {e}')
            continue
        logger.debug(f'Standardizing {file}...')
        standardized_messages = reader.standardize_messages(raw_messages)
        if not standardized_messages:
            logger.warning(f'No messages found in {file}, skipping')
            continue
        logger.debug(f'Parsing {file}...')
        parser.parse(standardized_messages)

    # sort bucket
    logger.debug('Sorting parser bucket...')
    parser.sort_bucket()

    day_list = parser.get_available_days()
    logger.info(f'Found {len(day_list)} days of messages...')

    # instantiate writer
    writer = writer_factory(config)

    # create AI processor
    ai_processor = ai_processor_factory(config)

    # filter out already-processed days when not writing to a single file
    if not writer.single_file:
        existing_files = set(os.listdir(writer.folder)) if os.path.isdir(writer.folder) else set()
        skipped = [day for day in day_list if any(f.startswith(day) for f in existing_files)]
        if skipped:
            logger.info(f'Skipping {len(skipped)} already-processed days')
            day_list = [day for day in day_list if day not in skipped]

    # get summary and write each day diary
    asyncio.run(_batch_process_days(day_list, parser, ai_processor, writer, logger))


async def _batch_process_days(day_list: list[str], parser: Parser, ai_processor: AiProcessor, writer: Writer, logger):
    """
    Processes the diary entry of  multiple days with concurrent processing.
    """
    total = len(day_list)
    counter = {"done": 0}
    # Create a task for every day
    tasks = [_process_single_day(day, parser, ai_processor, writer, logger, counter, total) for day in day_list]

    # Execute tasks with parallel processing
    completed_days = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    for i, result in enumerate(completed_days):
        if isinstance(result, Exception):
            logger.error(f'Failed to process {day_list[i]}: {result}')

    writer.close()

    return completed_days


async def _process_single_day(day: str, parser: Parser, ai_processor: AiProcessor, writer: Writer, logger,
                              counter: dict, total: int):
    """
    Processes the diary entry of a single day.
    :param day:
    :param parser:
    :param ai_processor:
    :param writer:
    :param logger:
    :return:
    """
    try:
        # get chat log
        logger.debug(f'Getting chat log for {day}...')
        messages = parser.get_messages(day)

        # compute summary
        logger.debug(f'Generating summary for {day}...')
        summary = await ai_processor.get_summary_async(messages)

        # write to file
        logger.debug(f'Writing file for {day}...')
        writer.write(day, summary)

        counter["done"] += 1
        logger.debug(f'Completed processing for {day}')
        logger.info(f'{counter["done"]}/{total} done!')
        return day

    except Exception as e:
        logger.error(f'Error processing {day}: {e}')
        raise
