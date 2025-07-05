from typing import Annotated, TypedDict, Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from operator import add
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

from src.dto.chunk import Chunk
from src.dto.message import Message
from src.service.ai_processor.ai_processor import AiProcessor
from src.service.logging_service import LoggingService
from src.service.parser.parser import get_chat_log_chunked


# Define the state schema for LangGraph
class ChatState(TypedDict, total=False):
    ai_chat: Annotated[list, add_messages]
    messages: list[Message]
    chunks: list[Chunk]
    mini_summaries: Annotated[list, add]
    summary: str


class MapReduceAiProcessor(AiProcessor):
    def __init__(self, logging_service: LoggingService, map_system_prompt: str = "", map_user_prompt: str = "",
                 map_model_name: str = "gemma-3-4b-it-qat",
                 map_temperature: float = 0.4, map_max_tokens: int = 2000, map_top_p: float = 0.7,
                 reduce_system_prompt: str = "", reduce_user_prompt: str = "",
                 reduce_model_name: str = "gemma-3-4b-it-qat",
                 reduce_temperature: float = 0.4, reduce_max_tokens: int = 2000, reduce_top_p: float = 0.7,
                 token_per_chunk: int = 4000, api_key: str = "", base_url: str = "", timeout: int = 600,
                 concurrency_limit: int = 2):
        self.map_system_prompt = map_system_prompt
        self.reduce_system_prompt = reduce_system_prompt
        self.map_user_prompt = map_user_prompt
        self.reduce_user_prompt = reduce_user_prompt
        self.token_per_chunk = token_per_chunk

        # Initialize OpenAI client with custom configuration
        self.map_client = ChatOpenAI(
            model=map_model_name,
            temperature=map_temperature,
            max_tokens=map_max_tokens,
            top_p=map_top_p,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=2
        )
        self.reduce_client = ChatOpenAI(
            model=reduce_model_name,
            temperature=reduce_temperature,
            max_tokens=reduce_max_tokens,
            top_p=reduce_top_p,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=2
        )

        # Prepare initial state
        initial_state = {
            "ai_chat": [],
            "messages": [],
            "chunks": [],
            "mini_summaries": [],
            "summary": ""
        }

        super().__init__(logging_service, concurrency_limit, initial_state)

    def build_graph(self) -> CompiledStateGraph:
        """Build and compile the LangGraph"""
        # Create the state graph
        graph_builder = StateGraph(ChatState)

        # Add the summarization node
        graph_builder.add_node("prepare-messages", self._prepare_messages)
        graph_builder.add_node("map-agent", self._map)
        graph_builder.add_node("reduce-agent", self._reduce)

        # draw graph
        graph_builder.add_edge(START, "prepare-messages")
        graph_builder.add_edge("prepare-messages", "map-agent")
        graph_builder.add_conditional_edges(
            "map-agent",
            self._should_keep_mapping,
            {
                True: "map-agent",
                False: "reduce-agent"
            })
        graph_builder.add_edge("reduce-agent", END)

        # Compile the graph
        return graph_builder.compile()

    async def _prepare_messages(self, state: ChatState) -> ChatState:
        """Node function that processes chat logs and generates summaries"""
        # get chat log
        messages = state["messages"]
        chunks = get_chat_log_chunked(messages, self.token_per_chunk)

        return {
            "chunks": chunks,
        }

    def _should_keep_mapping(self, state: ChatState) -> bool:
        # Continue if there are chunks in the queue
        if len(state["chunks"]) > 0:
            return True
        else:
            self.logger.debug("Mapping recursion hit the stop condition!")
            return False

    async def _map(self, state: ChatState) -> ChatState:
        """Node function that processes chat chunks and generates mini summaries"""
        # get chat log
        self.logger.info(f'Processing chat chunk, {len(state["chunks"])} left')
        chunk: Chunk = state["chunks"].pop()

        chat_log = chunk["content"]

        ai_chat_messages = []
        if self.map_system_prompt:
            ai_chat_messages.append(SystemMessage(content=self.map_system_prompt))

        # Format the user prompt with the chat log
        formatted_prompt = self.map_user_prompt.format(messages=chat_log) if self.map_user_prompt else chat_log
        ai_chat_messages.append(HumanMessage(content=formatted_prompt))

        # Get response from LLM
        response = await self.map_client.ainvoke(ai_chat_messages)
        mini_summary = response.content if response.content else ""

        return {
            "mini_summaries": [mini_summary],
        }

    async def _reduce(self, state: ChatState) -> ChatState:
        """Node function that processes mini summaries and generates a final summary"""
        # get summaries
        self.logger.info(f'Processing {len(state["mini_summaries"])} mini summaries')
        summaries = "\n\n".join(state["mini_summaries"])

        ai_chat_messages = []
        if self.reduce_system_prompt:
            ai_chat_messages.append(SystemMessage(content=self.reduce_system_prompt))

        # Format the user prompt with the chat log
        formatted_prompt = self.reduce_user_prompt.format(summaries=summaries) if self.reduce_user_prompt else summaries
        ai_chat_messages.append(HumanMessage(content=formatted_prompt))

        # Get response from LLM
        response = await self.reduce_client.ainvoke(ai_chat_messages)
        summary = response.content if response.content else ""

        return {
            "summary": summary,
        }