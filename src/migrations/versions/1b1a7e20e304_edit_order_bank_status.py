"""Edit Order bank status

Revision ID: 1b1a7e20e304
Revises: 4a3b6140fd22
Create Date: 2024-11-26 19:36:37.474226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.migrations.utils import is_sqlite


# revision identifiers, used by Alembic.
revision: str = '1b1a7e20e304'
down_revision: Union[str, None] = '4a3b6140fd22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Perform the upgrade operation, adapting behavior for SQLite.
    """
    if is_sqlite():
        # SQLite does not support ALTER COLUMN directly.
        # Workaround: create a temporary table with the new schema,
        # copy data, and replace the old table.
        with op.batch_alter_table("orders") as batch_op:
            batch_op.add_column(sa.Column("bank_temp", sa.String(8), nullable=True))
        op.execute("UPDATE orders SET bank_temp = bank")
        with op.batch_alter_table("orders") as batch_op:
            batch_op.drop_column("bank")
            batch_op.add_column(sa.Column("bank", sa.Enum("TINK", "INTER", name="orderbank"), nullable=True))
            batch_op.drop_column("bank_temp")
    else:
        # For databases with full ALTER support
        op.alter_column(
            "orders",
            "bank",
            existing_type=sa.VARCHAR(length=8),
            type_=sa.Enum("TINK", "INTER", name="orderbank"),
            existing_nullable=False,
        )


def downgrade() -> None:
    """
    Revert the migration, adapting behavior for SQLite.
    """
    if is_sqlite():
        # Reverse the workaround: replace table with original schema
        with op.batch_alter_table("orders") as batch_op:
            batch_op.add_column(sa.Column("bank_temp", sa.String(8), nullable=True))
        op.execute("UPDATE orders SET bank_temp = CAST(bank AS TEXT)")
        with op.batch_alter_table("orders") as batch_op:
            batch_op.drop_column("bank")
            batch_op.add_column(sa.Column("bank", sa.String(8), nullable=True))
            batch_op.drop_column("bank_temp")
    else:
        op.alter_column(
            "orders",
            "bank",
            existing_type=sa.Enum("TINK", "INTER", name="orderbank"),
            type_=sa.VARCHAR(length=8),
            existing_nullable=False,
        )
