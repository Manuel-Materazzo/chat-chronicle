import asyncio
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph


# Define the state schema for LangGraph
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    chat_log: str
    summary: str


class AiService:
    def __init__(self, config: dict):
        self.config = config
        self.concurrency_limit = config.get('inference-service', {}).get('concurrency-limit', 2)
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)

        # Initialize OpenAI client with custom configuration
        self.openai_client = self._get_openai_client(config)

        # Create LangGraph
        self.graph = self._build_graph()

    def get_summary_sync(self, chat_log: str) -> str:
        """Synchronous wrapper for getting AI summary"""
        return asyncio.run(self.get_summary_async(chat_log))

    async def get_summary_async(self, chat_log: str) -> str:
        """Asynchronous method to get AI summary with concurrency control"""

        # Prepare initial state
        initial_state = {
            "messages": [],
            "chat_log": chat_log,
            "summary": ""
        }

        async with self.semaphore:
            # Invoke the graph
            result = await self.graph.ainvoke(initial_state)

            # Return the summary from the result
            return result.get("summary", "")

    def _get_openai_client(self, config: dict) -> ChatOpenAI:
        """Configure and return OpenAI client"""
        # Get timeouts from config
        timeout = config.get('inference-service', {}).get('timeout', 600)

        return ChatOpenAI(
            model=config.get('llm', {}).get('model-name', 'gpt-3.5-turbo'),
            temperature=config.get('llm', {}).get('temperature', 0.7),
            max_tokens=config.get('llm', {}).get('max-tokens', 2000),
            top_p=config.get('llm', {}).get('top-p', 0.8),
            api_key=config.get('inference-service', {}).get('api-key', ''),
            base_url=config.get('inference-service', {}).get('endpoint', ''),
            timeout=timeout,
            max_retries=2
        )

    def _build_graph(self) -> CompiledStateGraph:
        """Build and compile the LangGraph"""
        # Create the state graph
        graph_builder = StateGraph(ChatState)

        # Add the summarization node
        graph_builder.add_node("summarize", self._summarize_node)

        # draw graph
        graph_builder.add_edge(START, "summarize")
        graph_builder.add_edge("summarize", END)


        # Compile the graph
        return graph_builder.compile()

    async def _summarize_node(self, state: ChatState) -> ChatState:
        """Node function that processes chat logs and generates summaries"""
        chat_log = state["chat_log"]

        # Create messages for the LLM
        system_prompt = self.config.get('llm', {}).get('system-prompt', '')
        user_prompt = self.config.get('llm', {}).get('user-prompt', '')

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Format the user prompt with the chat log
        formatted_prompt = user_prompt.format(messages=chat_log) if user_prompt else chat_log
        messages.append(HumanMessage(content=formatted_prompt))

        # Get response from LLM
        response = await self.openai_client.ainvoke(messages)
        summary = response.content if response.content else ""

        return {
            "messages": messages + [response],
            "summary": summary
        }
