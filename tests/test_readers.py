import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

from src.dto.enums.input_file_type import InputFileType
from src.service.logging_service import LoggingService
from src.service.reader.instagram_export_json_reader import InstagramExportJsonReader
from src.service.reader.whatsapp_txt_reader import WhatsappTxtReader
from src.service.reader.reader_factory import reader_factory


def _logging_service():
    return LoggingService({'logs': {'level': 'WARNING'}})


class TestInstagramExportJsonReader(unittest.TestCase):

    def setUp(self):
        self.system_messages = {
            'user-interactions': {
                'message-like': 'Liked a message',
                'message-reaction': 'Added reaction',
                'call-start': 'Started a call',
            },
            'user-content': {
                'posts-and-reels': '[Shared a reel]',
                'video-uploads': '[Sent a video]',
                'photo-uploads': '[Sent a photo]',
                'audio-messages': '[Sent audio]',
                'call-start': '[Call started]',
                'call-end': '[Call ended]',
            }
        }
        self.reader = InstagramExportJsonReader(self.system_messages, _logging_service())

    def test_standardize_basic_message(self):
        data = {
            "messages": [
                {"sender_name": "Alice", "timestamp_ms": 1700000000000, "content": "Hello!"}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["sender_name"], "Alice")
        self.assertEqual(messages[0]["content"], "Hello!")
        self.assertIsInstance(messages[0]["timestamp"], datetime)
        self.assertIsInstance(messages[0]["token_count"], int)

    def test_standardize_shared_reel(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "share": {"link": "url"}}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "[Shared a reel]")

    def test_standardize_call_duration(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "call_duration": 120}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "[Call ended]")

    def test_standardize_video(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "videos": [{"uri": "video.mp4"}]}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "[Sent a video]")

    def test_standardize_photo(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "photos": [{"uri": "photo.jpg"}]}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "[Sent a photo]")

    def test_standardize_audio(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "audio_files": [{"uri": "audio.mp3"}]}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "[Sent audio]")

    def test_standardize_message_like_returns_empty(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "content": "Liked a message"}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "")

    def test_standardize_message_reaction_returns_empty(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "content": "Added reaction ❤️"}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "")

    def test_standardize_empty_messages(self):
        data = {"messages": []}
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages, [])

    def test_standardize_missing_messages_key(self):
        data = {}
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages, [])

    def test_standardize_multiple_messages(self):
        data = {
            "messages": [
                {"sender_name": "Alice", "timestamp_ms": 1700000000000, "content": "Hi"},
                {"sender_name": "Bob", "timestamp_ms": 1700000001000, "content": "Hey"},
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(len(messages), 2)

    def test_read_json_file(self):
        data = {"messages": [{"sender_name": "A", "timestamp_ms": 1000, "content": "test"}]}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            path = f.name
        try:
            result = self.reader.read(path)
            self.assertEqual(result, data)
        finally:
            os.unlink(path)

    def test_call_start_message(self):
        data = {
            "messages": [
                {"sender_name": "Bob", "timestamp_ms": 1700000000000, "content": "Started a call"}
            ]
        }
        messages = self.reader.standardize_messages(data)
        self.assertEqual(messages[0]["content"], "[Call started]")


class TestWhatsappTxtReader(unittest.TestCase):

    def setUp(self):
        self.reader = WhatsappTxtReader(_logging_service())

    def test_standardize_single_message(self):
        lines = ["15/01/2024, 10:30 - Alice: Hello!\n"]
        messages = self.reader.standardize_messages(lines)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["sender_name"], "Alice")
        self.assertEqual(messages[0]["content"], "Hello!")
        self.assertEqual(messages[0]["timestamp"], datetime(2024, 1, 15, 10, 30))

    def test_standardize_multiple_messages(self):
        lines = [
            "15/01/2024, 10:30 - Alice: Hello!\n",
            "15/01/2024, 10:31 - Bob: Hi there!\n",
        ]
        messages = self.reader.standardize_messages(lines)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["sender_name"], "Alice")
        self.assertEqual(messages[1]["sender_name"], "Bob")

    def test_standardize_multiline_message(self):
        lines = [
            "15/01/2024, 10:30 - Alice: First line\n",
            "Second line\n",
            "15/01/2024, 10:31 - Bob: Reply\n",
        ]
        messages = self.reader.standardize_messages(lines)
        self.assertEqual(len(messages), 2)
        self.assertIn("First line", messages[0]["content"])
        self.assertIn("Second line", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "Reply")

    def test_standardize_empty_lines(self):
        messages = self.reader.standardize_messages([])
        self.assertEqual(messages, [])

    def test_standardize_non_matching_lines_only(self):
        # Non-matching lines get accumulated as continuation content with empty sender
        lines = ["This is not a message\n", "Neither is this\n"]
        messages = self.reader.standardize_messages(lines)
        # The parser accumulates unmatched lines as a single message with empty sender
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["sender_name"], "")

    def test_read_txt_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("15/01/2024, 10:30 - Alice: Hello!\n")
            path = f.name
        try:
            result = self.reader.read(path)
            self.assertEqual(len(result), 1)
            self.assertIn("Alice", result[0])
        finally:
            os.unlink(path)

    def test_token_count_present(self):
        lines = ["15/01/2024, 10:30 - Alice: Hello world!\n"]
        messages = self.reader.standardize_messages(lines)
        self.assertIn("token_count", messages[0])
        self.assertIsInstance(messages[0]["token_count"], int)
        self.assertGreater(messages[0]["token_count"], 0)


class TestReaderGetFileList(unittest.TestCase):

    def test_get_file_list_finds_json_files(self):
        reader = InstagramExportJsonReader({}, _logging_service())
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files
            open(os.path.join(tmpdir, "chat1.json"), 'w').close()
            open(os.path.join(tmpdir, "chat2.json"), 'w').close()
            open(os.path.join(tmpdir, "readme.txt"), 'w').close()

            files = reader.get_file_list(os.fsencode(tmpdir))
            self.assertEqual(len(files), 2)
            self.assertTrue(all(f.endswith('.json') for f in files))

    def test_get_file_list_finds_txt_files(self):
        reader = WhatsappTxtReader(_logging_service())
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "chat.txt"), 'w').close()
            open(os.path.join(tmpdir, "data.json"), 'w').close()

            files = reader.get_file_list(os.fsencode(tmpdir))
            self.assertEqual(len(files), 1)
            self.assertTrue(files[0].endswith('.txt'))

    def test_get_file_list_raises_when_empty(self):
        reader = InstagramExportJsonReader({}, _logging_service())
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                reader.get_file_list(os.fsencode(tmpdir))


class TestReaderFactory(unittest.TestCase):

    def test_instagram_export_returns_correct_reader(self):
        config = {'parsing': {'messages': {}, 'chars-per-token': 4.0}, 'logs': {'level': 'WARNING'}}
        reader = reader_factory(InputFileType.INSTAGRAM_EXPORT, config)
        self.assertIsInstance(reader, InstagramExportJsonReader)

    def test_whatsapp_export_returns_correct_reader(self):
        config = {'parsing': {'messages': {}, 'chars-per-token': 4.0}, 'logs': {'level': 'WARNING'}}
        reader = reader_factory(InputFileType.WHATSAPP_EXPORT, config)
        self.assertIsInstance(reader, WhatsappTxtReader)

    def test_reader_extension(self):
        config = {'parsing': {'messages': {}, 'chars-per-token': 4.0}, 'logs': {'level': 'WARNING'}}
        ig_reader = reader_factory(InputFileType.INSTAGRAM_EXPORT, config)
        wa_reader = reader_factory(InputFileType.WHATSAPP_EXPORT, config)
        self.assertEqual(ig_reader.get_extension(), ".json")
        self.assertEqual(wa_reader.get_extension(), ".txt")

    def test_unsupported_type_raises(self):
        config = {'parsing': {'messages': {}, 'chars-per-token': 4.0}, 'logs': {'level': 'WARNING'}}
        with self.assertRaises(ValueError):
            reader_factory("UNSUPPORTED", config)


if __name__ == '__main__':
    unittest.main()
