from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum, UniqueConstraint, Boolean, func
import enum
from .session import Base

class AppreciationSource(str, enum.Enum):
    tap = "tap"
    ad_boost = "ad_boost"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True,autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Relationships
    wallet = relationship("TokenWallet", back_populates="user", uselist=False, passive_deletes=True)
    videos = relationship("Video", back_populates="creator", passive_deletes=True)
    appreciation_tokens = relationship("AppreciationToken", back_populates="user", passive_deletes=True)

class TokenWallet(Base):
    __tablename__ = "token_wallets"
    wallet_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    monthly_budget = Column(Integer, default=10)
    bonus_balance = Column(Integer, default=10) # Per month

    # Relationships
    user = relationship("User", back_populates="wallet")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String, unique=True, nullable=False, index=True)
    duration_s = Column(Integer)
    ai_score = Column(Float, default=0.0)
    ai_label = Column(String)
    meta_data = Column(JSON)
    s3_key = Column(String, unique=True, nullable=False)

    # Relationships
    creator = relationship("User", back_populates="videos")
    appreciation_tokens = relationship("AppreciationToken", back_populates="video", passive_deletes=True)


class AppreciationToken(Base):
    __tablename__ = "appreciation_tokens"
    token_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    ip_hash = Column(String)
    source = Column(Enum(AppreciationSource), default=AppreciationSource.tap)
    used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # <-- add this
    
    # Relationships
    user = relationship("User", back_populates="appreciation_tokens")
    video = relationship("Video", back_populates="appreciation_tokens")

    __table_args__ = (UniqueConstraint("user_id", "video_id", name="uniq_user_video_appreciation"),)


# class Comment(Base):
#     __tablename__ = "comments"
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#     stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streams.id"), nullable=False)
#     viewer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
#     text: Mapped[str] = mapped_column(Text, nullable=False)
#     flags: Mapped[dict] = mapped_column(JSON, server_default=text("'{}'::json"), nullable=False)
#     created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


