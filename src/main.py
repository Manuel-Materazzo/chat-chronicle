import os

from src.service.config_service import get_configs
from src.service.ai_service import AiService
from src.service.logging_service import LoggingService
from src.service.parser.parser_factory import parser_factory, ext_factory
from src.service.writer.writer_factory import writer_factory

# read configs
config = get_configs('../config.yml')

logging_service = LoggingService(config)
logger = logging_service.get_logger(__name__)

if __name__ == "__main__":
    # read configs
    input_path = config.get('input', {}).get('path', './')
    logger.debug(f'input_path: {input_path}')
    input_directory = os.fsencode(input_path)
    logger.debug(f'Input directory: {input_directory}')

    # generate files list
    extension = ext_factory(config)
    logger.debug(f'Listing files with {extension} extension...')
    files = []
    for file in os.listdir(input_directory):
        filename = os.fsdecode(file)
        logger.debug(f'File or folder found: {filename}')
        if filename.lower().endswith(extension):
            logger.debug(f'Saving it as: {input_path}/{filename}')
            files.append(f"{input_path}/{filename}")

    if len(files) == 0:
        raise FileNotFoundError(f"No {extension} files found on {input_path}")
    else:
        logger.info(f'Found {len(files)} files to process...')

    logger.debug('Reading files...')

    # read files
    parser = parser_factory(config, files)

    day_list = parser.get_available_days()

    logger.info(f'Found {len(day_list)} days of messages...')

    # instantiate writer
    writer = writer_factory(config)

    # create AI service
    ai_service = AiService(config)

    done_count = 1

    # get summary and write each day diary
    for day in parser.get_available_days():
        logger.debug(f'Getting chat log for {day}...')
        chat_log = parser.get_chat_log(day)
        logger.debug(f'Generating summary for {day}...')
        summary = ai_service.get_summary_sync(chat_log)
        logger.debug(f'Writing file for {day}...')
        writer.write(day, chat_log, summary)
        logger.info(f'{done_count}/{len(day_list)} done!')

    writer.close()
