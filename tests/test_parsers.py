import unittest
from datetime import datetime

from src.dto.enums.input_file_type import InputFileType
from src.service.parser.parser import get_chat_log, get_chat_log_chunked, Parser
from src.service.parser.instagram_export import InstagramExport
from src.service.parser.whatsapp_export import WhatsappExport
from src.service.parser.parser_factory import parser_factory


def _make_message(sender, content, timestamp, token_count=10):
    return {
        'sender_name': sender,
        'timestamp': timestamp,
        'content': content,
        'token_count': token_count,
    }


class TestGetChatLog(unittest.TestCase):

    def test_empty_messages(self):
        result = get_chat_log([])
        self.assertEqual(result, "")

    def test_single_message(self):
        messages = [_make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30))]
        result = get_chat_log(messages)
        self.assertEqual(result, "[10:30] Alice: Hello!\n")

    def test_multiple_messages(self):
        messages = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30)),
            _make_message("Bob", "Hi!", datetime(2024, 1, 15, 10, 31)),
        ]
        result = get_chat_log(messages)
        self.assertIn("[10:30] Alice: Hello!", result)
        self.assertIn("[10:31] Bob: Hi!", result)

    def test_midnight_formatting(self):
        messages = [_make_message("Alice", "Late night", datetime(2024, 1, 15, 0, 5))]
        result = get_chat_log(messages)
        self.assertIn("[00:05]", result)


class TestGetChatLogChunked(unittest.TestCase):

    def test_empty_messages(self):
        result = get_chat_log_chunked([], 100)
        self.assertEqual(result, [])

    def test_few_messages_single_chunk(self):
        messages = [
            _make_message("Alice", "Hi", datetime(2024, 1, 15, 10, i), token_count=5)
            for i in range(10)
        ]
        result = get_chat_log_chunked(messages, 10000)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["messages_count"], 10)

    def test_many_messages_multiple_chunks(self):
        messages = [
            _make_message("Alice", "Message " * 20, datetime(2024, 1, 15, 10, i % 60), token_count=100)
            for i in range(20)
        ]
        result = get_chat_log_chunked(messages, 200)
        self.assertGreater(len(result), 1)

    def test_chunk_has_timestamps(self):
        messages = [
            _make_message("Alice", "Hi", datetime(2024, 1, 15, 10, 0), token_count=5),
            _make_message("Bob", "Hey", datetime(2024, 1, 15, 10, 5), token_count=5),
            _make_message("Alice", "What's up", datetime(2024, 1, 15, 10, 10), token_count=5),
            _make_message("Bob", "nm", datetime(2024, 1, 15, 10, 15), token_count=5),
        ]
        result = get_chat_log_chunked(messages, 10000)
        if len(result) > 0:
            chunk = result[0]
            self.assertIsNotNone(chunk["start_timestamp"])
            self.assertIsNotNone(chunk["end_timestamp"])
            self.assertGreater(chunk["messages_count"], 0)
            self.assertGreater(len(chunk["content"]), 0)

    def test_too_few_messages_discarded(self):
        messages = [
            _make_message("Alice", "Hi", datetime(2024, 1, 15, 10, 0), token_count=5),
            _make_message("Bob", "Hey", datetime(2024, 1, 15, 10, 1), token_count=5),
        ]
        result = get_chat_log_chunked(messages, 10000)
        # Only 2 messages, below the threshold of 3 for the last chunk
        self.assertEqual(len(result), 0)


class TestParserHandleNewlines(unittest.TestCase):

    def setUp(self):
        self.parser = InstagramExport()

    def test_colon_newline(self):
        result = self.parser.handle_newlines("hello:\nworld")
        self.assertEqual(result, "hello: world")

    def test_semicolon_newline(self):
        result = self.parser.handle_newlines("hello;\nworld")
        self.assertEqual(result, "hello; world")

    def test_comma_newline(self):
        result = self.parser.handle_newlines("hello,\nworld")
        self.assertEqual(result, "hello, world")

    def test_period_newline(self):
        result = self.parser.handle_newlines("hello.\nworld")
        self.assertEqual(result, "hello. world")

    def test_bare_newline(self):
        result = self.parser.handle_newlines("hello\nworld")
        self.assertEqual(result, "hello. world")

    def test_no_newline(self):
        result = self.parser.handle_newlines("hello world")
        self.assertEqual(result, "hello world")


class TestInstagramExportParser(unittest.TestCase):

    def setUp(self):
        self.parser = InstagramExport()

    def test_parse_basic_message(self):
        messages = [_make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        days = self.parser.get_available_days()
        self.assertEqual(len(days), 1)
        self.assertEqual(days[0], "2024-01-15")

    def test_parse_groups_by_day(self):
        messages = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30)),
            _make_message("Bob", "Hi!", datetime(2024, 1, 15, 11, 0)),
            _make_message("Alice", "Next day!", datetime(2024, 1, 16, 9, 0)),
        ]
        self.parser.parse(messages)
        days = self.parser.get_available_days()
        self.assertEqual(len(days), 2)

    def test_parse_empty_content_skipped(self):
        messages = [_make_message("Alice", "", datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        days = self.parser.get_available_days()
        self.assertEqual(len(days), 0)

    def test_parse_fixes_unicode(self):
        # Instagram double-encodes UTF-8 as latin1
        original = "Ciao à tutti"
        double_encoded = original.encode('utf8').decode('latin1')
        messages = [_make_message("Alice", double_encoded, datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        day_messages = self.parser.get_messages("2024-01-15")
        self.assertEqual(day_messages[0]["content"], "Ciao à tutti")

    def test_parse_removes_unicode_from_sender(self):
        messages = [_make_message("Alicé 🎉", "Hello!", datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        day_messages = self.parser.get_messages("2024-01-15")
        # Non-ASCII chars removed
        self.assertNotIn("🎉", day_messages[0]["sender_name"])

    def test_get_messages_returns_empty_for_unknown_date(self):
        self.assertEqual(self.parser.get_messages("1999-01-01"), [])

    def test_get_messages_grouped(self):
        messages = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30)),
            _make_message("Bob", "Bye!", datetime(2024, 1, 16, 10, 30)),
        ]
        self.parser.parse(messages)
        grouped = self.parser.get_messages_grouped()
        self.assertIn("2024-01-15", grouped)
        self.assertIn("2024-01-16", grouped)

    def test_ignore_chat_before(self):
        parser = InstagramExport(ignore_chat_enabled=True, ignore_chat_before="2024-01-15",
                                 ignore_chat_after="2024-12-31")
        messages = [
            _make_message("Alice", "Old message", datetime(2024, 1, 14, 10, 30)),
            _make_message("Alice", "New message", datetime(2024, 1, 15, 10, 30)),
        ]
        parser.parse(messages)
        days = parser.get_available_days()
        self.assertEqual(len(days), 1)
        self.assertEqual(days[0], "2024-01-15")

    def test_ignore_chat_after(self):
        parser = InstagramExport(ignore_chat_enabled=True, ignore_chat_before="2024-01-01",
                                 ignore_chat_after="2024-01-15")
        messages = [
            _make_message("Alice", "Valid", datetime(2024, 1, 15, 10, 30)),
            _make_message("Alice", "Too late", datetime(2024, 1, 16, 10, 30)),
        ]
        parser.parse(messages)
        days = parser.get_available_days()
        self.assertEqual(len(days), 1)
        self.assertEqual(days[0], "2024-01-15")


class TestWhatsappExportParser(unittest.TestCase):

    def setUp(self):
        self.parser = WhatsappExport()

    def test_parse_basic_message(self):
        messages = [_make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        days = self.parser.get_available_days()
        self.assertEqual(len(days), 1)
        self.assertEqual(days[0], "2024-01-15")

    def test_parse_groups_by_day(self):
        messages = [
            _make_message("Alice", "Hello!", datetime(2024, 1, 15, 10, 30)),
            _make_message("Alice", "Next day!", datetime(2024, 1, 16, 9, 0)),
        ]
        self.parser.parse(messages)
        self.assertEqual(len(self.parser.get_available_days()), 2)

    def test_parse_empty_content_skipped(self):
        messages = [_make_message("Alice", "", datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        self.assertEqual(len(self.parser.get_available_days()), 0)

    def test_parse_handles_newlines(self):
        messages = [_make_message("Alice", "Hello\nWorld", datetime(2024, 1, 15, 10, 30))]
        self.parser.parse(messages)
        day_messages = self.parser.get_messages("2024-01-15")
        self.assertNotIn("\n", day_messages[0]["content"])

    def test_ignore_chat_enabled(self):
        parser = WhatsappExport(ignore_chat_enabled=True, ignore_chat_before="2024-01-15",
                                ignore_chat_after="2024-01-15")
        messages = [
            _make_message("Alice", "Old", datetime(2024, 1, 14, 10, 30)),
            _make_message("Alice", "Valid", datetime(2024, 1, 15, 10, 30)),
            _make_message("Alice", "Future", datetime(2024, 1, 16, 10, 30)),
        ]
        parser.parse(messages)
        self.assertEqual(len(parser.get_available_days()), 1)


class TestParserSortBucket(unittest.TestCase):

    def test_sort_bucket_orders_messages(self):
        parser = InstagramExport()
        messages = [
            _make_message("Alice", "Second", datetime(2024, 1, 15, 11, 0)),
            _make_message("Alice", "First", datetime(2024, 1, 15, 10, 0)),
        ]
        parser.parse(messages)
        parser.sort_bucket()
        day_messages = parser.get_messages("2024-01-15")
        self.assertEqual(day_messages[0]["content"], "First")
        self.assertEqual(day_messages[1]["content"], "Second")


class TestParserExtractChatSessions(unittest.TestCase):

    def test_no_carryover_when_messages_after_sleep_window(self):
        parser = InstagramExport(chat_sessions_enabled=True, sleep_window_start=2, sleep_window_end=9)
        messages = [
            _make_message("Alice", "Morning", datetime(2024, 1, 15, 10, 0)),
            _make_message("Bob", "Hello", datetime(2024, 1, 15, 11, 0)),
        ]
        result = parser.extract_chat_sessions(messages)
        self.assertEqual(len(result), 2)

    def test_empty_messages(self):
        parser = InstagramExport(chat_sessions_enabled=True)
        result = parser.extract_chat_sessions([])
        self.assertEqual(result, [])

    def test_carryover_with_gap_in_sleep_window(self):
        parser = InstagramExport(chat_sessions_enabled=True, sleep_window_start=2, sleep_window_end=9)
        messages = [
            _make_message("Alice", "Late night", datetime(2024, 1, 15, 1, 0)),
            # 5-hour gap in sleep window
            _make_message("Bob", "Morning", datetime(2024, 1, 15, 6, 0)),
            _make_message("Alice", "Afternoon", datetime(2024, 1, 15, 14, 0)),
        ]
        result = parser.extract_chat_sessions(messages)
        # First message should be carried over, remaining should be returned
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["content"], "Morning")


class TestParserFactory(unittest.TestCase):

    def test_instagram_export(self):
        config = {'parsing': {'chat-sessions': {'enabled': True}, 'ignore-chat': {'enabled': False}}}
        parser = parser_factory(InputFileType.INSTAGRAM_EXPORT, config)
        self.assertIsInstance(parser, InstagramExport)

    def test_whatsapp_export(self):
        config = {'parsing': {'chat-sessions': {'enabled': True}, 'ignore-chat': {'enabled': False}}}
        parser = parser_factory(InputFileType.WHATSAPP_EXPORT, config)
        self.assertIsInstance(parser, WhatsappExport)

    def test_unsupported_type_raises(self):
        config = {'parsing': {'chat-sessions': {'enabled': True}, 'ignore-chat': {'enabled': False}}}
        with self.assertRaises(ValueError):
            parser_factory("UNSUPPORTED", config)

    def test_factory_passes_config(self):
        config = {
            'parsing': {
                'chat-sessions': {
                    'enabled': True,
                    'sleep-window-start-hour': 3,
                    'sleep-window-end-hour': 8,
                },
                'ignore-chat': {'enabled': False}
            }
        }
        parser = parser_factory(InputFileType.INSTAGRAM_EXPORT, config)
        self.assertTrue(parser.chat_sessions_enabled)


if __name__ == '__main__':
    unittest.main()
