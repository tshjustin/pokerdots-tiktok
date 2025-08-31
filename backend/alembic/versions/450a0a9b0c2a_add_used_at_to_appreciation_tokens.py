from alembic import op
import sqlalchemy as sa

revision = "0002_add_used_at"
down_revision = "b4d454f4524e"  # set to your previous revision id
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        "appreciation_tokens",
        sa.Column(
            "used_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
    )
    op.execute("UPDATE appreciation_tokens SET used_at = timezone('utc', now()) WHERE used_at IS NULL;")
    op.alter_column("appreciation_tokens", "used_at", server_default=None)

def downgrade():
    op.drop_column("appreciation_tokens", "used_at")
