# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.config import settings
from app.models.agent import Agent
from jose import JWTError, jwt
router = APIRouter()
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate JWT token for agent"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Verify JWT token and return current agent"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        agent_id: str = payload.get("sub")
        
        if agent_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        agent = db.query(Agent).filter(Agent.agent_id == uuid.UUID(agent_id)).first()
        
        if agent is None:
            raise HTTPException(status_code=401, detail="Agent not found")
        
        return agent
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/token")
def login_agent(agent_id: uuid.UUID, db: Session = Depends(get_db)):
    """Agent authentication to get JWT token"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    access_token = create_access_token(data={"sub": str(agent.agent_id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "agent_id": str(agent.agent_id)
    }
