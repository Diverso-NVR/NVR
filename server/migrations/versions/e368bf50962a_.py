"""empty message

Revision ID: e368bf50962a
Revises: a9bd3f8edc15
Create Date: 2020-01-15 10:30:12.516816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e368bf50962a'
down_revision = 'a9bd3f8edc15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('main_source', sa.String(length=100), nullable=True))
    op.add_column('rooms', sa.Column('screen_source', sa.String(length=100), nullable=True))
    op.add_column('rooms', sa.Column('sound_source', sa.String(length=100), nullable=True))
    op.add_column('rooms', sa.Column('tracking_source', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rooms', 'tracking_source')
    op.drop_column('rooms', 'sound_source')
    op.drop_column('rooms', 'screen_source')
    op.drop_column('rooms', 'main_source')
    # ### end Alembic commands ###
