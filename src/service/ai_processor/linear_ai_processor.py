from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

from src.dto.message import Message
from src.service.ai_processor.ai_processor import AiProcessor
from src.service.parser.parser import get_chat_log


# Define the state schema for LangGraph
class ChatState(TypedDict, total=False):
    ai_chat: Annotated[list, add_messages]
    messages: list[Message]
    summary: str


class LinearAiProcessor(AiProcessor):
    def __init__(self, system_prompt: str, user_prompt: str, model_name: str = "gemma-3-4b-it-qat",
                 temperature: float = 0.4, max_tokens: int = 2000, top_p: float = 0.7, api_key: str = "",
                 base_url: str = "", timeout: int = 600, concurrency_limit: int = 2):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

        # Initialize OpenAI client with custom configuration
        self.openai_client = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=2
        )

        # Prepare initial state
        initial_state = {
            "ai_chat": [],
            "messages": [],
            "summary": ""
        }

        super().__init__(concurrency_limit, initial_state)

    def build_graph(self) -> CompiledStateGraph:
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
        # get chat log
        messages = state["messages"]
        chat_log = get_chat_log(messages)

        ai_chat_messages = []
        if self.system_prompt:
            ai_chat_messages.append(SystemMessage(content=self.system_prompt))

        # Format the user prompt with the chat log
        formatted_prompt = self.user_prompt.format(messages=chat_log) if self.user_prompt else chat_log
        ai_chat_messages.append(HumanMessage(content=formatted_prompt))

        # Get response from LLM
        response = await self.openai_client.ainvoke(ai_chat_messages)
        summary = response.content if response.content else ""

        return {
            "ai_chat": ai_chat_messages + [response],
            "summary": summary
        }
