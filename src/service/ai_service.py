import asyncio

from openai import AsyncOpenAI
from semantic_kernel.connectors.ai import PromptExecutionSettings

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel
from semantic_kernel.services.ai_service_client_base import AIServiceClientBase

service_id = "local-gpt"


class AiService:

    def __init__(self, config: dict):
        self.kernel = Kernel()
        # create empty chat history
        self.empty_chat_history = ChatHistory(system_message=config.get('llm', {}).get('system-prompt', ''))

        # create LLM API client and add it to kernel
        chat_completion_client = self.__get_chat_service(config)
        self.kernel.add_service(chat_completion_client)

        # set llm params on kernel
        settings = self.__get_setting(config)

        # add chat function to kernel
        self.chat_function = self.kernel.add_function(
            plugin_name="ChatBot",
            function_name="Chat",
            prompt=config.get('llm', {}).get('user-prompt', ''),
            template_format="semantic-kernel",
            prompt_execution_settings=settings,
        )
        self.concurrency_limit = config.get('inference-service', {}).get('concurrency-limit', 2)
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)

    def get_summary_sync(self, chat_log: str) -> str:
        return asyncio.run(self.__get_ai_full_response(chat_log))

    async def get_summary_async(self, chat_log: str) -> str:
        async with self.semaphore:
            return await self.__get_ai_full_response(chat_log)

    async def __get_ai_full_response(self, messages: str) -> str:
        result = await self.kernel.invoke(
            self.chat_function,
            KernelArguments(messages=messages, chat_history=self.empty_chat_history)
        )
        if result is None:
            return ""
        return str(result)

    def __get_setting(self, config: dict) -> PromptExecutionSettings:
        """
        Returns the LLM settings object
        :param config:
        :return:
        """
        settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id)
        settings.max_tokens = config.get('llm', {}).get('max-tokens', 2000)
        settings.temperature = config.get('llm', {}).get('temperature', 0.7)
        settings.top_p = config.get('llm', {}).get('top-p', 0.8)
        return settings

    def __get_chat_service(self, config: dict) -> AIServiceClientBase:
        """
        Returns the chat completion client
        :param config:
        :return:
        """
        openAIClient: AsyncOpenAI = AsyncOpenAI(
            api_key=config.get('inference-service', {}).get('api-key', ''),
            base_url=config.get('inference-service', {}).get('endpoint', ''),
        )
        return OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id=config.get('llm', {}).get('model-name', ''),
            async_client=openAIClient
        )
