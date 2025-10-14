"""update booking model added created_at and update_at fields in model

Revision ID: 4cfaf9fcf5dc
Revises: bff197ac6894
Create Date: 2025-10-12 23:19:12.302802

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '4cfaf9fcf5dc'
down_revision: Union[str, None] = 'bff197ac6894'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
