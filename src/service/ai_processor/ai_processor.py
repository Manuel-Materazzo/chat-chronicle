import asyncio
from abc import ABC, abstractmethod

from langchain_core.globals import set_verbose


class AiProcessor(ABC):

    def __init__(self, concurrency_limit: int, initial_state: dict):
        set_verbose(True)
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)
        self.initial_state = initial_state

        # Create LangGraph
        self.graph = self.build_graph()

    @abstractmethod
    def build_graph(self):
        """Build and compile the LangGraph"""
        pass

    def get_summary_sync(self, chat_log: str) -> str:
        """Synchronous wrapper for getting AI summary"""
        return asyncio.run(self.get_summary_async(chat_log))

    async def get_summary_async(self, chat_log: str) -> str:
        """Asynchronous method to get AI summary with concurrency control"""

        state = self.initial_state.copy()
        state["chat_log"] = chat_log

        async with self.semaphore:
            # Invoke the graph
            result = await self.graph.ainvoke(state)

            # Return the summary from the result
            return result.get("summary", "")
