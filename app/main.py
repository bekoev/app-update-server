import uvicorn
from loguru import logger

from app.api.server import create_app
from app.core.containers import container

app = create_app(container)


def main() -> None:
    config = container.config()
    logger.info(f"-- Start {config.app.name} version 0.0.1 --")
    uvicorn.run(
        "app.main:app",
        host=config.app.host,
        port=config.app.port,
        reload=config.app.reloader,
    )
