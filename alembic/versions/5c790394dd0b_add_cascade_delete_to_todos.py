"""add cascade delete to todos

Revision ID: 5c790394dd0b
Revises: 2303f786b154
Create Date: 2024-09-25 16:07:00.343110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c790394dd0b'
down_revision: Union[str, None] = '2303f786b154'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('todos_owner_id_fkey', 'todos', type_='foreignkey')
    op.create_foreign_key(None, 'todos', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_column('users', 'phone_number')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'todos', type_='foreignkey')
    op.create_foreign_key('todos_owner_id_fkey', 'todos', 'users', ['owner_id'], ['id'])
    # ### end Alembic commands ###
