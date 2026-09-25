"""add balance non-negative check constraint

Revision ID: 5ff5059a869c
Revises: f8ff005d9bfe
Create Date: 2026-09-23 20:26:15.109551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ff5059a869c'
down_revision: Union[str, Sequence[str], None] = 'f8ff005d9bfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint("check_balance_non_negative", "accounts", "balance >= 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("check_balance_non_negative", "accounts", type_="check")
