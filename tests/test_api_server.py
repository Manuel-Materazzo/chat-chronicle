import unittest
from unittest.mock import patch, MagicMock

from src.api_server import app
from src.controller.summary_controller import set_config, execute_summary_request
from src.dto.enums.input_file_type import InputFileType


class TestSetConfig(unittest.TestCase):

    @patch('src.controller.summary_controller.ai_processor_factory')
    def test_set_config_initializes_globals(self, mock_factory):
        mock_factory.return_value = MagicMock()
        config = {
            'logs': {'level': 'WARNING'},
            'inference-service': {'concurrency-limit': 3},
        }
        set_config(config)

        import src.controller.summary_controller as sc
        self.assertEqual(sc.app_config, config)
        self.assertIsNotNone(sc.logging_service)
        self.assertIsNotNone(sc.ai_processor)
        self.assertIsNotNone(sc.ai_semaphore)


class TestExecuteSummaryRequest(unittest.TestCase):

    @patch('src.controller.summary_controller.ai_processor')
    @patch('src.controller.summary_controller.parser_factory')
    @patch('src.controller.summary_controller.reader_factory')
    def test_execute_summary_request(self, mock_reader_factory, mock_parser_factory, mock_ai):
        from datetime import datetime

        # Setup reader mock
        mock_reader = MagicMock()
        mock_reader.standardize_messages.return_value = [
            {'sender_name': 'Alice', 'timestamp': datetime(2024, 1, 15, 10, 30),
             'content': 'Hello!', 'token_count': 5}
        ]
        mock_reader_factory.return_value = mock_reader

        # Setup parser mock
        mock_parser = MagicMock()
        mock_parser.get_available_days.return_value = ["2024-01-15"]
        mock_parser.get_messages.return_value = [
            {'sender_name': 'Alice', 'timestamp': datetime(2024, 1, 15, 10, 30),
             'content': 'Hello!', 'token_count': 5}
        ]
        mock_parser_factory.return_value = mock_parser

        # Setup AI processor mock - need to patch the module-level variable
        import src.controller.summary_controller as sc
        sc.ai_processor = MagicMock()
        sc.ai_processor.get_summary_sync.return_value = {
            'summary': 'A great day.',
            'ai_chat': [],
            'messages': [],
        }

        config = {'logs': {'level': 'WARNING'}}
        raw_messages = [{"sender_name": "Alice", "timestamp_ms": 1700000000000, "content": "Hello!"}]

        result = execute_summary_request(InputFileType.INSTAGRAM_EXPORT, config, raw_messages)

        self.assertIn("entries", result)
        self.assertEqual(len(result["entries"]), 1)
        self.assertEqual(result["entries"][0]["date"], "2024-01-15")
        self.assertEqual(result["entries"][0]["summary"], "A great day.")

    @patch('src.controller.summary_controller.ai_processor')
    @patch('src.controller.summary_controller.parser_factory')
    @patch('src.controller.summary_controller.reader_factory')
    def test_execute_with_intermediate_steps(self, mock_reader_factory, mock_parser_factory, mock_ai):
        from datetime import datetime

        mock_reader = MagicMock()
        mock_reader.standardize_messages.return_value = []
        mock_reader_factory.return_value = mock_reader

        mock_parser = MagicMock()
        mock_parser.get_available_days.return_value = ["2024-01-15"]
        mock_parser.get_messages.return_value = []
        mock_parser_factory.return_value = mock_parser

        import src.controller.summary_controller as sc
        sc.ai_processor = MagicMock()
        sc.ai_processor.get_summary_sync.return_value = {
            'summary': 'Entry',
            'ai_chat': ['msg'],
            'extra': 'data',
        }

        config = {'output': {'export-intermediate-steps': True}, 'logs': {'level': 'WARNING'}}
        result = execute_summary_request(InputFileType.INSTAGRAM_EXPORT, config, [])
        entry = result["entries"][0]
        self.assertEqual(entry["summary"], "Entry")
        self.assertIn("intermediate_steps", entry)
        self.assertEqual(entry["intermediate_steps"]["extra"], "data")


class TestFlaskEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('src.controller.summary_controller.execute_summary_request')
    @patch('src.controller.summary_controller.ai_semaphore')
    def test_instagram_export_endpoint(self, mock_semaphore, mock_execute):
        mock_semaphore.acquire.return_value = True
        mock_execute.return_value = {
            "entries": [{"date": "2024-01-15", "summary": "A great day."}]
        }

        response = self.client.post('/summarize/instagram-export', json={
            "configs": {},
            "messages": [{"sender_name": "Alice", "timestamp_ms": 1700000000000, "content": "Hi"}]
        })
        self.assertEqual(response.status_code, 200)

    @patch('src.controller.summary_controller.ai_semaphore')
    def test_instagram_export_busy(self, mock_semaphore):
        mock_semaphore.acquire.return_value = False

        response = self.client.post('/summarize/instagram-export', json={
            "configs": {},
            "messages": [{"sender_name": "Alice", "timestamp_ms": 1700000000000, "content": "Hi"}]
        })
        self.assertEqual(response.status_code, 503)

    @patch('src.controller.summary_controller.execute_summary_request')
    @patch('src.controller.summary_controller.ai_semaphore')
    def test_whatsapp_export_endpoint(self, mock_semaphore, mock_execute):
        mock_semaphore.acquire.return_value = True
        mock_execute.return_value = {
            "entries": [{"date": "2024-01-15", "summary": "A great day."}]
        }

        response = self.client.post('/summarize/whatsapp-export', json={
            "configs": {},
            "messages": ["15/01/2024, 10:30 - Alice: Hello!"]
        })
        self.assertEqual(response.status_code, 200)

    @patch('src.controller.summary_controller.ai_semaphore')
    def test_whatsapp_export_busy(self, mock_semaphore):
        mock_semaphore.acquire.return_value = False

        response = self.client.post('/summarize/whatsapp-export', json={
            "configs": {},
            "messages": ["line"]
        })
        self.assertEqual(response.status_code, 503)

    def test_instagram_export_missing_messages(self):
        import src.controller.summary_controller as sc
        sc.ai_semaphore = MagicMock()
        sc.ai_semaphore.acquire.return_value = True

        response = self.client.post('/summarize/instagram-export', json={
            "configs": {}
        })
        self.assertEqual(response.status_code, 422)

    def test_whatsapp_export_missing_messages(self):
        import src.controller.summary_controller as sc
        sc.ai_semaphore = MagicMock()
        sc.ai_semaphore.acquire.return_value = True

        response = self.client.post('/summarize/whatsapp-export', json={
            "configs": {}
        })
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()
