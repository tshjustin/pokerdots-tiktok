import os, hmac, hashlib
from fastapi import Header, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.models import IdempotencyKey

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Idempotency header
def require_idempotency_key(idempotency_key: str | None = Header(None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(400, "Missing Idempotency-Key header")
    return idempotency_key

def claim_idempotency(db: Session, key: str, action: str):
    try:
        db.add(IdempotencyKey(key=key, action=action))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate Idempotency-Key")

# Client IP (supports proxies)
def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host

# Salted IP hash (privacy-safe)
_SALT = os.getenv("IP_HASH_SALT", "dev-only-change-me")
def hash_ip(ip: str) -> str:
    return hmac.new(_SALT.encode(), msg=ip.encode(), digestmod=hashlib.sha256).hexdigest()
