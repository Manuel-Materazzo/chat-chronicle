import os
from yaml import SafeLoader, SafeDumper, dump, load

config = dict()


def str_presenter(dumper, data):
    if '\n' in data:
        clean_data = "\n".join(line.rstrip() for line in data.splitlines())
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
    if config.get('Input', None) is not None:
        return config

    # output default config file if not found
    if not os.path.isfile(filename):
        config['input'] = {
            'file-type': 'INSTAGRAM_EXPORT',
            'folder': '../input/',
        }
        config['output'] = {
            'folder': '../output/',
        }
        config['inference-service'] = {
            'endpoint': 'http://127.0.0.1:1234/v1',
            'api-key': 'xxx',
        }
        config['llm'] = {
            'model-name': 'gemma-3-4b-it-qat',
            'max-tokens': 2000,
            'temperature': 0.7,
            'top-p': 0.8,
            'system-prompt': """You are a bot that writes simple diary entries.
Below are messages from one day of Instagram DMs.
Each message starts with the sender’s name, then a colon, then the text.
Your job is to write a short diary entry that summarizes what the user did or talked about that day, based only on the provided messages.
""",
            'user-prompt': """Messages:
{{$messages}}
Diary entry:
""",
        }
        with open(filename, 'w') as configfile:
            SafeDumper.add_representer(str, str_presenter)
            dump(config, configfile, Dumper=SafeDumper, allow_unicode=True)

    # load config from file
    with open(filename, 'r') as configfile:
        config = load(configfile, Loader=SafeLoader)

    return config
