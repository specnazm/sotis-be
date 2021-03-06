"""empty message

Revision ID: 75b41c265bdc
Revises: 5b553214613c
Create Date: 2021-12-28 18:58:47.234798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75b41c265bdc'
down_revision = '5b553214613c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('kspaces', sa.Column('domain_id', sa.Integer(), nullable=True))
    op.drop_constraint('kspaces_domen_id_fkey', 'kspaces', type_='foreignkey')
    op.create_foreign_key(None, 'kspaces', 'parts', ['domain_id'], ['id'])
    op.drop_column('kspaces', 'domen_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('kspaces', sa.Column('domen_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'kspaces', type_='foreignkey')
    op.create_foreign_key('kspaces_domen_id_fkey', 'kspaces', 'parts', ['domen_id'], ['id'])
    op.drop_column('kspaces', 'domain_id')
    # ### end Alembic commands ###
