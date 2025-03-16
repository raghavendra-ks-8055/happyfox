"""Create emails table

Revision ID: 001
Revises:
Create Date: 2023-11-16 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "emails",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("gmail_id", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("thread_id", sa.String(), index=True),
        sa.Column("from_address", sa.String(), nullable=False),
        sa.Column("to_address", sa.String()),
        sa.Column("subject", sa.String()),
        sa.Column("body", sa.Text()),
        sa.Column("snippet", sa.String()),
        sa.Column("received_date", sa.DateTime(), default=sa.func.now()),
        sa.Column("label_ids", JSON()),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()
        ),
    )


def downgrade():
    op.drop_table("emails")
