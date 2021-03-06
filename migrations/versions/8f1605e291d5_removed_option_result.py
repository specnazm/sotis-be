"""removed option result

Revision ID: 8f1605e291d5
Revises: d44f8d99390b
Create Date: 2021-12-14 11:01:30.145240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f1605e291d5'
down_revision = 'd44f8d99390b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('option_result')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('option_result',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('checked', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('student_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('test_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('option_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['option_id'], ['options.id'], name='option_result_option_id_fkey'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name='option_result_student_id_fkey'),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], name='option_result_test_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='option_result_pkey')
    )
    # ### end Alembic commands ###
