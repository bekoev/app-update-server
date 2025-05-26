"""Add update manifest

Revision ID: e79e6a04a0c1
Revises:
Create Date: 2025-05-22 16:57:42.253818

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e79e6a04a0c1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "update_manifests",
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("version"),
    )


def downgrade() -> None:
    op.drop_table("update_manifests")
