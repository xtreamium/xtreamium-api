"""add_oauth_fields_to_user

Revision ID: 4032dbea90c9
Revises: a4845ecd0f96
Create Date: 2025-11-29 18:38:47.493236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4032dbea90c9'
down_revision: Union[str, Sequence[str], None] = 'a4845ecd0f96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new OAuth columns
    op.add_column('users', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_token', sa.String(), nullable=True))

    # For SQLite, we need to use batch_alter_table to modify existing columns
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(),
                              nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop OAuth columns
    op.drop_column('users', 'oauth_token')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')

    # Revert hashed_password to non-nullable
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(),
                              nullable=False)
