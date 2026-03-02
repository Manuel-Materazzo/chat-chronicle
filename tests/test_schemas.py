import unittest
from datetime import datetime

from marshmallow import ValidationError

from src.dto.schemas.message_schema import MessageSchema
from src.dto.schemas.instagram_export_message_schema import InstagramExportMessageSchema
from src.dto.schemas.instagram_export_request_schema import InstagramExportRequestSchema
from src.dto.schemas.whatsapp_export_request_schema import WhatsappExportRequestSchema
from src.dto.schemas.chat_chronicle_request_schema import ChatChronicleRequestSchema
from src.dto.schemas.summary_schema import SummarySchema
from src.dto.schemas.summary_response_schema import SummaryResponseSchema


class TestMessageSchema(unittest.TestCase):

    def setUp(self):
        self.schema = MessageSchema()

    def test_valid_data(self):
        data = {
            "sender_name": "Alice",
            "timestamp": "2024-01-15T10:30:00",
            "content": "Hello!"
        }
        result = self.schema.load(data)
        self.assertEqual(result["sender_name"], "Alice")
        self.assertEqual(result["content"], "Hello!")
        self.assertIsInstance(result["timestamp"], datetime)

    def test_missing_sender_name(self):
        data = {"timestamp": "2024-01-15T10:30:00", "content": "Hello!"}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("sender_name", ctx.exception.messages)

    def test_missing_content(self):
        data = {"sender_name": "Alice", "timestamp": "2024-01-15T10:30:00"}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("content", ctx.exception.messages)

    def test_missing_timestamp(self):
        data = {"sender_name": "Alice", "content": "Hello!"}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("timestamp", ctx.exception.messages)


class TestInstagramExportMessageSchema(unittest.TestCase):

    def setUp(self):
        self.schema = InstagramExportMessageSchema()

    def test_valid_minimal_data(self):
        data = {"sender_name": "Bob", "timestamp_ms": 1700000000000}
        result = self.schema.load(data)
        self.assertEqual(result["sender_name"], "Bob")
        self.assertEqual(result["timestamp_ms"], 1700000000000)

    def test_valid_full_data(self):
        data = {
            "sender_name": "Bob",
            "timestamp_ms": 1700000000000,
            "content": "Hi there",
            "call_duration": 120,
            "reactions": [{"emoji": "❤️"}],
            "share": {"link": "https://example.com"},
            "videos": [],
            "audio_files": [],
            "photos": [],
            "is_geoblocked_for_viewer": False,
            "is_unsent_image_by_messenger_kid_parent": False,
        }
        result = self.schema.load(data)
        self.assertEqual(result["sender_name"], "Bob")
        self.assertEqual(result["content"], "Hi there")
        self.assertEqual(result["call_duration"], 120)

    def test_optional_fields_omitted(self):
        data = {"sender_name": "Bob", "timestamp_ms": 1700000000000}
        result = self.schema.load(data)
        self.assertNotIn("content", result)
        self.assertNotIn("call_duration", result)

    def test_missing_sender_name(self):
        data = {"timestamp_ms": 1700000000000}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("sender_name", ctx.exception.messages)

    def test_missing_timestamp_ms(self):
        data = {"sender_name": "Bob"}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("timestamp_ms", ctx.exception.messages)


class TestInstagramExportRequestSchema(unittest.TestCase):

    def setUp(self):
        self.schema = InstagramExportRequestSchema()

    def test_valid_data(self):
        data = {
            "configs": {"key": "value"},
            "messages": [{"sender_name": "Bob", "timestamp_ms": 1700000000000}]
        }
        result = self.schema.load(data)
        self.assertEqual(len(result["messages"]), 1)

    def test_missing_messages(self):
        data = {"configs": {}}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("messages", ctx.exception.messages)

    def test_empty_messages(self):
        data = {"configs": {}, "messages": []}
        result = self.schema.load(data)
        self.assertEqual(result["messages"], [])


class TestWhatsappExportRequestSchema(unittest.TestCase):

    def setUp(self):
        self.schema = WhatsappExportRequestSchema()

    def test_valid_data(self):
        data = {
            "configs": {},
            "messages": ["line1", "line2"]
        }
        result = self.schema.load(data)
        self.assertEqual(result["messages"], ["line1", "line2"])

    def test_missing_messages(self):
        data = {"configs": {}}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("messages", ctx.exception.messages)


class TestChatChronicleRequestSchema(unittest.TestCase):

    def setUp(self):
        self.schema = ChatChronicleRequestSchema()

    def test_valid_data(self):
        data = {
            "configs": {},
            "messages": [
                {"sender_name": "Alice", "timestamp": "2024-01-15T10:30:00", "content": "Hello!"}
            ]
        }
        result = self.schema.load(data)
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["sender_name"], "Alice")

    def test_missing_messages(self):
        data = {"configs": {}}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("messages", ctx.exception.messages)


class TestSummarySchema(unittest.TestCase):

    def setUp(self):
        self.schema = SummarySchema()

    def test_valid_data(self):
        data = {"date": "2024-01-15", "summary": "A great day."}
        result = self.schema.load(data)
        self.assertEqual(result["date"], "2024-01-15")
        self.assertEqual(result["summary"], "A great day.")

    def test_with_optional_chat(self):
        data = {"date": "2024-01-15", "summary": "A great day.", "chat": "Alice: Hi"}
        result = self.schema.load(data)
        self.assertEqual(result["chat"], "Alice: Hi")

    def test_missing_date(self):
        data = {"summary": "A great day."}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("date", ctx.exception.messages)

    def test_missing_summary(self):
        data = {"date": "2024-01-15"}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("summary", ctx.exception.messages)


class TestSummaryResponseSchema(unittest.TestCase):

    def setUp(self):
        self.schema = SummaryResponseSchema()

    def test_valid_data(self):
        data = {
            "entries": [
                {"date": "2024-01-15", "summary": "A great day."}
            ]
        }
        result = self.schema.load(data)
        self.assertEqual(len(result["entries"]), 1)

    def test_missing_entries(self):
        data = {}
        with self.assertRaises(ValidationError) as ctx:
            self.schema.load(data)
        self.assertIn("entries", ctx.exception.messages)

    def test_empty_entries(self):
        data = {"entries": []}
        result = self.schema.load(data)
        self.assertEqual(result["entries"], [])


if __name__ == '__main__':
    unittest.main()
