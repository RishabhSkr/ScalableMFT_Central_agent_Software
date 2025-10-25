# app/main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from app.database import get_db, engine
from app.models import agent, task, transfer_log, alert
from app.api import agents, tasks, logs, auth
from app.services import task_service, monitoring_service

# Create all tables
agent.Base.metadata.create_all(bind=engine)
task.Base.metadata.create_all(bind=engine)
transfer_log.Base.metadata.create_all(bind=engine)
alert.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FTP Transfer Central Manager", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])

@app.get("/")
def root():
    return {"message": "FTP Central Manager API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
