"""empty message

Revision ID: 2fa37bbe12b2
Revises: aad9a519a32d
Create Date: 2025-02-23 12:36:35.322386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fa37bbe12b2'
down_revision = 'aad9a519a32d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))  # Change to nullable=True
        batch_op.drop_constraint('fk_students_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_students_user_id', 'users', ['user_id'], ['id'])
        batch_op.drop_column('fk_students_user_id')

def downgrade():
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fk_students_user_id', sa.INTEGER(), nullable=True))  # Change to nullable=True
        batch_op.drop_constraint('fk_students_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_students_user_id', 'users', ['fk_students_user_id'], ['id'])
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
