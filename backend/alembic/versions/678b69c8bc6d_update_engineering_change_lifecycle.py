"""update engineering change lifecycle

Revision ID: 678b69c8bc6d
Revises: ef52531ac608
Create Date: 2026-08-20 21:47:34.814066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '678b69c8bc6d'
down_revision: Union[str, Sequence[str], None] = 'ef52531ac608'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TYPE changestatus RENAME VALUE 'IMPLEMENTED' TO 'IMPLEMENTING'"
    )

    op.execute(
        "ALTER TYPE changestatus ADD VALUE 'VERIFIED' AFTER 'IMPLEMENTING'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE changestatus RENAME TO changestatus_old")

    op.execute(
        """
        CREATE TYPE changestatus AS ENUM (
            'DRAFT',
            'SUBMITTED',
            'UNDER_REVIEW',
            'APPROVED',
            'REJECTED',
            'IMPLEMENTED',
            'CLOSED'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE engineering_changes
        ALTER COLUMN status
        TYPE changestatus
        USING status::text::changestatus
        """
    )

    op.execute("DROP TYPE changestatus_old")
