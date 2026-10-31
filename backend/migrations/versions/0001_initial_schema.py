"""Initial ECO-LOOP schema."""

from alembic import op

from app.core.database import Base
import app.models  # noqa: F401

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the current set of domain tables."""
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Drop ECO-LOOP domain tables created by this initial revision."""
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=True)
