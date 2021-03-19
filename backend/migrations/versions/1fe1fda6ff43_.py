"""empty message

Revision ID: 1fe1fda6ff43
Revises: c05df771cc26
Create Date: 2021-03-19 21:33:08.418805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fe1fda6ff43'
down_revision = 'c05df771cc26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.VARCHAR(length=50), server_default=sa.text('NULL::character varying'), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
