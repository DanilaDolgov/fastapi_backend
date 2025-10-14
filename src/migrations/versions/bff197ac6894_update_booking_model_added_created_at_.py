"""update booking model added created_at and update_at fields in model

Revision ID: bff197ac6894
Revises: 95bd3d8a8646
Create Date: 2025-10-12 23:16:56.080622

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = 'bff197ac6894'
down_revision: Union[str, None] = '95bd3d8a8646'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
