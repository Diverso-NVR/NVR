"""empty message

Revision ID: 8316f4f289c1
Revises: f8f2be3fd920
Create Date: 2021-02-23 20:48:31.378027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8316f4f289c1"
down_revision = "f8f2be3fd920"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("rooms", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "rooms", "organizations", ["organization_id"], ["id"])
    op.add_column("users", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "users", "organizations", ["organization_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_column("users", "organization_id")
    op.drop_constraint(None, "rooms", type_="foreignkey")
    op.drop_column("rooms", "organization_id")
    # ### end Alembic commands ###
