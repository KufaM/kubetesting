from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Přidání cesty k souboru s aplikací
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db  # Importování db objektu z Flask aplikace

# Načítání konfiguračního souboru Alembic
fileConfig(context.config.config_file_name)

# Nastavení pro generování migrací
target_metadata = db.Model.metadata

def run_migrations_online():
    # Používáme engine pro SQLite
    connectable = engine_from_config(
        context.config.get_section(context.config.default_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
