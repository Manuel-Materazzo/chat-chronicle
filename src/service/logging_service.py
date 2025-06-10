import logging.config

from src.dto.enums.log_levels import LogLevel


class LoggingService:

    def __init__(self, config: dict) -> None:
        level = config.get('logs', {}).get('level', LogLevel.INFO)
        LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(message)s",
                }
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                }
            },
            "loggers": {"": {"handlers": ["stdout"], "level": str(level)}},
        }

        logging.config.dictConfig(LOGGING)

    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)
