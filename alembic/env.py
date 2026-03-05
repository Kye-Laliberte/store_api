import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

load_dotenv()

config = context.config

if config.config_file_name is not None:
     fileConfig(config.config_file_name)