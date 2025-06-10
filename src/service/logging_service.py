import logging.config

from src.dto.enums.log_levels import LogLevel


def get_logger(config: dict, name: str) -> logging.Logger:
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
    logger = logging.getLogger(name)
    return logger
