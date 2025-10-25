# app/services/agent_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.models.agent import Agent
from app.schemas.agent_schema import AgentRegister

class AgentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_agent(self, agent_data: AgentRegister) -> Agent:
        """Register a new agent"""
        new_agent = Agent(
            hostname=agent_data.hostname,
            ip_address=agent_data.ip_address,
            mac_address=agent_data.mac_address,
            os_info=agent_data.os_info,
            agent_version=agent_data.agent_version,
            status='active',
            last_heartbeat=datetime.utcnow()
        )
        
        self.db.add(new_agent)
        self.db.commit()
        self.db.refresh(new_agent)
        return new_agent
    
    def get_agent(self, agent_id: uuid.UUID) -> Optional[Agent]:
        """Get agent by ID"""
        return self.db.query(Agent).filter(Agent.agent_id == agent_id).first()
    
    def get_agent_by_hostname_ip(self, hostname: str, ip_address: str) -> Optional[Agent]:
        """Find agent by hostname and IP"""
        return self.db.query(Agent).filter(
            and_(Agent.hostname == hostname, Agent.ip_address == ip_address)
        ).first()
    
    def list_agents(
        self,
        skip: int,
        limit: int,
        status_filter: Optional[str] = None
    ) -> List[Agent]:
        """List all agents"""
        query = self.db.query(Agent)
        
        if status_filter:
            query = query.filter(Agent.status == status_filter)
        
        return query.offset(skip).limit(limit).all()
    
    def delete_agent(self, agent_id: uuid.UUID) -> bool:
        """Delete an agent"""
        agent = self.get_agent(agent_id)
        if agent:
            self.db.delete(agent)
            self.db.commit()
            return True
        return False
