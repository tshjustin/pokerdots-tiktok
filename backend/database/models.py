from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum, UniqueConstraint, Boolean, func
import enum
from .session import Base
from datetime import datetime, timezone



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
    description = Column(String)
    duration_s = Column(Integer)
    view_count = Column(Integer, default=0)
    ai_score = Column(Float, default=0.0) # added AI scores 
    ai_label = Column(String) 
    meta_data = Column(JSON)
    s3_key = Column(String, unique=True, nullable=False)
    s3_url = Column(String, nullable=False)  # added S3 url 
    file_size = Column(Integer)
    upload_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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



# --- Optional: AI score table (used by pools settlement, safe to keep empty initially) ---
class VideoAIScore(Base):
    __tablename__ = "video_ai_scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    # store probabilities in [0,1]
    human_prob = Column(Float)
    ai_prob = Column(Float)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))

    __table_args__ = (UniqueConstraint("video_id", name="uq_video_ai_score_video"),)

# --- Compensation rules (per month) ---
class CompensationRule(Base):
    __tablename__ = "compensation_rules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(7), unique=True, index=True)  # 'YYYY-MM'
    human_multiplier = Column(Float, default=1.2)
    ai_multiplier = Column(Float, default=0.7)
    dpv_base = Column(Float, default=1.0)

# --- Pools and shares ---
class Pool(Base):
    __tablename__ = "pools"
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_month = Column(String(7), index=True)   # 'YYYY-MM'
    base_amount = Column(Float, default=0.0)
    settled = Column(Boolean, default=False)
    settled_at = Column(DateTime(timezone=True))
    total_effective_tokens = Column(Float, default=0.0)

    shares = relationship("PoolShare", backref="pool", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("period_month", name="uq_pool_period_month"),)

class PoolShare(Base):
    __tablename__ = "pool_shares"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, ForeignKey("pools.id", ondelete="CASCADE"), index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    token_count = Column(Integer, default=0)
    effective_tokens = Column(Float, default=0.0)
    share_pct = Column(Float, default=0.0)
    payout_amount = Column(Float, default=0.0)

    __table_args__ = (UniqueConstraint("pool_id", "creator_id", name="uq_poolshare_pool_creator"),)
