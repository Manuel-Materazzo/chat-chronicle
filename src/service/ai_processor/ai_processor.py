import asyncio
from abc import ABC, abstractmethod

from langchain_core.globals import set_verbose

from src.dto.message import Message
from src.service.logging_service import LoggingService


class AiProcessor(ABC):

    def __init__(self, logging_service: LoggingService, concurrency_limit: int, initial_state: dict):
        set_verbose(True)
        self.logger = logging_service.get_logger(__name__)
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)
        self.initial_state = initial_state

        # Create LangGraph
        self.graph = self.build_graph()

    @abstractmethod
    def build_graph(self):
        """Build and compile the LangGraph"""
        pass

    def get_summary_sync(self, messages: list[Message]) -> str:
        """Synchronous wrapper for getting AI summary"""
        return asyncio.run(self.get_summary_async(messages))

    async def get_summary_async(self, messages: list[Message]) -> str:
        """Asynchronous method to get AI summary with concurrency control"""

        state = self.initial_state.copy()
        state["messages"] = messages

        async with self.semaphore:
            # Invoke the graph
            result = await self.graph.ainvoke(state)

            # Return the summary from the result
            return result.get("summary", "")
