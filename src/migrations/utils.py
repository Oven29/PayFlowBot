from alembic import op
from sqlalchemy.dialects import sqlite


def is_sqlite() -> bool:
    """
     Check if the current database connection is SQLite.
    """
    return isinstance(op.get_bind().dialect, sqlite.dialect)
