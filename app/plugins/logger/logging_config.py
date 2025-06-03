from __future__ import annotations

import logging
import sys
from collections.abc import Generator
from logging.config import dictConfig
from logging.handlers import QueueListener
from pathlib import Path
from queue import Queue

from app.settings import MainSettings


def init_logging(config: LoggingConfiguration) -> Generator[logging.Logger, None, None]:
    config.apply_configuration()
    for listener in config.get_logging_listeners():
        listener.start()

    yield logging.getLogger(config.logger_name)

    for listener in config.get_logging_listeners():
        listener.stop()


class LoggingConfiguration:
    """The class to handle logging configuration for the whole application."""

    def __init__(self, app_settings: MainSettings) -> None:
        self._app_settings = app_settings
        self.logger_name = self._app_settings.app.name.replace("-", "_")
        self._logging_queue: Queue = Queue(-1)
        self._logging_listener: QueueListener | None = None

    def apply_configuration(self) -> None:
        """Apply the configuration to standard logging facility."""

        dictConfig(self.get_config_dict())

        # Setup handlers that may block, as per
        #   https://docs.python.org/3/howto/logging-cookbook.html#dealing-with-handlers-that-block
        file_handler = logging.getHandlerByName("file_handler")
        if file_handler is not None:
            listener_handlers = (file_handler,)
            self._logging_listener = QueueListener(
                self._logging_queue, *listener_handlers
            )

    def get_logging_listeners(self) -> list[QueueListener]:
        """Get listeners that require starting and stopping."""
        return [self._logging_listener] if self._logging_listener else []

    def get_config_dict(self) -> dict:
        logging_lvl = self._app_settings.logger.level
        use_dev_logger = self._app_settings.logger.developer_logger
        console_logger = "console_loguru" if use_dev_logger else "console_json"

        config = {
            "version": 1,
            "disable_existing_loggers": True,
            #
            "loggers": {
                self.logger_name: {
                    "level": logging_lvl,
                    "propagate": False,
                    "handlers": [console_logger, "queue_handler"],
                },
                "uvicorn": {
                    "level": logging_lvl,
                    "propagate": False,
                    "handlers": [console_logger, "queue_handler"],
                },
                "uvicorn.access": {
                    "level": logging_lvl,
                    "propagate": False,
                    "handlers": [console_logger, "queue_handler"],
                },
                "uvicorn.errors": {
                    "level": logging_lvl,
                    "propagate": False,
                    "handlers": [console_logger, "queue_handler"],
                },
            },
            #
            "handlers": {
                "console_loguru": {
                    "class": "app.plugins.logger.handlers.loguruHandler.LoguruHandler",
                },
                "console_json": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "json_formatter",
                },
                "queue_handler": {
                    "class": "logging.handlers.QueueHandler",
                    "queue": self._logging_queue,
                },
                "file_handler": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": (
                        Path(self._app_settings.logger.file_storage_path) / "app.log"
                    ),
                    "maxBytes": self._app_settings.logger.file_max_size,
                    "backupCount": self._app_settings.logger.file_backup_count,
                    "formatter": "plain",
                },
            },
            #
            "formatters": {
                "json_formatter": {
                    "()": "app.plugins.logger.utils.jsonFormatter.JsonFormatter",
                },
                "plain": {
                    "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
        }

        return config
