"""add user role field

Revision ID: 20260131_add_user_role
Revises: 20260125_add_las_file_type
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260131_add_user_role'
down_revision = '20260125_add_las_file_type'
branch_labels = None
depends_on = None


def upgrade():
    # 添加role字段，默认值为'user'
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=False, server_default='user'))
    
    # 将admin用户的role设置为'admin'
    op.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")


def downgrade():
    # 删除role字段
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')
