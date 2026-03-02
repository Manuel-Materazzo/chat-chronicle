import logging
import unittest

from src.service.logging_service import LoggingService


class TestLoggingService(unittest.TestCase):

    def test_init_with_default_level(self):
        config = {'logs': {'level': 'INFO'}}
        service = LoggingService(config)
        logger = service.get_logger("test")
        self.assertIsInstance(logger, logging.Logger)

    def test_init_with_debug_level(self):
        config = {'logs': {'level': 'DEBUG'}}
        service = LoggingService(config)
        logger = service.get_logger("test_debug")
        self.assertIsInstance(logger, logging.Logger)

    def test_init_with_empty_config(self):
        config = {}
        service = LoggingService(config)
        logger = service.get_logger("test_empty")
        self.assertIsInstance(logger, logging.Logger)

    def test_get_logger_returns_named_logger(self):
        config = {'logs': {'level': 'INFO'}}
        service = LoggingService(config)
        logger = service.get_logger("my_module")
        self.assertEqual(logger.name, "my_module")

    def test_different_names_return_different_loggers(self):
        config = {'logs': {'level': 'INFO'}}
        service = LoggingService(config)
        logger1 = service.get_logger("module_a")
        logger2 = service.get_logger("module_b")
        self.assertNotEqual(logger1.name, logger2.name)


if __name__ == '__main__':
    unittest.main()
