"""Add file info fields

Revision ID: 08ea19acb0a3
Revises: e300fab89c9c
Create Date: 2025-05-22 18:48:07.604331

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "08ea19acb0a3"
down_revision = "e300fab89c9c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("update_files", sa.Column("name", sa.String(), nullable=True))
    op.add_column("update_files", sa.Column("size", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("update_files", "size")
    op.drop_column("update_files", "name")
