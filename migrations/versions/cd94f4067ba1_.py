"""empty message

Revision ID: cd94f4067ba1
Revises: 7e060c8add4b
Create Date: 2021-12-28 14:20:15.530475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd94f4067ba1'
down_revision = '7e060c8add4b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kspaces',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domen_id', sa.Integer(), nullable=True),
    sa.Column('problem', sa.Integer(), nullable=True),
    sa.Column('probability', sa.Float(), nullable=True),
    sa.Column('iita_generated', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['domen_id'], ['parts.id'], ),
    sa.ForeignKeyConstraint(['problem'], ['sections.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('problems_related',
    sa.Column('source', sa.Integer(), nullable=True),
    sa.Column('target', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['source'], ['sections.id'], ),
    sa.ForeignKeyConstraint(['target'], ['sections.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('problems_related')
    op.drop_table('kspaces')
    # ### end Alembic commands ###