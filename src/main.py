import asyncio

from openai import AsyncOpenAI

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel

from src.services.instagram_export import InstagramExport

system_message = """You are a bot that writes simple diary entries.
Below are messages from one day of Instagram DMs.
Each message starts with the sender’s name, then a colon, then the text.
Your job is to write a short diary entry that summarizes what the user did or talked about that day, based only on the provided messages.
"""

kernel = Kernel()

service_id = "local-gpt"

openAIClient: AsyncOpenAI = AsyncOpenAI(
    api_key="pepino",
    base_url="http://127.0.0.1:1234/v1",
)
kernel.add_service(
    OpenAIChatCompletion(service_id=service_id, ai_model_id="gemma-3-4b-it-qat", async_client=openAIClient))

settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
settings.max_tokens = 2000
settings.temperature = 0.7
settings.top_p = 0.8

chat_function = kernel.add_function(
    plugin_name="ChatBot",
    function_name="Chat",
    prompt=system_message + """    
{{$chat_history}}
Messages:
{{$messages}}
Diary entry:
""",
    template_format="semantic-kernel",
    prompt_execution_settings=settings,
)

chat_history = ChatHistory(system_message=system_message)


async def main(messages: str) -> None:
    answer = await kernel.invoke(chat_function, KernelArguments(messages=messages, chat_history=chat_history))
    print(f"{answer}")


if __name__ == "__main__":
    reader = InstagramExport("C:\\message_1.json")
    day = reader.get_available_days()[0]
    # print(reader.get_diary_record(day))
    asyncio.run(main(reader.get_diary_record(day)))
