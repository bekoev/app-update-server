"""Add file info

Revision ID: e300fab89c9c
Revises: e79e6a04a0c1
Create Date: 2025-05-22 18:07:24.748593

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e300fab89c9c"
down_revision = "e79e6a04a0c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "update_files",
        sa.Column(
            "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("comment", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("update_files")
