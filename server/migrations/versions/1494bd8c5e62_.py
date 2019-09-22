"""empty message

Revision ID: 1494bd8c5e62
Revises: 4de86d57c651
Create Date: 2019-09-22 14:09:22.595001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1494bd8c5e62'
down_revision = '4de86d57c651'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('chosen_sound', sa.String(length=100), nullable=False))
    op.alter_column('rooms', 'free',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('rooms', 'processing',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('rooms', 'timestamp',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('rooms', 'status')
    op.drop_column('rooms', 'chosenSound')
    op.add_column('sources', sa.Column('main_cam', sa.Boolean(), nullable=False))
    op.drop_column('sources', 'mainCam')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sources', sa.Column('mainCam', sa.BOOLEAN(), nullable=False))
    op.drop_column('sources', 'main_cam')
    op.add_column('rooms', sa.Column('chosenSound', sa.VARCHAR(length=100), nullable=True))
    op.add_column('rooms', sa.Column('status', sa.BOOLEAN(), nullable=True))
    op.alter_column('rooms', 'timestamp',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('rooms', 'processing',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('rooms', 'free',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.drop_column('rooms', 'chosen_sound')
    # ### end Alembic commands ###
