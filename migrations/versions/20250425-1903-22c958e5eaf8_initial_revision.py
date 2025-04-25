"""Initial revision

Revision ID: 22c958e5eaf8
Revises:
Create Date: 2025-04-25 19:03:49.695122

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "22c958e5eaf8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
