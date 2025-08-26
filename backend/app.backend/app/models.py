from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, Integer, ForeignKey, JSON, TIMESTAMP, text, Numeric
from app.db import Base

NUM = Numeric(18, 2)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped[str] = mapped_column(Text, server_default="viewer", nullable=False)  # 'viewer','creator','admin'
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Stream(Base):
    __tablename__ = "streams"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, server_default="live", nullable=False)   # 'live','ended','settled'
    start_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    end_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    policy_json: Mapped[dict] = mapped_column(JSON, server_default=text("'{}'::json"), nullable=False)

class ViewerSession(Base):
    __tablename__ = "viewer_sessions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streams.id"), nullable=False)
    viewer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_fingerprint_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    ended_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

class EngagementEvent(Base):
    __tablename__ = "engagement_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streams.id"), nullable=False)
    viewer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)  # 'like','share','view'
    flags: Mapped[dict] = mapped_column(JSON, server_default=text("'{}'::json"), nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streams.id"), nullable=False)
    viewer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    flags: Mapped[dict] = mapped_column(JSON, server_default=text("'{}'::json"), nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Gift(Base):
    __tablename__ = "gifts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streams.id"), nullable=False)
    from_user: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    coin_amount: Mapped[float] = mapped_column(NUM, nullable=False)
    device_fingerprint_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
