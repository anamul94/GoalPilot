"""add_goal_is_active

Revision ID: f2a8c7d1b9e4
Revises: 716f4b6bc58b
Create Date: 2026-04-03 12:26:50

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a8c7d1b9e4'
down_revision: Union[str, None] = '716f4b6bc58b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('goals', sa.Column('is_active', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_index(op.f('ix_goals_is_active'), 'goals', ['is_active'], unique=False)
    op.alter_column('goals', 'is_active', server_default=None)


def downgrade() -> None:
    op.drop_index(op.f('ix_goals_is_active'), table_name='goals')
    op.drop_column('goals', 'is_active')
