# app/api/tasks.py (Updated with RabbitMQ)
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService
from app.messaging.producers import TaskProducer

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new transfer task"""
    task_service = TaskService(db)
    new_task = task_service.create_task(task_data)
    
    # Publish task assignment message to RabbitMQ
    TaskProducer.publish_task_assignment(
        task_id=new_task.task_id,
        agent_id=new_task.agent_id,
        task_data={
            'source_path': new_task.source_path,
            'destination_path': new_task.destination_path,
            'protocol': new_task.protocol,
            'compression_enabled': new_task.compression_enabled,
            'compression_type': new_task.compression_type
        }
    )
    
    return new_task

@router.post("/{task_id}/retry")
def retry_failed_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Manually trigger retry for a failed task"""
    task_service = TaskService(db)
    task = task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != 'failed':
        raise HTTPException(status_code=400, detail="Only failed tasks can be retried")
    
    # Reset task and publish retry message
    task_service.reset_task_for_retry(task_id)
    
    TaskProducer.publish_task_retry(
        task_id=task_id,
        agent_id=task.agent_id,
        retry_count=task.retry_count
    )
    
    return {"message": "Task queued for retry"}
