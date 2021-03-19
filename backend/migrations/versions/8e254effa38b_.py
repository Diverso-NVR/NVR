"""empty message

Revision ID: 8e254effa38b
Revises: 6e516be39982
Create Date: 2021-03-18 23:07:20.121132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e254effa38b'
down_revision = '6e516be39982'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('roles', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('roles', sa.Column('modified_at', sa.DateTime(), nullable=True))
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.create_unique_constraint(None, 'roles', ['name'])
    op.add_column('users', sa.Column('_role_id', sa.Integer(), nullable=True))
    op.drop_constraint('users__role_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'roles', ['_role_id'], ['id'])
    op.drop_column('users', '_role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('_role', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key('users__role_fkey', 'users', 'roles', ['_role'], ['name'])
    op.drop_column('users', '_role_id')
    op.drop_constraint(None, 'roles', type_='unique')
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.drop_column('roles', 'modified_at')
    op.drop_column('roles', 'id')
    op.drop_column('roles', 'created_at')
    # ### end Alembic commands ###
