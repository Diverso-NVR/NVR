"""empty message

Revision ID: 384ca68f75a0
Revises: 5af61ad4104d
Create Date: 2020-11-18 15:09:07.099596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "384ca68f75a0"
down_revision = "5af61ad4104d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("records", sa.Column("room_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(None, "records", ["event_id"])
    op.create_foreign_key(None, "records", "rooms", ["room_id"], ["id"])
    op.drop_column("records", "room_name")
    op.drop_column("records", "user_email")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "records",
        sa.Column(
            "user_email", sa.VARCHAR(length=100), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "records",
        sa.Column(
            "room_name", sa.VARCHAR(length=200), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(None, "records", type_="foreignkey")
    op.drop_constraint(None, "records", type_="unique")
    op.drop_column("records", "room_id")
    # ### end Alembic commands ###
