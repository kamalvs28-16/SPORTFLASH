import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from pipeline.config import RESULTS_DIR, VIDEOS_DIR
from api.db import init_db
from api.routes import router

app = FastAPI(
    title="SPORTFLASH Player Analysis Engine API",
    description="Backend API for Player-Centric Football Analytics, Tracking, Pitch Calibration & Roster Management",
    version="3.0.0"
)

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for player photos, annotated match videos, and results
app.mount("/static/results", StaticFiles(directory=RESULTS_DIR), name="results")
app.mount("/static/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

# Include Router
app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()
    print("[INFO] SPORTFLASH Backend API v3.0 started successfully.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
