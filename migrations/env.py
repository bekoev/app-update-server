import asyncio

# from app.config import MainSettings
from app.plugins.postgres.settings import PostgresSettings
from app.entities.base import EntityBase as Base

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection


from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
db_config = PostgresSettings()

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=db_config.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    data_base_url = context.get_tag_argument()
    connectable = create_async_engine(
        data_base_url if data_base_url else db_config.url,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


try:
    loop = asyncio.get_running_loop()
except RuntimeError:  # 'RuntimeError: There is no current event loop...'
    loop = None

if context.is_offline_mode():
    run_migrations_offline()
else:
    if loop and loop.is_running():
        tsk = loop.create_task(run_migrations_online())
    else:
        asyncio.run(run_migrations_online())
