import logging
import sys

import loguru

loguru_format = (
    "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss}</green> "
    "- <level>{message}</level>"
)
loguru_logger = loguru.logger


class LoguruHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET) -> None:
        super().__init__(level)
        loguru_logger.remove()
        loguru_logger.add(sys.stdout, format=loguru_format, level=level)

    def emit(self, record):
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
