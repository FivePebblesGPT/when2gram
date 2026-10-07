"""Initial schema.

Revision ID: 0001
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("telegram_id"),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=32), nullable=False),
        sa.Column("organizer_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("start_minute", sa.Integer(), nullable=False),
        sa.Column("end_minute", sa.Integer(), nullable=False),
        sa.Column("slot_minutes", sa.Integer(), nullable=False),
        sa.Column("response_target", sa.Integer(), nullable=True),
        sa.Column("target_notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organizer_id"], ["users.telegram_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_organizer_id"), "events", ["organizer_id"], unique=False)
    op.create_index(op.f("ix_events_token"), "events", ["token"], unique=True)
    op.create_table(
        "event_days",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "day", name="uq_event_days_event_day"),
    )
    op.create_index(op.f("ix_event_days_event_id"), "event_days", ["event_id"], unique=False)
    op.create_table(
        "responses",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id", "user_id"),
    )
    op.create_table(
        "availability_days",
        sa.Column("event_day_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("slot_mask", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["event_day_id"], ["event_days.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_day_id", "user_id"),
    )
    op.create_table(
        "inline_invites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("inline_message_id", sa.String(length=255), nullable=False),
        sa.Column("sent_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sent_by_user_id"], ["users.telegram_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inline_message_id"),
    )
    op.create_index(op.f("ix_inline_invites_event_id"), "inline_invites", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inline_invites_event_id"), table_name="inline_invites")
    op.drop_table("inline_invites")
    op.drop_table("availability_days")
    op.drop_table("responses")
    op.drop_index(op.f("ix_event_days_event_id"), table_name="event_days")
    op.drop_table("event_days")
    op.drop_index(op.f("ix_events_token"), table_name="events")
    op.drop_index(op.f("ix_events_organizer_id"), table_name="events")
    op.drop_table("events")
    op.drop_table("users")
