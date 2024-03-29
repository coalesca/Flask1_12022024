"""Second migration

Revision ID: af3efccc3a62
Revises: e9ac75d3abc5
Create Date: 2024-02-16 21:07:45.892421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af3efccc3a62'
down_revision = 'e9ac75d3abc5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=302),
               nullable=False)

    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.alter_column('author_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.alter_column('author_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=302),
               nullable=True)

    # ### end Alembic commands ###
