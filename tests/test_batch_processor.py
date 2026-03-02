import asyncio
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from src.batch_processor import process_all, _batch_process_days, _process_single_day


def _make_message(sender, content, timestamp, token_count=10):
    return {
        'sender_name': sender,
        'timestamp': timestamp,
        'content': content,
        'token_count': token_count,
    }


class TestProcessSingleDay(unittest.TestCase):

    def test_process_single_day_success(self):
        import src.batch_processor as bp
        bp.done_count = 1
        bp.total = 1

        mock_parser = MagicMock()
        mock_parser.get_messages.return_value = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30))
        ]

        mock_ai = MagicMock()
        mock_ai.get_summary_async = AsyncMock(return_value={"summary": "A great day.", "ai_chat": []})

        mock_writer = MagicMock()
        mock_logger = MagicMock()

        result = asyncio.run(_process_single_day("2024-01-15", mock_parser, mock_ai, mock_writer, mock_logger))
        self.assertEqual(result, "2024-01-15")
        mock_writer.write.assert_called_once_with("2024-01-15", {"summary": "A great day.", "ai_chat": []})

    def test_process_single_day_error_reraises(self):
        import src.batch_processor as bp
        bp.done_count = 1
        bp.total = 1

        mock_parser = MagicMock()
        mock_parser.get_messages.return_value = []

        mock_ai = MagicMock()
        mock_ai.get_summary_async = AsyncMock(side_effect=RuntimeError("AI failed"))

        mock_writer = MagicMock()
        mock_logger = MagicMock()

        with self.assertRaises(RuntimeError):
            asyncio.run(_process_single_day("2024-01-15", mock_parser, mock_ai, mock_writer, mock_logger))


class TestBatchProcessDays(unittest.TestCase):

    def test_batch_process_multiple_days(self):
        mock_parser = MagicMock()
        mock_parser.get_messages.return_value = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30))
        ]

        mock_ai = MagicMock()
        mock_ai.get_summary_async = AsyncMock(return_value={"summary": "Summary", "ai_chat": []})

        mock_writer = MagicMock()
        mock_logger = MagicMock()

        days = ["2024-01-15", "2024-01-16"]
        results = asyncio.run(_batch_process_days(days, mock_parser, mock_ai, mock_writer, mock_logger))
        self.assertEqual(len(results), 2)
        mock_writer.close.assert_called_once()

    def test_batch_process_handles_exceptions(self):
        mock_parser = MagicMock()
        mock_parser.get_messages.return_value = []

        mock_ai = MagicMock()
        mock_ai.get_summary_async = AsyncMock(side_effect=RuntimeError("fail"))

        mock_writer = MagicMock()
        mock_logger = MagicMock()

        results = asyncio.run(_batch_process_days(["2024-01-15"], mock_parser, mock_ai, mock_writer, mock_logger))
        # asyncio.gather with return_exceptions=True puts exception in results
        self.assertIsInstance(results[0], RuntimeError)
        mock_writer.close.assert_called_once()


class TestProcessAll(unittest.TestCase):

    @patch('src.batch_processor.ai_processor_factory')
    @patch('src.batch_processor.writer_factory')
    @patch('src.batch_processor.parser_factory')
    @patch('src.batch_processor.reader_factory')
    @patch('src.batch_processor.asyncio')
    def test_process_all_flow(self, mock_asyncio, mock_reader_factory, mock_parser_factory,
                               mock_writer_factory, mock_ai_factory):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test input file
            input_dir = os.path.join(tmpdir, "input")
            os.makedirs(input_dir)
            open(os.path.join(input_dir, "chat.json"), 'w').close()

            config = {
                'logs': {'level': 'WARNING'},
                'batch': {
                    'input': {'type': 'INSTAGRAM_EXPORT', 'path': input_dir},
                    'output': {'type': 'TXT', 'path': tmpdir}
                }
            }

            # Setup mocks
            mock_reader = MagicMock()
            mock_reader.get_extension.return_value = ".json"
            mock_reader.get_file_list.return_value = [os.path.join(input_dir, "chat.json")]
            mock_reader.read.return_value = {"messages": []}
            mock_reader.standardize_messages.return_value = []
            mock_reader_factory.return_value = mock_reader

            mock_parser = MagicMock()
            mock_parser.get_available_days.return_value = ["2024-01-15"]
            mock_parser_factory.return_value = mock_parser

            mock_writer = MagicMock()
            mock_writer_factory.return_value = mock_writer

            mock_ai = MagicMock()
            mock_ai_factory.return_value = mock_ai

            process_all(config)

            mock_reader_factory.assert_called_once()
            mock_parser_factory.assert_called_once()
            mock_writer_factory.assert_called_once()
            mock_ai_factory.assert_called_once()
            mock_reader.read.assert_called_once()
            mock_reader.standardize_messages.assert_called_once()
            mock_parser.parse.assert_called_once()
            mock_parser.sort_bucket.assert_called_once()


if __name__ == '__main__':
    unittest.main()
