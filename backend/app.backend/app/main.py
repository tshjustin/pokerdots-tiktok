from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine, Base
from app.routers import health, sessions, events, comments, gifts

app = FastAPI(title="app (backend)")

# Create tables on boot (simple for beginners). Later you can switch to Alembic.
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Optional: simple constraints you can add later via migrations.

# Routes
app.include_router(health.router, prefix="")
app.include_router(sessions.router, prefix="/sessions", tags=["viewer-sessions"])
app.include_router(events.router,   prefix="/events",   tags=["engagement"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(gifts.router,    prefix="/gifts",    tags=["gifts"])
