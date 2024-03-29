"""empty message

Revision ID: 205e9569ea2a
Revises: fcee913329c9
Create Date: 2020-12-01 17:37:08.899517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "205e9569ea2a"
down_revision = "fcee913329c9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("records", sa.Column("ruz_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(None, "records", ["ruz_id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "records", type_="unique")
    op.drop_column("records", "ruz_id")
    # ### end Alembic commands ###
