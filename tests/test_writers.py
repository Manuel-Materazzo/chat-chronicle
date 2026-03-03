import json
import os
import tempfile
import unittest

from src.dto.enums.writer_type import WriterType
from src.service.writer.txt_writer import TxtWriter
from src.service.writer.json_writer import JsonWriter
from src.service.writer.ndjson_writer import NdJsonWriter
from src.service.writer.writer_factory import writer_factory


class TestTxtWriter(unittest.TestCase):

    def test_write_single_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TxtWriter(tmpdir, single_file=True)
            writer.write("2024-01-15", {"summary": "A great day."})
            writer.close()

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1)
            self.assertTrue(files[0].endswith("_full-chronicle.txt"))

            with open(os.path.join(tmpdir, files[0]), encoding='utf-8') as f:
                content = f.read()
            self.assertIn("[2024-01-15]", content)
            self.assertIn("A great day.", content)

    def test_write_multiple_days_single_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TxtWriter(tmpdir, single_file=True)
            writer.write("2024-01-15", {"summary": "Day one."})
            writer.write("2024-01-16", {"summary": "Day two."})
            writer.close()

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1)

            with open(os.path.join(tmpdir, files[0]), encoding='utf-8') as f:
                content = f.read()
            self.assertIn("[2024-01-15]", content)
            self.assertIn("[2024-01-16]", content)

    def test_write_separate_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TxtWriter(tmpdir, single_file=False)
            writer.write("2024-01-15", {"summary": "Day one."})
            writer.write("2024-01-16", {"summary": "Day two."})
            writer.close()

            files = sorted(os.listdir(tmpdir))
            self.assertEqual(len(files), 2)
            self.assertIn("2024-01-15_chronicle.txt", files)
            self.assertIn("2024-01-16_chronicle.txt", files)

    def test_write_with_intermediate_steps(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TxtWriter(tmpdir, single_file=False, export_intermediate_steps=True)
            from datetime import datetime
            summary_state = {
                "summary": "A great day.",
                "ai_chat": ["msg1"],
                "messages": [
                    {"sender_name": "Alice", "timestamp": datetime(2024, 1, 15, 10, 30),
                     "content": "Hi", "token_count": 5}
                ],
                "extra_step": "some data"
            }
            writer.write("2024-01-15", summary_state)
            writer.close()

            with open(os.path.join(tmpdir, "2024-01-15_chronicle.txt"), encoding='utf-8') as f:
                content = f.read()
            self.assertIn("A great day.", content)
            self.assertIn("Chat History:", content)
            self.assertIn("extra_step:", content)


class TestJsonWriter(unittest.TestCase):

    def test_write_single_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = JsonWriter(tmpdir, single_file=True)
            writer.write("2024-01-15", {"summary": "A great day."})
            writer.close()

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1)

            with open(os.path.join(tmpdir, files[0]), encoding='utf-8') as f:
                content = f.read()
            data = json.loads(content)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["date"], "2024-01-15")
            self.assertEqual(data[0]["summary"], "A great day.")

    def test_write_multiple_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = JsonWriter(tmpdir, single_file=True)
            writer.write("2024-01-15", {"summary": "Day one."})
            writer.write("2024-01-16", {"summary": "Day two."})
            writer.close()

            files = os.listdir(tmpdir)
            with open(os.path.join(tmpdir, files[0]), encoding='utf-8') as f:
                data = json.loads(f.read())
            self.assertEqual(len(data), 2)

    def test_write_separate_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = JsonWriter(tmpdir, single_file=False)
            writer.write("2024-01-15", {"summary": "Day one."})
            writer.close()

            files = os.listdir(tmpdir)
            # separate mode writes per-date files
            found = [f for f in files if "2024-01-15" in f]
            self.assertGreater(len(found), 0)


class TestNdJsonWriter(unittest.TestCase):

    def test_write_single_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = NdJsonWriter(tmpdir, single_file=True)
            writer.write("2024-01-15", {"summary": "A great day."})
            writer.close()

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1)

            with open(os.path.join(tmpdir, files[0]), encoding='utf-8') as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(entry["date"], "2024-01-15")
            self.assertEqual(entry["summary"], "A great day.")

    def test_write_multiple_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = NdJsonWriter(tmpdir, single_file=True)
            writer.write("2024-01-15", {"summary": "Day one."})
            writer.write("2024-01-16", {"summary": "Day two."})
            writer.close()

            files = os.listdir(tmpdir)
            with open(os.path.join(tmpdir, files[0]), encoding='utf-8') as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["date"], "2024-01-15")
            self.assertEqual(json.loads(lines[1])["date"], "2024-01-16")

    def test_write_separate_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = NdJsonWriter(tmpdir, single_file=False)
            writer.write("2024-01-15", {"summary": "Day one."})
            writer.write("2024-01-16", {"summary": "Day two."})
            writer.close()

            files = sorted(os.listdir(tmpdir))
            self.assertEqual(len(files), 2)
            self.assertIn("2024-01-15_chronicle.json", files)
            self.assertIn("2024-01-16_chronicle.json", files)

            with open(os.path.join(tmpdir, "2024-01-15_chronicle.json"), encoding='utf-8') as f:
                entry = json.loads(f.readline())
            self.assertEqual(entry["date"], "2024-01-15")
            self.assertEqual(entry["summary"], "Day one.")


class TestWriterFactory(unittest.TestCase):

    def test_txt_writer(self):
        config = {
            'batch': {
                'output': {'type': WriterType.TXT, 'path': './', 'merge-to-one-file': True,
                           'export-intermediate-steps': False}
            }
        }
        writer = writer_factory(config)
        self.assertIsInstance(writer, TxtWriter)

    def test_json_writer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'batch': {
                    'output': {'type': WriterType.JSON, 'path': tmpdir, 'merge-to-one-file': True,
                               'export-intermediate-steps': False}
                }
            }
            writer = writer_factory(config)
            self.assertIsInstance(writer, JsonWriter)
            writer.close()

    def test_ndjson_writer(self):
        config = {
            'batch': {
                'output': {'type': WriterType.NDJSON, 'path': './', 'merge-to-one-file': True,
                           'export-intermediate-steps': False}
            }
        }
        writer = writer_factory(config)
        self.assertIsInstance(writer, NdJsonWriter)

    def test_unsupported_type_raises(self):
        config = {
            'batch': {
                'output': {'type': 'UNSUPPORTED', 'path': './', 'merge-to-one-file': True,
                           'export-intermediate-steps': False}
            }
        }
        with self.assertRaises(ValueError):
            writer_factory(config)

    def test_default_config(self):
        config = {}
        writer = writer_factory(config)
        self.assertIsInstance(writer, TxtWriter)


if __name__ == '__main__':
    unittest.main()
