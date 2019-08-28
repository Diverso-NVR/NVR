"""empty message

Revision ID: d3bd71078459
Revises: 71e237baafa2
Create Date: 2019-07-09 23:24:49.553036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3bd71078459'
down_revision = '71e237baafa2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rooms', 'status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('status', sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###