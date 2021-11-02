"""empty message

Revision ID: 15b5bd1de436
Revises: 0ca0af0ae728
Create Date: 2021-11-02 21:40:10.527921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15b5bd1de436'
down_revision = '0ca0af0ae728'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parts', sa.Column('title', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parts', 'title')
    # ### end Alembic commands ###