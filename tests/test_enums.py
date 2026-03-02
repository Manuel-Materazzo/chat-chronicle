import unittest

from src.dto.enums.input_file_type import InputFileType
from src.dto.enums.log_levels import LogLevel
from src.dto.enums.run_mode import RunMode
from src.dto.enums.summarization_strategy import SummarizationStrategy
from src.dto.enums.writer_type import WriterType


class TestInputFileType(unittest.TestCase):

    def test_members(self):
        self.assertEqual(InputFileType.INSTAGRAM_EXPORT, "INSTAGRAM_EXPORT")
        self.assertEqual(InputFileType.WHATSAPP_EXPORT, "WHATSAPP_EXPORT")

    def test_member_count(self):
        self.assertEqual(len(InputFileType), 2)

    def test_string_comparison(self):
        self.assertEqual(InputFileType.INSTAGRAM_EXPORT, "INSTAGRAM_EXPORT")
        self.assertIsInstance(InputFileType.INSTAGRAM_EXPORT, str)

    def test_iteration(self):
        members = list(InputFileType)
        self.assertIn(InputFileType.INSTAGRAM_EXPORT, members)
        self.assertIn(InputFileType.WHATSAPP_EXPORT, members)


class TestLogLevel(unittest.TestCase):

    def test_members(self):
        self.assertEqual(LogLevel.DEBUG, "DEBUG")
        self.assertEqual(LogLevel.INFO, "INFO")
        self.assertEqual(LogLevel.WARNING, "WARNING")
        self.assertEqual(LogLevel.ERROR, "ERROR")
        self.assertEqual(LogLevel.CRITICAL, "CRITICAL")

    def test_member_count(self):
        self.assertEqual(len(LogLevel), 5)

    def test_string_comparison(self):
        self.assertEqual(LogLevel.INFO, "INFO")
        self.assertIsInstance(LogLevel.INFO, str)


class TestRunMode(unittest.TestCase):

    def test_members(self):
        self.assertEqual(RunMode.BATCH, "batch")
        self.assertEqual(RunMode.API, "api")

    def test_member_count(self):
        self.assertEqual(len(RunMode), 2)

    def test_string_comparison(self):
        self.assertEqual(RunMode.BATCH, "batch")
        self.assertNotEqual(RunMode.BATCH, "BATCH")


class TestSummarizationStrategy(unittest.TestCase):

    def test_members(self):
        self.assertEqual(SummarizationStrategy.LINEAR, "LINEAR")
        self.assertEqual(SummarizationStrategy.MAP_REDUCE, "MAP_REDUCE")

    def test_member_count(self):
        self.assertEqual(len(SummarizationStrategy), 2)


class TestWriterType(unittest.TestCase):

    def test_members(self):
        self.assertEqual(WriterType.TXT, "TXT")
        self.assertEqual(WriterType.NDJSON, "NDJSON")
        self.assertEqual(WriterType.JSON, "JSON")

    def test_member_count(self):
        self.assertEqual(len(WriterType), 3)


if __name__ == '__main__':
    unittest.main()
