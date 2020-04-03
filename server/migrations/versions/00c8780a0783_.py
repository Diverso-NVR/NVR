"""empty message

Revision ID: 00c8780a0783
Revises: c228c2073ceb
Create Date: 2020-03-29 16:10:43.271986

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '00c8780a0783'
down_revision = 'c228c2073ceb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=100), nullable=False),
    sa.Column('start_time', sa.String(length=100), nullable=False),
    sa.Column('end_time', sa.String(length=100), nullable=False),
    sa.Column('event_name', sa.String(length=200), nullable=True),
    sa.Column('event_id', sa.String(length=200), nullable=True),
    sa.Column('user_email', sa.String(length=200), nullable=False),
    sa.Column('room_name', sa.String(length=200), nullable=False),
    sa.Column('done', sa.Boolean(), nullable=True),
    sa.Column('processing', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('channels',
    sa.Column('id', sa.String(length=100), nullable=False),
    sa.Column('resource_id', sa.String(length=100), nullable=True),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('pid', table_name='streams')
    op.drop_table('streams')
    op.add_column('rooms', sa.Column('stream_url', sa.String(length=300), nullable=True))
    op.create_unique_constraint(None, 'rooms', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rooms', type_='unique')
    op.drop_column('rooms', 'stream_url')
    op.create_table('streams',
    sa.Column('url', mysql.VARCHAR(collation='utf8_bin', length=250), nullable=False),
    sa.Column('pid', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('url'),
    mysql_collate='utf8_bin',
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index('pid', 'streams', ['pid'], unique=True)
    op.drop_table('channels')
    op.drop_table('records')
    # ### end Alembic commands ###