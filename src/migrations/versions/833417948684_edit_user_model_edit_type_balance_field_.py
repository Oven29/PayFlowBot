"""Edit User model - edit type balance field from int to float

Revision ID: 833417948684
Revises: b3c189945c8b
Create Date: 2024-11-21 23:38:10.053595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.migrations.utils import is_sqlite


# revision identifiers, used by Alembic.
revision: str = '833417948684'
down_revision: Union[str, None] = 'b3c189945c8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем, используется ли SQLite
    if is_sqlite():
        # Временная колонка с новым типом данных
        with op.batch_alter_table('checks') as batch_op:
            batch_op.add_column(sa.Column('status_temp', sa.Enum('OK', 'UNDERPAYMENT', 'OVERPAYMENT', 'ERROR', name='checkstatus'), nullable=False))
        # Перенос данных из старой колонки в новую
        op.execute("""
            UPDATE checks
            SET status_temp = status
        """)
        # Удаляем старую колонку
        with op.batch_alter_table('checks') as batch_op:
            batch_op.drop_column('status')
        # Переименовываем новую колонку
        with op.batch_alter_table('checks') as batch_op:
            batch_op.alter_column('status_temp', new_column_name='status')
    else:
        # Стандартное изменение типа для других баз данных
        op.alter_column('checks', 'status',
                        existing_type=sa.VARCHAR(length=13),
                        type_=sa.Enum('OK', 'UNDERPAYMENT', 'OVERPAYMENT', 'ERROR', name='checkstatus'),
                        existing_nullable=False)

    # Аналогично для изменения типа у `users.balance`
    if is_sqlite():
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('balance_temp', sa.Float(), nullable=True))
        op.execute("""
            UPDATE users
            SET balance_temp = balance
        """)
        with op.batch_alter_table('users') as batch_op:
            batch_op.drop_column('balance')
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column('balance_temp', new_column_name='balance')
    else:
        op.alter_column('users', 'balance',
                        existing_type=sa.INTEGER(),
                        type_=sa.Float(),
                        existing_nullable=True)


def downgrade() -> None:
    # Обратный процесс для SQLite
    if is_sqlite():
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('balance_temp', sa.INTEGER(), nullable=True))
        op.execute("""
            UPDATE users
            SET balance_temp = balance
        """)
        with op.batch_alter_table('users') as batch_op:
            batch_op.drop_column('balance')
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column('balance_temp', new_column_name='balance')

        with op.batch_alter_table('checks') as batch_op:
            batch_op.add_column(sa.Column('status_temp', sa.VARCHAR(length=13), nullable=False))
        op.execute("""
            UPDATE checks
            SET status_temp = status
        """)
        with op.batch_alter_table('checks') as batch_op:
            batch_op.drop_column('status')
        with op.batch_alter_table('checks') as batch_op:
            batch_op.alter_column('status_temp', new_column_name='status')
    else:
        # Стандартное изменение типа для других баз данных
        op.alter_column('users', 'balance',
                        existing_type=sa.Float(),
                        type_=sa.INTEGER(),
                        existing_nullable=True)
        op.alter_column('checks', 'status',
                        existing_type=sa.Enum('OK', 'UNDERPAYMENT', 'OVERPAYMENT', 'ERROR', name='checkstatus'),
                        type_=sa.VARCHAR(length=13),
                        existing_nullable=False)
