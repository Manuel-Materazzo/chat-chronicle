import asyncio
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from src.dto.enums.summarization_strategy import SummarizationStrategy
from src.service.ai_processor.ai_processor_factory import ai_processor_factory
from src.service.ai_processor.linear_ai_processor import LinearAiProcessor
from src.service.ai_processor.map_reduce_ai_processor import MapReduceAiProcessor
from src.service.logging_service import LoggingService


def _logging_service():
    return LoggingService({'logs': {'level': 'WARNING'}})


def _make_message(sender, content, timestamp, token_count=10):
    return {
        'sender_name': sender,
        'timestamp': timestamp,
        'content': content,
        'token_count': token_count,
    }


class TestLinearAiProcessor(unittest.TestCase):

    @patch('src.service.ai_processor.linear_ai_processor.ChatOpenAI')
    def test_build_graph(self, mock_chat):
        processor = LinearAiProcessor(
            _logging_service(), "system", "user: {messages}", "model", 0.4, 2000, 0.7,
            "key", "http://localhost", 600, 2
        )
        self.assertIsNotNone(processor.graph)

    @patch('src.service.ai_processor.linear_ai_processor.ChatOpenAI')
    def test_summarize_node(self, mock_chat):
        mock_response = MagicMock()
        mock_response.content = "Summary text"
        mock_client = MagicMock()
        mock_client.ainvoke = AsyncMock(return_value=mock_response)

        processor = LinearAiProcessor(
            _logging_service(), "You are a bot", "{messages}", "model", 0.4, 2000, 0.7,
            "key", "http://localhost", 600, 2
        )
        processor.openai_client = mock_client

        messages = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30)),
        ]
        state = {"messages": messages, "ai_chat": [], "summary": ""}
        result = asyncio.run(processor._summarize_node(state))
        self.assertEqual(result["summary"], "Summary text")
        mock_client.ainvoke.assert_called_once()

    @patch('src.service.ai_processor.linear_ai_processor.ChatOpenAI')
    def test_get_summary_async(self, mock_chat):
        from langchain_core.messages import AIMessage
        mock_response = AIMessage(content="Diary entry")
        mock_client = MagicMock()
        mock_client.ainvoke = AsyncMock(return_value=mock_response)

        processor = LinearAiProcessor(
            _logging_service(), "System prompt", "{messages}", "model", 0.4, 2000, 0.7,
            "key", "http://localhost", 600, 2
        )
        processor.openai_client = mock_client

        messages = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30)),
        ]
        result = asyncio.run(processor.get_summary_async(messages))
        self.assertIn("summary", result)

    @patch('src.service.ai_processor.linear_ai_processor.ChatOpenAI')
    def test_empty_system_prompt(self, mock_chat):
        mock_response = MagicMock()
        mock_response.content = "Result"
        mock_client = MagicMock()
        mock_client.ainvoke = AsyncMock(return_value=mock_response)

        processor = LinearAiProcessor(
            _logging_service(), "", "{messages}", "model", 0.4, 2000, 0.7,
            "key", "http://localhost", 600, 2
        )
        processor.openai_client = mock_client

        state = {
            "messages": [_make_message("Alice", "Hi", datetime(2024, 1, 15, 10, 0))],
            "ai_chat": [], "summary": ""
        }
        result = asyncio.run(processor._summarize_node(state))
        # Should not include a SystemMessage when prompt is empty
        call_args = mock_client.ainvoke.call_args[0][0]
        from langchain_core.messages import SystemMessage
        system_msgs = [m for m in call_args if isinstance(m, SystemMessage)]
        self.assertEqual(len(system_msgs), 0)


class TestMapReduceAiProcessor(unittest.TestCase):

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_build_graph(self, mock_chat):
        processor = MapReduceAiProcessor(
            _logging_service(),
            map_system_prompt="map sys", map_user_prompt="{messages}",
            map_summary_template="{content} {start-date} {end-date}",
            reduce_system_prompt="reduce sys", reduce_user_prompt="{summaries}",
            api_key="key", base_url="http://localhost", timeout=600, concurrency_limit=2
        )
        self.assertIsNotNone(processor.graph)

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_prepare_messages(self, mock_chat):
        processor = MapReduceAiProcessor(
            _logging_service(),
            map_system_prompt="", map_user_prompt="{messages}",
            reduce_system_prompt="", reduce_user_prompt="{summaries}",
            token_per_chunk=100,
            api_key="key", base_url="http://localhost", timeout=600, concurrency_limit=2
        )
        messages = [
            _make_message("Alice", "Hi " * 50, datetime(2024, 1, 15, 10, i % 60), token_count=50)
            for i in range(20)
        ]
        state = {"messages": messages, "chunks": [], "mini_summaries": [], "ai_chat": [], "summary": ""}
        result = asyncio.run(processor._prepare_messages(state))
        self.assertIn("chunks", result)
        self.assertIsInstance(result["chunks"], list)

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_should_keep_mapping_true(self, mock_chat):
        processor = MapReduceAiProcessor(
            _logging_service(),
            api_key="key", base_url="http://localhost", timeout=600, concurrency_limit=2
        )
        state = {"chunks": [{"content": "test"}]}
        self.assertTrue(processor._should_keep_mapping(state))

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_should_keep_mapping_false(self, mock_chat):
        processor = MapReduceAiProcessor(
            _logging_service(),
            api_key="key", base_url="http://localhost", timeout=600, concurrency_limit=2
        )
        state = {"chunks": []}
        self.assertFalse(processor._should_keep_mapping(state))

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_map_node(self, mock_chat):
        mock_response = MagicMock()
        mock_response.content = "Mini summary"
        mock_client = MagicMock()
        mock_client.ainvoke = AsyncMock(return_value=mock_response)

        # Empty template to skip formatting (template uses hyphenated keys like {start-date})
        processor = MapReduceAiProcessor(
            _logging_service(),
            map_system_prompt="sys", map_user_prompt="{messages}",
            map_summary_template="",
            reduce_system_prompt="", reduce_user_prompt="",
            api_key="key", base_url="http://localhost", timeout=600, concurrency_limit=2
        )
        processor.map_client = mock_client

        state = {
            "chunks": [{
                "content": "chat log text",
                "start_timestamp": datetime(2024, 1, 15, 10, 0),
                "end_timestamp": datetime(2024, 1, 15, 11, 0),
                "token_count": 100,
                "messages_count": 5,
            }],
            "mini_summaries": [],
            "ai_chat": [],
        }
        result = asyncio.run(processor._map(state))
        self.assertIn("mini_summaries", result)
        self.assertEqual(len(result["mini_summaries"]), 1)
        self.assertEqual(result["mini_summaries"][0], "Mini summary")

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_reduce_node(self, mock_chat):
        mock_response = MagicMock()
        mock_response.content = "Final diary entry"
        mock_client = MagicMock()
        mock_client.ainvoke = AsyncMock(return_value=mock_response)

        processor = MapReduceAiProcessor(
            _logging_service(),
            map_system_prompt="", map_user_prompt="",
            reduce_system_prompt="sys", reduce_user_prompt="{summaries}",
            api_key="key", base_url="http://localhost", timeout=600, concurrency_limit=2
        )
        processor.reduce_client = mock_client

        state = {
            "mini_summaries": ["Summary 1", "Summary 2"],
            "ai_chat": [],
        }
        result = asyncio.run(processor._reduce(state))
        self.assertEqual(result["summary"], "Final diary entry")


class TestAiProcessorFactory(unittest.TestCase):

    @patch('src.service.ai_processor.map_reduce_ai_processor.ChatOpenAI')
    def test_map_reduce_strategy(self, mock_chat):
        config = {
            'logs': {'level': 'WARNING'},
            'summarization': {'strategy': SummarizationStrategy.MAP_REDUCE},
            'inference-service': {'api-key': 'test', 'endpoint': 'http://localhost', 'concurrency-limit': 1,
                                  'timeout': 60},
        }
        processor = ai_processor_factory(config)
        self.assertIsInstance(processor, MapReduceAiProcessor)

    @patch('src.service.ai_processor.linear_ai_processor.ChatOpenAI')
    def test_linear_strategy(self, mock_chat):
        config = {
            'logs': {'level': 'WARNING'},
            'summarization': {'strategy': SummarizationStrategy.LINEAR},
            'inference-service': {'api-key': 'test', 'endpoint': 'http://localhost', 'concurrency-limit': 1,
                                  'timeout': 60},
        }
        processor = ai_processor_factory(config)
        self.assertIsInstance(processor, LinearAiProcessor)

    def test_unsupported_strategy_raises(self):
        config = {
            'logs': {'level': 'WARNING'},
            'summarization': {'strategy': 'UNSUPPORTED'},
            'inference-service': {'api-key': 'test', 'endpoint': 'http://localhost'},
        }
        with self.assertRaises(ValueError):
            ai_processor_factory(config)


if __name__ == '__main__':
    unittest.main()
