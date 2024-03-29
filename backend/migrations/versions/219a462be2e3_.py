"""empty message

Revision ID: 219a462be2e3
Revises: 0e9dd6124ab0
Create Date: 2021-03-10 01:31:04.347012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "219a462be2e3"
down_revision = "0e9dd6124ab0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.add_column("rooms", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.drop_constraint("rooms_name_key", "rooms", type_="unique")
    op.create_foreign_key(None, "rooms", "organizations", ["organization_id"], ["id"])
    op.drop_column("rooms", "stream_url")
    op.drop_column("rooms", "tracking_state")
    op.drop_column("rooms", "tracking_source")
    op.drop_column("sources", "tracking")
    op.add_column("users", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "users", "organizations", ["organization_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_column("users", "organization_id")
    op.add_column(
        "sources",
        sa.Column(
            "tracking",
            sa.VARCHAR(length=200),
            server_default=sa.text("NULL::character varying"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "rooms",
        sa.Column(
            "tracking_source",
            sa.VARCHAR(length=100),
            server_default=sa.text("NULL::character varying"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "rooms",
        sa.Column("tracking_state", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "rooms",
        sa.Column(
            "stream_url",
            sa.VARCHAR(length=300),
            server_default=sa.text("NULL::character varying"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(None, "rooms", type_="foreignkey")
    op.create_unique_constraint("rooms_name_key", "rooms", ["name"])
    op.drop_column("rooms", "organization_id")
    op.drop_table("organizations")
    # ### end Alembic commands ###
