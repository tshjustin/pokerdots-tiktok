from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# from ..database.models import User, Video, Appreciation, TokenWallet #, AdSession
# from schemas import SignUp, Login, AppreciateIn, AdStartIn, AdCompleteIn
# from security import create_access_token, get_current_user
# from utils import ip_hash, rate_limit_ok
import logging
from database.db import create_database, create_tables
logging.basicConfig(level=logging.INFO)


# ---------- Swagger / OpenAPI polish ----------
tags_metadata = [
    {"name": "Health", "description": "Service health checks."},
    {"name": "Auth", "description": "Signup, login, and token endpoints (OAuth2 Password flow)."},
]

app = FastAPI(
    title="PokerDots API",
    version="1.0.0",
    description="Backend for PokerDots (auth, health, and more).",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)

origins = [
    "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origins you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only import routes after "app" has been initialised
from .routes.health import router as health_router
from .auth.auth_router import router as auth_router
from .routes.appreciations import router as appreciations_router
# from database import events

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(appreciations_router)

# Application startup event
@app.on_event("startup")
def startup_event():
    logging.info("Application is starting up...")
    # Create DB
    create_database()
    logging.info("Database successfully created.")
    # Create DB Tables
    create_tables()
    logging.info("Tables successfully created.")

@app.on_event("shutdown")
def shutdown_event():
    logging.info("Application is shutting down.")

# @app.get("/tokens/balance")
# def balance(user=Depends(get_current_user), db: Session = Depends(get_db)):
#     # return monthly_budget + bonus_balance
#     ...

# @app.post("/appreciations")
# def appreciate(req: Request, inp: AppreciateIn,
#                user=Depends(get_current_user), db: Session = Depends(get_db)):
#     client_ip = req.headers.get("x-forwarded-for", req.client.host)
#     if not rate_limit_ok(user.id, client_ip): raise HTTPException(429)
#     v = db.get(Video, inp.video_id)
#     if not v: raise HTTPException(404, "video not found")
#     # watch-time check (trusted from client or verified from player logs)
#     if inp.watched_seconds < min(v.duration_s*0.3, 15):
#         raise HTTPException(400, "insufficient watch time")
#     # ensure wallet has tokens
#     wallet = db.query(TokenWallet).filter_by(user_id=user.id).first()
#     if wallet.monthly_budget + wallet.bonus_balance < 1:
#         raise HTTPException(400, "insufficient tokens")
#     # one per user/video
#     exists = db.query(Appreciation).filter_by(user_id=user.id, video_id=v.id).first()
#     if exists: raise HTTPException(409, "already appreciated")
#     # record + deduct
#     apprec = Appreciation(user_id=user.id, video_id=v.id,
#                           ip_hash=ip_hash(client_ip), source="tap")
#     db.add(apprec)
#     if wallet.monthly_budget > 0: wallet.monthly_budget -= 1
#     else: wallet.bonus_balance -= 1
#     db.commit()
#     return {"ok": True}

# @app.post("/ads/start")
# def ad_start(inp: AdStartIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
#     sess = AdSession(user_id=user.id, provider=inp.provider, status="started", reward_tokens=inp.reward_tokens)
#     db.add(sess); db.commit()
#     return {"ad_session_id": sess.id}

# @app.post("/ads/complete")
# def ad_complete(inp: AdCompleteIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
#     # verify provider webhook/token here; enforce idempotency
#     sess = db.get(AdSession, inp.ad_session_id)
#     if not sess or sess.user_id != user.id: raise HTTPException(404)
#     if sess.status == "completed": return {"ok": True}  # idempotent
#     sess.status = "completed"
#     wallet = db.query(TokenWallet).filter_by(user_id=user.id).first()
#     wallet.bonus_balance += sess.reward_tokens
#     db.commit()
#     return {"ok": True, "bonus_added": sess.reward_tokens}

# @app.post("/videos/ai-check")
# def ai_check(video_id: int, db: Session = Depends(get_db)):
#     # call your model / external API; here stub:
#     v = db.get(Video, video_id)
#     if not v: raise HTTPException(404)
#     v.ai_score = 0.35  # TODO replace with real
#     v.ai_label = "low"
#     db.commit()
#     return {"video_id": v.id, "ai_score": v.ai_score, "ai_label": v.ai_label}
