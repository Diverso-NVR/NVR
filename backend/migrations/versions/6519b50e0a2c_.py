"""empty message

Revision ID: 6519b50e0a2c
Revises: 
Create Date: 2020-06-26 15:42:36.583954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6519b50e0a2c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(length=100), nullable=False),
        sa.Column("start_time", sa.String(length=100), nullable=False),
        sa.Column("end_time", sa.String(length=100), nullable=False),
        sa.Column("event_name", sa.String(length=200), nullable=True),
        sa.Column("event_id", sa.String(length=200), nullable=True),
        sa.Column("user_email", sa.String(length=200), nullable=False),
        sa.Column("room_name", sa.String(length=200), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=True),
        sa.Column("processing", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("tracking_state", sa.Boolean(), nullable=True),
        sa.Column("drive", sa.String(length=200), nullable=True),
        sa.Column("calendar", sa.String(length=200), nullable=True),
        sa.Column("stream_url", sa.String(length=300), nullable=True),
        sa.Column("sound_source", sa.String(length=100), nullable=True),
        sa.Column("main_source", sa.String(length=100), nullable=True),
        sa.Column("tracking_source", sa.String(length=100), nullable=True),
        sa.Column("screen_source", sa.String(length=100), nullable=True),
        sa.Column("auto_control", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=True),
        sa.Column("access", sa.Boolean(), nullable=True),
        sa.Column("api_key", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("api_key"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("ip", sa.String(length=200), nullable=True),
        sa.Column("port", sa.String(length=200), nullable=True),
        sa.Column("rtsp", sa.String(length=200), nullable=True),
        sa.Column("audio", sa.String(length=200), nullable=True),
        sa.Column("merge", sa.String(length=200), nullable=True),
        sa.Column("tracking", sa.String(length=200), nullable=True),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sources")
    op.drop_table("channels")
    op.drop_table("users")
    op.drop_table("rooms")
    op.drop_table("records")
    # ### end Alembic commands ###
