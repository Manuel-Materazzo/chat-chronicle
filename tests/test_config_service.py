import os
import tempfile
import unittest

from src.service.config_service import get_configs, str_presenter, config as module_config


class TestGetConfigs(unittest.TestCase):

    def setUp(self):
        # Reset the global config between tests
        import src.service.config_service as cs
        cs.config = dict()

    def test_creates_default_config_when_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config_test.yml")
            self.assertFalse(os.path.isfile(config_path))

            config = get_configs(config_path)

            self.assertTrue(os.path.isfile(config_path))
            self.assertIn('logs', config)
            self.assertIn('batch', config)
            self.assertIn('parsing', config)
            self.assertIn('inference-service', config)
            self.assertIn('summarization', config)

    def test_default_config_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config_test.yml")
            config = get_configs(config_path)

            # batch input
            self.assertEqual(config['batch']['input']['type'], 'INSTAGRAM_EXPORT')
            self.assertEqual(config['batch']['input']['path'], './input/')

            # batch output
            self.assertEqual(config['batch']['output']['type'], 'TXT')
            self.assertTrue(config['batch']['output']['merge-to-one-file'])
            self.assertFalse(config['batch']['output']['export-intermediate-steps'])

            # logs
            self.assertEqual(config['logs']['level'], 'INFO')

            # parsing
            self.assertEqual(config['parsing']['chars-per-token'], 4.0)
            self.assertEqual(config['parsing']['token-per-chunk'], 4000)

    def test_loads_existing_config_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config_test.yml")
            # Write a minimal valid config
            with open(config_path, 'w') as f:
                f.write("logs:\n  level: DEBUG\nbatch:\n  input:\n    type: WHATSAPP_EXPORT\n")

            config = get_configs(config_path)
            self.assertEqual(config['logs']['level'], 'DEBUG')
            self.assertEqual(config['batch']['input']['type'], 'WHATSAPP_EXPORT')

    def test_caching_returns_same_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config_test.yml")
            config1 = get_configs(config_path)

            # Reset to allow re-read but ensure the cache check works
            import src.service.config_service as cs
            # config is already set with 'logs' key, so second call should return cached
            config2 = get_configs(config_path)
            self.assertEqual(config1, config2)


class TestStrPresenter(unittest.TestCase):

    def test_single_line_string(self):
        from yaml import SafeDumper
        dumper = SafeDumper("")
        result = str_presenter(dumper, "hello world")
        self.assertEqual(result.value, "hello world")

    def test_multiline_string(self):
        from yaml import SafeDumper
        dumper = SafeDumper("")
        result = str_presenter(dumper, "line1\nline2\nline3")
        self.assertEqual(result.style, '|')
        self.assertIn("line1", result.value)
        self.assertIn("line2", result.value)


if __name__ == '__main__':
    unittest.main()
