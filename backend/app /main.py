from fastapi import FastAPI
from app.routers.health import router as health_router

app = FastAPI(title="FairWave Backend")
app.include_router(health_router)

# add your real routers next: gifts, comments, sessions, scoring, settlement
