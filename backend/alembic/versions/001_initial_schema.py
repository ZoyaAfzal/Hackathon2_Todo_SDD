"""Initial schema for Phase II - User and Task tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-01-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        "user",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    # Create task table
    op.create_table(
        "task",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False
        ),
    )
    op.create_index("ix_task_user_id", "task", ["user_id"])
    op.create_index("ix_task_created_at", "task", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_task_created_at", table_name="task")
    op.drop_index("ix_task_user_id", table_name="task")
    op.drop_table("task")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")
