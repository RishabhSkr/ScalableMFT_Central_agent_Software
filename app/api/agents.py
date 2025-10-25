from app.cache.cacheManager import cacheManager
from fastapi import HTTPException
from fastapi import APIRouter
from fastapi import Request
from sqlalchemy.orm import Session

import uuid
from agentApp.agent.service.agentService import AgentService

router = APIRouter()
@router.post("/{agent_id}/heartbeat")
def send_heartbeat(
    agent_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    """Send heartbeat with rate limiting"""
    
    # Rate limit: 120 requests per minute per agent
    if not cacheManager.check_rate_limit(f"heartbeat:{agent_id}", 120, 60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down heartbeat frequency."
        )
    
    # Process heartbeat...
    agent_service = AgentService(db)
    agent_service.update_agent_status(agent_id, 'active')
    
    return {"status": "ok"}
