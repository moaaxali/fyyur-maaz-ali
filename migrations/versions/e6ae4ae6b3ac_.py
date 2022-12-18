"""empty message

Revision ID: e6ae4ae6b3ac
Revises: 76182135ccce
Create Date: 2022-12-15 23:36:01.849776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6ae4ae6b3ac'
down_revision = '76182135ccce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.alter_column('start_time',
               existing_type=sa.DATE(),
               type_=sa.String(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.alter_column('start_time',
               existing_type=sa.String(),
               type_=sa.DATE(),
               nullable=True)

    # ### end Alembic commands ###
