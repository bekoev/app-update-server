from functools import lru_cache

from app.core.containers import container


@lru_cache
def get_logger():
    return container.logger()
