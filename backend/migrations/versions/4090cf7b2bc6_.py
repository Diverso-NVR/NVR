"""empty message

Revision ID: 4090cf7b2bc6
Revises: cf578317c711
Create Date: 2020-11-24 14:07:01.245536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4090cf7b2bc6"
down_revision = "cf578317c711"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user_records", "id")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user_records",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
    )
    # ### end Alembic commands ###
