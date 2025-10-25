# app/services/task_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        new_task = Task(
            agent_id=task_data.agent_id,
            task_type=task_data.task_type,
            source_path=task_data.source_path,
            destination_path=task_data.destination_path,
            file_pattern=task_data.file_pattern,
            compression_enabled=task_data.compression_enabled,
            compression_type=task_data.compression_type,
            protocol=task_data.protocol,
            schedule_cron=task_data.schedule_cron,
            next_run_time=task_data.next_run_time or datetime.utcnow(),
            priority=task_data.priority,
            max_retries=task_data.max_retries,
            status='pending'
        )
        
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task
    
    def get_task(self, task_id: uuid.UUID) -> Optional[Task]:
        """Get task by ID"""
        return self.db.query(Task).filter(Task.task_id == task_id).first()
    
    def list_tasks(
        self,
        skip: int,
        limit: int,
        status_filter: Optional[str] = None,
        agent_id: Optional[uuid.UUID] = None
    ) -> List[Task]:
        """List tasks with filters"""
        query = self.db.query(Task)
        
        if status_filter:
            query = query.filter(Task.status == status_filter)
        
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
        
        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_agent_pending_tasks(self, agent_id: uuid.UUID) -> List[Task]:
        """Get pending tasks for a specific agent"""
        return self.db.query(Task).filter(
            and_(
                Task.agent_id == agent_id,
                Task.status.in_(['pending', 'assigned']),
                Task.next_run_time <= datetime.utcnow()
            )
        ).order_by(Task.priority.desc(), Task.next_run_time.asc()).all()
    
    def update_task_status(self, task_id: uuid.UUID, status: str):
        """Update task status"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            if status == 'in_progress':
                task.assigned_at = datetime.utcnow()
            elif status in ['completed', 'failed']:
                task.completed_at = datetime.utcnow()
            self.db.commit()
    
    def reset_task_for_retry(self, task_id: uuid.UUID):
        """Reset failed task for retry"""
        task = self.get_task(task_id)
        if task and task.retry_count < task.max_retries:
            task.status = 'pending'
            task.retry_count += 1
            task.next_run_time = datetime.utcnow() + timedelta(minutes=5 * task.retry_count)
            self.db.commit()
            return True
        return False
    
    def update_task(self, task_id: uuid.UUID, task_update: TaskUpdate) -> Optional[Task]:
        """Update task configuration"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete_task(self, task_id: uuid.UUID) -> bool:
        """Delete a task"""
        task = self.get_task(task_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
