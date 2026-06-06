"""add video description for text-only posts

Revision ID: 20260515_video_desc
Revises:
Create Date: 2026-05-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_video_desc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("videos", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("videos", "description")
