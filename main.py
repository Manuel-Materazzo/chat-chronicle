import sys
from src.batch_processor import process_all
from src.api_server import start_server
from src.dto.enums.run_mode import RunMode
from src.service.config_service import get_configs
from src.service.logging_service import LoggingService

# read configs
config = get_configs('./config.yml')

logging_service = LoggingService(config)
logger = logging_service.get_logger(__name__)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else RunMode.BATCH

    if mode == RunMode.BATCH:
        process_all(config)
    elif mode == RunMode.API:
        start_server(config)
    else:
        message = f"Application run mode not supported, please choose one of the following: {[e for e in RunMode]}"
        raise ValueError(message)
