"""Add DSP sessions table

Revision ID: dsp_sessions_001
Revises: 3781e22d8b01
Create Date: 2024-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from open_webui.migrations.util import get_existing_tables

# revision identifiers, used by Alembic.
revision: str = "dsp_sessions_001"
down_revision: Union[str, None] = "3781e22d8b01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_tables = set(get_existing_tables())
    
    if "dsp_session" not in existing_tables:
        op.create_table(
            "dsp_session",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("graph", sa.JSON(), nullable=True),
            sa.Column("forked_graph", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
            sa.Column("updated_at", sa.BigInteger(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    op.drop_table("dsp_session") 