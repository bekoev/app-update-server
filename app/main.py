import uvicorn

from app.api.server import create_app
from app.core.containers import container

app = create_app(container)


def main() -> None:
    config = container.config()
    container.logger().info(f"-- Start {config.app.name} version 0.0.1 --")
    uvicorn.run(
        "app.main:app",
        host=config.app.host,
        port=config.app.port,
        reload=config.app.reloader,
        log_config=container.logging_config().get_config_dict(),
    )
