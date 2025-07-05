import os
from enum import StrEnum
import textwrap

from yaml.representer import SafeRepresenter
from yaml import SafeLoader, SafeDumper, dump, load

from src.dto.enums.input_file_type import InputFileType
from src.dto.enums.log_levels import LogLevel
from src.dto.enums.summarization_strategy import SummarizationStrategy
from src.dto.enums.writer_type import WriterType

config = dict()

# represent enums as string
SafeDumper.add_multi_representer(
    StrEnum,
    SafeRepresenter.represent_str,
)


def str_presenter(dumper, data):
    """
    Fixes multiline string representation
    :param dumper:
    :param data:
    :return:
    """
    if '\n' in data:
        clean_data = "\n".join(line.lstrip().rstrip() for line in data.splitlines())
        return dumper.represent_scalar('tag:yaml.org,2002:str', clean_data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


def get_configs(filename: str) -> dict:
    """
    Reads the config file, or creates it if it doesn't exist.
    :param filename:
    :return:
    """
    global config

    # skip if already loaded
    if config.get('logs', None) is not None:
        return config

    # output default config file if not found
    if not os.path.isfile(filename):
        config = {
            'batch': {
                'input': {
                    'type': InputFileType.INSTAGRAM_EXPORT,
                    'path': './input/',
                },
                'output': {
                    'type': WriterType.TXT,
                    'path': './output/',
                    'merge-to-one-file': True,
                    'export-intermediate-steps': False,
                }
            },
            'logs': {
                'level': LogLevel.INFO,
            },
            'parsing': {
                'chars-per-token': 4.0,
                'token-per-chunk': 4000,
                'chat-sessions': {
                    'enabled': True,
                    'sleep-window-start-hour': 2,
                    'sleep-window-end-hour': 9,
                },
                'ignore-chat': {
                    'enabled': False,
                    'ignore-before': '1990-01-01',
                    'ignore-after': '2150-01-01'
                },
                'messages': {
                    'user-interactions': {
                        'message-like': 'Ha messo "Mi piace" a un messaggio',
                        'message-reaction': 'Ha aggiunto la reazione'
                    },
                    'user-content': {
                        'posts-and-reels': '[Shared an internet video]',
                        'video-uploads': '[Sent a video of himself]',
                        'photo-uploads': '[Sent a photo of himself]',
                        'audio-messages': '[Sent an audio message]'
                    }
                }
            },
            'inference-service': {
                'endpoint': 'http://127.0.0.1:1234/v1',
                'api-key': 'xxx',
                'concurrency-limit': 2,
                'timeout': 600,
                'connect-timeout': 10
            },
            'summarization': {
                'strategy': SummarizationStrategy.MAP_REDUCE,
                'linear-strategy': {
                    'max-tokens': 2000,
                    'model-name': 'gemma-3-4b-it-qat',
                    'temperature': 0.4,
                    'top-p': 0.7,
                    'system-prompt': """You are a bot that writes simple diary entries.
                        Below are messages from one day of Instagram DMs.
                        Each message starts with the sender’s name, then a colon, then the text.
                        Your job is to write a short diary entry that summarizes what the user did or talked about that day, based only on the provided messages.
                    """,
                    'user-prompt': """Messages:
                        {messages}
                        Diary entry:
                    """,
                },
                'map-reduce-strategy': {
                    'map-agent': {
                        'max-tokens': 2000,
                        'model-name': 'gemma-3-4b-it-qat',
                        'temperature': 0.2,
                        'top-p': 0.7,
                        'system-prompt': """You are an assistant who analyzes blocks of chat messages to extract key information.
                                Analyze this block of messages and create a structured summary of activities, conversations, and events.
                                Each message starts with the sender name, then a colon, then the text.
                                SPECIFIC INSTRUCTIONS:
                                1. Identify the main events
                                2. Note the emotions expressed
                                3. Record important conversation topics
                                4. Maintain the chronological order of events
                                5. Include only facts present in the messages
                        """,
                        'user-prompt': """Messages:
                                {messages}
                                
                                Now, following the instructions step-by-step, write the summary.
                         """,
                        'mini-summary-template': """Summary Start Date: {start-date}
                                Summary End Date: {end-date}
                                {content}
                        """,
                    },
                    'reduce-agent': {
                        'max-tokens': 2000,
                        'model-name': 'gemma-3-4b-it-qat',
                        'temperature': 0.4,
                        'top-p': 0.7,
                        'system-prompt': """You are an assistant who writes personal journal entries by combining message block summaries.
                                You will receive several structured message block summaries from the same day.
                                Each message starts with the sender name, then a colon, then the text.
                                Your job is to write a short diary by combining all summaries into a single coherent journal entry.
                                CRITICAL INSTRUCTIONS:
                                1. Write in first person
                                2. Organize all events chronologically
                                3. Create a smooth narrative flow between different blocks
                                4. Maintain the personal and reflective tone of a journal
                                5. Eliminate duplication between blocks
                                6. Length: 150-250 words
                                7. Begin with "Dear Diary," and end with a reflection on the day.
                        """,
                        'user-prompt': """Messages:
                                {messages}
                                
                                Now, following the instructions step-by-step, write the diary page.
                        """,
                    },
                }

            }
        }
        with open(filename, 'w') as configfile:
            SafeDumper.add_representer(str, str_presenter)
            dump(config, configfile, Dumper=SafeDumper, allow_unicode=True)

    # load config from file
    with open(filename, 'r') as configfile:
        config = load(configfile, Loader=SafeLoader)

    return config
