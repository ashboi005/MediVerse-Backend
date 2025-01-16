from __future__ import with_statement
import os
import sys
from logging.config import fileConfig

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add your project's path to sys.path (optional depending on your project structure)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database object and your models here
from config import db
from models import User, UserDetails  # Adjust according to your models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Setup logging if needed
fileConfig(config.config_file_name)

# Set up SQLAlchemy engine
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=db.metadata,
            compare_type=True,  # Ensure it compares column types in migrations
        )

        with context.begin_transaction():
            context.run_migrations()

if __name__ == '__main__':
    run_migrations_online()
