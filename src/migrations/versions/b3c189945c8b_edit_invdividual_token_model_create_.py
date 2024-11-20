"""Edit invdividual token model: create manager field

Revision ID: b3c189945c8b
Revises: 56f6c39ca7b6
Create Date: 2024-11-20 22:05:56.159891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c189945c8b'
down_revision: Union[str, None] = '56f6c39ca7b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Используем batch mode для изменений
    with op.batch_alter_table('individual_tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('manager', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_individual_tokens_users_id_manager',
            'users',
            ['manager'],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    # Используем batch mode для отката изменений
    with op.batch_alter_table('individual_tokens', schema=None) as batch_op:
        batch_op.drop_constraint('fk_individual_tokens_users_id_manager', type_='foreignkey')
        batch_op.drop_column('manager')
