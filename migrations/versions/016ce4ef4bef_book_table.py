"""book table

Revision ID: 016ce4ef4bef
Revises: 
Create Date: 2020-11-21 15:39:30.770407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016ce4ef4bef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.Text(), nullable=False),
    sa.Column('surname', sa.Text(), nullable=False),
    sa.Column('date_birth', sa.Date(), nullable=True),
    sa.Column('date_death', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('book')
    op.drop_table('author')
    # ### end Alembic commands ###
