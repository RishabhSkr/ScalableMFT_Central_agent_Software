# app/workers/heartbeat_monitor.py
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.agent import Agent
from app.services.alert_service import AlertService

@celery_app.task
def check_agent_heartbeats():
    """Monitor agent heartbeats and mark inactive agents"""
    db = SessionLocal()
    try:
        threshold = datetime.utcnow() - timedelta(minutes=5)
        
        # Find agents that haven't sent heartbeat recently
        inactive_agents = db.query(Agent).filter(
            Agent.last_heartbeat < threshold,
            Agent.status == 'active'
        ).all()
        
        alert_service = AlertService(db)
        
        for agent in inactive_agents:
            agent.status = 'inactive'
            db.commit()
            
            # Create alert
            alert_service.create_alert(
                agent_id=agent.agent_id,
                severity='warning',
                alert_type='agent_offline',
                message=f"Agent {agent.hostname} has not sent heartbeat for 5+ minutes"
            )
            
            print(f"Agent {agent.hostname} marked as inactive")
    
    finally:
        db.close()
