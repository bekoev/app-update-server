from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import wait_for
from logging import Logger
from typing import Any


class Plugin(ABC):
    """Base class for plugins"""

    healthcheck_name: str = "plugin"
    healthcheck_timeout: int = 10000000

    def __init__(self, logger: Logger):
        self.logger = logger

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        raise NotImplementedError

    async def health_check_call(self) -> bool:
        is_passed = False
        try:
            fut = self.health_check()
            if self.healthcheck_timeout:
                await wait_for(fut, timeout=self.healthcheck_timeout)
            else:
                await fut
            is_passed = True

        except TimeoutError:
            self.logger.critical(
                f"Exceeded the timeout of {self.healthcheck_timeout} seconds",
                exc_info=True,
            )
        except Exception:
            # self.logger.critical("Error occurred", exc_info=True)
            pass
        return is_passed
