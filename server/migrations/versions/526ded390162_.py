"""empty message

Revision ID: 526ded390162
Revises: 2357820f9dae
Create Date: 2019-09-22 12:32:24.534816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '526ded390162'
down_revision = '2357820f9dae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('rooms', 'chosenSound',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    op.alter_column('rooms', 'chosenSound',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    # ### end Alembic commands ###
