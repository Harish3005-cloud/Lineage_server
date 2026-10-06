from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import engine, Base, get_db
import app.db.models  # registers User, Project, ProjectMember on Base
from app.api.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="LINEAGE API", lifespan=lifespan)

# Register API routes
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "connected"
    }
