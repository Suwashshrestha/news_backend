"""add_category_details_and_ads_table

Revision ID: b302e235d820
Revises: 20260515_video_desc
Create Date: 2026-05-22 15:59:39.299206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b302e235d820'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to categories
    op.add_column('categories', sa.Column('color', sa.String(length=20), nullable=True))
    op.add_column('categories', sa.Column('description', sa.Text(), nullable=True))

    # Create advertisements table
    op.create_table(
        'advertisements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=True),
        sa.Column('redirect_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advertisements_id'), 'advertisements', ['id'], unique=False)
    op.create_index(op.f('ix_advertisements_slug'), 'advertisements', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_advertisements_slug'), table_name='advertisements')
    op.drop_index(op.f('ix_advertisements_id'), table_name='advertisements')
    op.drop_table('advertisements')
    op.drop_column('categories', 'description')
    op.drop_column('categories', 'color')
