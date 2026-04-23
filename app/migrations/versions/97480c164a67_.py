from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '97480c164a67'
down_revision = '259e87bf98fa'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    with op.batch_alter_table('assessment_subject_scores', schema=None) as batch_op:
        if bind.dialect.name != 'sqlite':  # Skip for SQLite
            existing_constraints = [
                fk['name'] for fk in inspector.get_foreign_keys('assessment_subject_scores')
                if fk['constrained_columns'] == ['student_id']
            ]
            if existing_constraints:
                batch_op.drop_constraint(existing_constraints[0], type_='foreignkey')

        # Add a new foreign key with a proper name
        batch_op.create_foreign_key(
            'fk_assessment_subject_scores_student_id',
            'students', ['student_id'], ['id'], ondelete='RESTRICT'
        )


def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    with op.batch_alter_table('assessment_subject_scores', schema=None) as batch_op:
        if bind.dialect.name != 'sqlite':  # Skip for SQLite
            batch_op.drop_constraint('fk_assessment_subject_scores_student_id', type_='foreignkey')

        # Restore the original foreign key
        batch_op.create_foreign_key(
            'fk_assessment_subject_scores_student_id',
            'students', ['student_id'], ['id']
        )
