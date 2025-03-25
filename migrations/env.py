import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your database models and Base metadata
from app.database import Base  # Import Base from your project
from app.users.models import User  # Import your models

# Load Alembic configuration
config = context.config

# Load logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for auto-generation
target_metadata = Base.metadata

# Get database URL from environment variables or Alembic config
DATABASE_URL = os.getenv('DATABASE_URL', config.get_main_option("sqlalchemy.url"))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run asynchronous migrations using async SQLAlchemy engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode using asyncio."""
    asyncio.run(run_async_migrations())

# Choose offline or online migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
