from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import engine
from app.models import Base
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.skills import router as skills_router
from app.routers.clans import router as clans_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SkillBoost",
    description="A gamified skill & clan platform — learn skills, join clans, conquer the leaderboard.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(skills_router)
app.include_router(clans_router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Welcome to SkillBoost 🎮"}
