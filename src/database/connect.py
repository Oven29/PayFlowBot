import databases
import ormar
import sqlalchemy

from src import config


base_config = ormar.OrmarConfig(
    metadata=sqlalchemy.MetaData(),
    database=databases.Database(config.DATABASE_URL),
    engine=sqlalchemy.create_engine(config.DATABASE_URL),
)


def create_all() -> None:
    """Create all tables in database if they don't exist"""
    from .models.users import User

    base_config.metadata.create_all(base_config.engine)


async def setup() -> None:
    create_all()
