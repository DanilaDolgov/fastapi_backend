"""initial migration

Revision ID: 4c6037d7cfb9
Revises: 
Create Date: 2025-06-18 11:51:00.162622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4c6037d7cfb9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('hotels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('hotels')

