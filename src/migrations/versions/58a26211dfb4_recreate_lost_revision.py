"""Recreate lost revision

Revision ID: 58a26211dfb4
Revises: cae0b892d31c
Create Date: 2025-11-02 16:52:13.860592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29d71fbc9739'
down_revision: Union[str, None] = 'cae0b892d31c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
