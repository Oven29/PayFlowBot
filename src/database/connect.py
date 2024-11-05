import databases
import ormar
import sqlalchemy

from src import config
from .enums import UserRole


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
    """Setup database"""
    create_all()

    from .methods.users import get_or_create
    await get_or_create(
        user_id=config.OWNER_ID,
        role=UserRole.OWNER,
    )
