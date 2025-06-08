import os
import asyncio

from openai import AsyncOpenAI

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel

from src.service.config_service import get_configs
from src.service.parser.parser_factory import parser_factory, ext_factory
from src.service.writer.writer_factory import writer_factory

# read configs
config = get_configs('../config.yml')

service_id = "local-gpt"
kernel = Kernel()

# create LLM API client and add it to kernel
openAIClient: AsyncOpenAI = AsyncOpenAI(
    api_key=config.get('inference-service', {}).get('api-key', ''),
    base_url=config.get('inference-service', {}).get('endpoint', ''),
)
kernel.add_service(
    OpenAIChatCompletion(
        service_id=service_id,
        ai_model_id=config.get('llm', {}).get('model-name', ''),
        async_client=openAIClient
    )
)

# set llm params on kernel
settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
settings.max_tokens = config.get('llm', {}).get('max-tokens', 2000)
settings.temperature = config.get('llm', {}).get('temperature', 0.7)
settings.top_p = config.get('llm', {}).get('top-p', 0.8)

# add chat function to kernel
chat_function = kernel.add_function(
    plugin_name="ChatBot",
    function_name="Chat",
    prompt=config.get('llm', {}).get('user-prompt', ''),
    template_format="semantic-kernel",
    prompt_execution_settings=settings,
)

# create chat history
chat_history = ChatHistory(system_message=config.get('llm', {}).get('system-prompt', ''))


async def get_summary(messages: str) -> str:
    result = await kernel.invoke(chat_function, KernelArguments(messages=messages, chat_history=chat_history))
    if result is None:
        return ""
    return result


if __name__ == "__main__":
    # read configs
    input_path = config.get('input', {}).get('path', './')

    input_directory = os.fsencode(input_path)

    # generate files list
    extension = ext_factory(config)
    files = []
    for file in os.listdir(input_directory):
        filename = os.fsdecode(file)
        if filename.lower().endswith(extension):
            files.append(f"{input_path}/{filename}")

    # read files
    parser = parser_factory(config, files)

    # instantiate writer
    writer = writer_factory(config)

    # get summary and write each day diary
    for day in parser.get_available_days():
        chat_log = parser.get_chat_log(day)
        summary = asyncio.run(get_summary(chat_log))
        writer.write(day, chat_log, summary)

    writer.close()