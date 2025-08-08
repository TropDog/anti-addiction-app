"""forms improvement

Revision ID: 4adb12c322b1
Revises: d76f72c20486
Create Date: 2025-08-08 21:30:07.237722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4adb12c322b1'
down_revision: Union[str, Sequence[str], None] = 'd76f72c20486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


quitstrategy_enum = postgresql.ENUM(
    'immediately', 'gradual_reduction', 'medication', 'behavioral_therapy', 'combination', 'undecided',
    name='quitstrategy'
)

quitstage_enum = postgresql.ENUM(
    'IMMEDIATELY', 'GRADUAL_REDUCTION', 'MEDICATION', 'BEHAVIORAL_THERAPY', 'COMBINATION', 'UNDECIDED',
    name='quitstage'
)

def upgrade() -> None:
    op.add_column('questions', sa.Column('user_profile_field_name', sa.String(), nullable=True))

    quitstrategy_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        'user_profiles',
        'quitting_strategy',
        existing_type=quitstage_enum,
        type_=quitstrategy_enum,
        postgresql_using='quitting_strategy::text::quitstrategy',
        existing_nullable=False,
    )



def downgrade() -> None:
    op.alter_column(
        'user_profiles',
        'quitting_strategy',
        existing_type=quitstrategy_enum,
        type_=quitstage_enum,
        postgresql_using='quitting_strategy::text::quitstage',
        existing_nullable=False,
    )

    op.drop_column('questions', 'user_profile_field_name')

    quitstrategy_enum.drop(op.get_bind(), checkfirst=True)
