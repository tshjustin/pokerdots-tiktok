from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from db import Base
import enum

class AppreciationSource(str, enum.Enum):
    tap = "tap"
    ad_boost = "ad_boost"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")

class TokenWallet(Base):
    __tablename__ = "token_wallets"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    monthly_budget = Column(Integer, default=100)
    bonus_balance = Column(Integer, default=0)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    title = Column(String)
    duration_s = Column(Integer)
    ai_score = Column(Float, default=0.0)
    ai_label = Column(String)
    metadata = Column(JSON)

class Appreciation(Base):
    __tablename__ = "appreciations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), index=True)
    ip_hash = Column(String)
    source = Column(Enum(AppreciationSource), default=AppreciationSource.tap)
    __table_args__ = (UniqueConstraint("user_id", "video_id", name="uniq_user_video_appreciation"),)
