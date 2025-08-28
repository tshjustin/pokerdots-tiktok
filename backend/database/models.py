from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
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

class TokenWallet(Base):
    __tablename__ = "token_wallets"
    wallet_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    monthly_budget = Column(Integer, default=100)
    bonus_balance = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="wallet")
    appreciation_tokens = relationship("AppreciationToken", back_populates="wallet", passive_deletes=True)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String, unique=True, nullable=False, index=True)
    duration_s = Column(Integer)
    ai_score = Column(Float, default=0.0)
    ai_label = Column(String)
    meta_data = Column(JSON)

    # Relationships
    creator = relationship("User", back_populates="videos")
    appreciation_tokens = relationship("AppreciationToken", back_populates="video", passive_deletes=True)

class AppreciationToken(Base):
    __tablename__ = "appreciation_tokens"
    token_id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_id = Column(Integer, ForeignKey("token_wallets.wallet_id", ondelete="CASCADE"), nullable=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    ip_hash = Column(String)
    source = Column(Enum(AppreciationSource), default=AppreciationSource.tap)

    # Relationships
    wallet = relationship("TokenWallet", back_populates="appreciation_tokens")
    video = relationship("Video", back_populates="appreciation_tokens")

    __table_args__ = (UniqueConstraint("wallet_id", "video_id", name="uniq_user_video_appreciation"),)
