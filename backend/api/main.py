from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Base, engine
from models import User, Video, Appreciation, TokenWallet, AdSession
from schemas import SignUp, Login, AppreciateIn, AdStartIn, AdCompleteIn
from security import create_access_token, get_current_user
from utils import ip_hash, rate_limit_ok

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post("/auth/signup")
def signup(data: SignUp, db: Session = Depends(get_db)):
    # create user + wallet
    ...

@app.post("/auth/login")
def login(data: Login, db: Session = Depends(get_db)):
    ...

@app.get("/tokens/balance")
def balance(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # return monthly_budget + bonus_balance
    ...

@app.post("/appreciations")
def appreciate(req: Request, inp: AppreciateIn,
               user=Depends(get_current_user), db: Session = Depends(get_db)):
    client_ip = req.headers.get("x-forwarded-for", req.client.host)
    if not rate_limit_ok(user.id, client_ip): raise HTTPException(429)
    v = db.get(Video, inp.video_id)
    if not v: raise HTTPException(404, "video not found")
    # watch-time check (trusted from client or verified from player logs)
    if inp.watched_seconds < min(v.duration_s*0.3, 15):
        raise HTTPException(400, "insufficient watch time")
    # ensure wallet has tokens
    wallet = db.query(TokenWallet).filter_by(user_id=user.id).first()
    if wallet.monthly_budget + wallet.bonus_balance < 1:
        raise HTTPException(400, "insufficient tokens")
    # one per user/video
    exists = db.query(Appreciation).filter_by(user_id=user.id, video_id=v.id).first()
    if exists: raise HTTPException(409, "already appreciated")
    # record + deduct
    apprec = Appreciation(user_id=user.id, video_id=v.id,
                          ip_hash=ip_hash(client_ip), source="tap")
    db.add(apprec)
    if wallet.monthly_budget > 0: wallet.monthly_budget -= 1
    else: wallet.bonus_balance -= 1
    db.commit()
    return {"ok": True}

@app.post("/ads/start")
def ad_start(inp: AdStartIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
    sess = AdSession(user_id=user.id, provider=inp.provider, status="started", reward_tokens=inp.reward_tokens)
    db.add(sess); db.commit()
    return {"ad_session_id": sess.id}

@app.post("/ads/complete")
def ad_complete(inp: AdCompleteIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # verify provider webhook/token here; enforce idempotency
    sess = db.get(AdSession, inp.ad_session_id)
    if not sess or sess.user_id != user.id: raise HTTPException(404)
    if sess.status == "completed": return {"ok": True}  # idempotent
    sess.status = "completed"
    wallet = db.query(TokenWallet).filter_by(user_id=user.id).first()
    wallet.bonus_balance += sess.reward_tokens
    db.commit()
    return {"ok": True, "bonus_added": sess.reward_tokens}

@app.post("/videos/ai-check")
def ai_check(video_id: int, db: Session = Depends(get_db)):
    # call your model / external API; here stub:
    v = db.get(Video, video_id)
    if not v: raise HTTPException(404)
    v.ai_score = 0.35  # TODO replace with real
    v.ai_label = "low"
    db.commit()
    return {"video_id": v.id, "ai_score": v.ai_score, "ai_label": v.ai_label}
