from app.cache.cache_manager import cache_manager

class AgentService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_agent(self, agent_id: uuid.UUID) -> Optional[Agent]:
        """Get agent by ID with caching"""
        
        # Try cache first
        cached_agent = cache_manager.get_agent_status(agent_id)
        if cached_agent:
            logger.debug(f"Agent {agent_id} retrieved from cache")
            return cached_agent
        
        # Not in cache, query database
        agent = self.db.query(Agent).filter(Agent.agent_id == agent_id).first()
        
        if agent:
            # Cache for next time
            cache_manager.cache_agent_status(agent_id, agent.to_dict())
        
        return agent
    
    def update_agent_status(self, agent_id: uuid.UUID, status: str):
        """Update agent status in DB and cache"""
        agent = self.db.query(Agent).filter(Agent.agent_id == agent_id).first()
        
        if agent:
            agent.status = status
            agent.last_heartbeat = datetime.utcnow()
            self.db.commit()
            
            # Update cache
            cache_manager.cache_agent_status(agent_id, agent.to_dict())
            
            # Update active agents set
            if status == 'active':
                cache_manager.add_active_agent(agent_id)
            else:
                cache_manager.remove_active_agent(agent_id)
