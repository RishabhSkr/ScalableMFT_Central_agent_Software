# app/workers/task_scheduler.py
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.task import Task
from app.models.agent import Agent

celery_app = Celery(
    'central_workers',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.beat_schedule = {
    'check-pending-tasks': {
        'task': 'app.workers.task_scheduler.assign_pending_tasks',
        'schedule': 30.0,  # Every 30 seconds
    },
    'monitor-agent-health': {
        'task': 'app.workers.heartbeat_monitor.check_agent_heartbeats',
        'schedule': 60.0,  # Every minute
    },
    'retry-failed-tasks': {
        'task': 'app.workers.retry_handler.retry_failed_tasks',
        'schedule': 300.0,  # Every 5 minutes
    },
}

@celery_app.task
def assign_pending_tasks():
    """Find and assign pending tasks to agents"""
    db = SessionLocal()
    try:
        pending_tasks = db.query(Task).filter(
            Task.status == 'pending',
            Task.next_run_time <= datetime.utcnow()
        ).order_by(Task.priority.desc()).limit(50).all()
        
        for task in pending_tasks:
            # Check if agent is active
            agent = db.query(Agent).filter(Agent.agent_id == task.agent_id).first()
            
            if agent and agent.status == 'active':
                task.status = 'assigned'
                task.assigned_at = datetime.utcnow()
                db.commit()
                
                print(f"Task {task.task_id} assigned to agent {agent.hostname}")
        
    finally:
        db.close()
