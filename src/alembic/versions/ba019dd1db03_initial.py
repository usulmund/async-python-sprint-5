"""initial

Revision ID: ba019dd1db03
Revises:
Create Date: 2023-10-10 17:58:22.432751

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ba019dd1db03'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_password',
        sa.Column(
            'id',
            sa.Integer,
            primary_key=True
        ),
        sa.Column(
            'username',
            sa.String(100),
            unique=True,
            nullable=False
        ),
        sa.Column(
            'password',
            sa.String(50),
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime,
            index=True,
            default=datetime.utcnow
        ),
    )
    op.create_table(
        'account_id_token',
        sa.Column(
            'account_id',
            sa.Integer,
            primary_key=True
        ),
        sa.Column(
            'token',
            sa.String(200),
            unique=True,
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime,
            index=True,
            default=datetime.utcnow
        ),
    )


def downgrade() -> None:
    op.drop_table('user_password')
    op.drop_table('account_id_token')
