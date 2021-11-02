"""empty message

Revision ID: 0ca0af0ae728
Revises: 16e9c4460b9b
Create Date: 2021-11-02 18:33:43.743690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ca0af0ae728'
down_revision = '16e9c4460b9b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test_result', sa.Column('student_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'test_result', 'students', ['student_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'test_result', type_='foreignkey')
    op.drop_column('test_result', 'student_id')
    # ### end Alembic commands ###
