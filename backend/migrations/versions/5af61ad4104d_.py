"""empty message

Revision ID: 5af61ad4104d
Revises: b1d97f35b0c1
Create Date: 2020-11-18 14:53:48.969519

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5af61ad4104d"
down_revision = "b1d97f35b0c1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("channels", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("channels", sa.Column("modified_at", sa.DateTime(), nullable=True))
    op.add_column("records", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("records", sa.Column("modified_at", sa.DateTime(), nullable=True))
    op.add_column("rooms", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("rooms", sa.Column("modified_at", sa.DateTime(), nullable=True))
    op.drop_table_comment("rooms", existing_comment="rooms table schema", schema=None)
    op.add_column("sources", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("sources", sa.Column("modified_at", sa.DateTime(), nullable=True))
    op.drop_table_comment(
        "sources", existing_comment="source table schema", schema=None
    )
    op.drop_column("sources", "time_editing")
    op.add_column("user_records", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column(
        "user_records", sa.Column("modified_at", sa.DateTime(), nullable=True)
    )
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("modified_at", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "modified_at")
    op.drop_column("users", "created_at")
    op.drop_column("user_records", "modified_at")
    op.drop_column("user_records", "created_at")
    op.add_column(
        "sources",
        sa.Column(
            "time_editing", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.create_table_comment(
        "sources", "source table schema", existing_comment=None, schema=None
    )
    op.drop_column("sources", "modified_at")
    op.drop_column("sources", "created_at")
    op.create_table_comment(
        "rooms", "rooms table schema", existing_comment=None, schema=None
    )
    op.drop_column("rooms", "modified_at")
    op.drop_column("rooms", "created_at")
    op.drop_column("records", "modified_at")
    op.drop_column("records", "created_at")
    op.drop_column("channels", "modified_at")
    op.drop_column("channels", "created_at")
    # ### end Alembic commands ###
