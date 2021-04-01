"""empty message

Revision ID: 87428e90af56
Revises: 
Create Date: 2021-03-30 13:17:18.968862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87428e90af56'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('consumer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('pwd', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('face',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('id_card', sa.String(length=50), nullable=True),
    sa.Column('arr', sa.String(length=4000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('key',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('consumer_id', sa.Integer(), nullable=True),
    sa.Column('api_key', sa.String(length=50), nullable=True),
    sa.Column('secret_key', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('key')
    op.drop_table('face')
    op.drop_table('consumer')
    # ### end Alembic commands ###