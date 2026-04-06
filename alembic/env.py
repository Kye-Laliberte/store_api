import os
import sys 
from logging.config import fileConfig
from sqlalchemy import engine_from_config,pool
from alembic import context, config
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models.sqlAmodels import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Alembic Config object
#alembic_cfg = Config(os.path.join(os.path.dirname(__file__),"..","alembic.ini"))
#alembic_cfg = config(os.path.join(...))
context_cfg = context.config
print(f"{context_cfg}  this is alembic_cfg")
print(f"{DATABASE_URL} this is DATABASE_URL")

# Override the URL from .env
context_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)


if context_cfg.config_file_name is not None:
     fileConfig(context_cfg.config_file_name)

data_metadata = Base.metadata

data_base_url= os.getenv("DATABASE_URL")
context_cfg.set_main_option("sqlalchemy.url", data_base_url)


# Generates SQL scripts without connecting to DB
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=data_metadata,
        literal_binds=True,  # embeds values directly in SQL
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()  # runs migration scripts


    # Applies migrations directly to the DB
def run_migrations_online():
    # Create engine from Alembic config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=data_metadata
        )

        with context.begin_transaction():
            context.run_migrations()  # runs migration script


if context.is_offline_mode():
    print("true")
    #run_migrations_offline()
#else:
    #run_migrations_online()