"""Add product reviews and one-time email verification records."""

from alembic import op
import sqlalchemy as sa

revision = "0002_reviews_email_verification"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "email_verifications" not in inspector.get_table_names():
        op.create_table(
            "email_verifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("code_hash", sa.String(64), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("sent_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.UniqueConstraint("user_id", name="uq_email_verification_user"),
        )
        op.create_index("ix_email_verifications_user_id", "email_verifications", ["user_id"])
    if "product_reviews" not in inspector.get_table_names():
        op.create_table(
            "product_reviews",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("content", sa.String(1200)),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("product_id", "user_id", name="uq_review_product_user"),
        )
        op.create_index("ix_product_reviews_product_id", "product_reviews", ["product_id"])
        op.create_index("ix_product_reviews_user_id", "product_reviews", ["user_id"])


def downgrade() -> None:
    op.drop_table("product_reviews")
    op.drop_table("email_verifications")
