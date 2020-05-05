"""empty message

Revision ID: 1d67f295953a
Revises: 87878fc88046
Create Date: 2020-03-23 23:53:20.236395

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1d67f295953a'
down_revision = '87878fc88046'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event_name', sa.String(length=200), nullable=True),
    sa.Column('room_name', sa.String(length=200), nullable=False),
    sa.Column('date', sa.String(length=100), nullable=False),
    sa.Column('start_time', sa.String(length=100), nullable=False),
    sa.Column('end_time', sa.String(length=100), nullable=False),
    sa.Column('user_email', sa.String(length=100), nullable=False),
    sa.Column('event_id', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('drive_file_url', sa.String(length=300), nullable=False),
    sa.Column('user_email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('channels')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channels',
    sa.Column('id', mysql.VARCHAR(collation='utf8_bin', length=100), nullable=False),
    sa.Column('resource_id', mysql.VARCHAR(collation='utf8_bin', length=100), nullable=True),
    sa.Column('room_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], name='channels_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8_bin',
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_table('user_records')
    op.drop_table('records')
    # ### end Alembic commands ###
