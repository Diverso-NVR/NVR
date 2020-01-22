"""empty message

Revision ID: a9bd3f8edc15
Revises: 8f0b730d464e
Create Date: 2020-01-15 10:28:40.574676

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a9bd3f8edc15'
down_revision = '8f0b730d464e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rooms', 'main_source')
    op.drop_column('rooms', 'tracking_source')
    op.drop_column('rooms', 'sound_source')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('sound_source', mysql.VARCHAR(collation='utf8_bin', length=100), nullable=True))
    op.add_column('rooms', sa.Column('tracking_source', mysql.VARCHAR(collation='utf8_bin', length=100), nullable=True))
    op.add_column('rooms', sa.Column('main_source', mysql.VARCHAR(collation='utf8_bin', length=100), nullable=True))
    # ### end Alembic commands ###