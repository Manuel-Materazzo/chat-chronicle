import asyncio
import logging
import threading
from abc import ABC, abstractmethod

from langchain_core.globals import set_verbose

from src.dto.message import Message
from src.service.logging_service import LoggingService

# Shared event loop for sync calls (avoids creating a new loop per request)
_loop = asyncio.new_event_loop()
_loop_thread = threading.Thread(target=_loop.run_forever, daemon=True)
_loop_thread.start()


class AiProcessor(ABC):

    def __init__(self, logging_service: LoggingService, concurrency_limit: int, initial_state: dict):
        self.logger = logging_service.get_logger(__name__)
        set_verbose(self.logger.isEnabledFor(logging.DEBUG))
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)
        self.initial_state = initial_state

        # Create LangGraph
        self.graph = self.build_graph()

    @abstractmethod
    def build_graph(self):
        """Build and compile the LangGraph"""
        pass

    def save_graph(self):
        """Draws a mermaid representation of the built graph"""
        png_data = self.graph.get_graph().draw_mermaid_png()

        with open("graph.png", "wb") as f:
            f.write(png_data)

    def get_summary_sync(self, messages: list[Message]) -> dict:
        """Synchronous wrapper for getting AI summary"""
        future = asyncio.run_coroutine_threadsafe(self.get_summary_async(messages), _loop)
        return future.result()

    async def get_summary_async(self, messages: list[Message]) -> dict:
        """Asynchronous method to get AI summary with concurrency control"""

        state = self.initial_state.copy()
        state["messages"] = messages

        async with self.semaphore:
            # Invoke the graph, setting a high recursion limit, because iterations are programmatically decided
            return await self.graph.ainvoke(state, {"recursion_limit": 1000})
