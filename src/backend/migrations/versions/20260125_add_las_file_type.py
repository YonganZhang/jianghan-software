"""add las to file_type enum

Revision ID: 20260125_add_las_file_type
Revises: ce94e8fb7cf9
Create Date: 2026-01-25

"""

from alembic import op
import sqlalchemy as sa


revision = '20260125_add_las_file_type'
down_revision = 'ce94e8fb7cf9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('files', schema=None, recreate='always') as batch_op:
        batch_op.alter_column(
            'type',
            existing_type=sa.Enum('xlsx', 'txt', name='file_type'),
            type_=sa.Enum('xlsx', 'txt', 'las', name='file_type'),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table('files', schema=None, recreate='always') as batch_op:
        batch_op.alter_column(
            'type',
            existing_type=sa.Enum('xlsx', 'txt', 'las', name='file_type'),
            type_=sa.Enum('xlsx', 'txt', name='file_type'),
            existing_nullable=False,
        )

