# app/workers/retry_handler.py
from datetime import datetime
from app.database import SessionLocal
from app.models.task import Task

@celery_app.task
def retry_failed_tasks():
    """Auto-retry failed tasks within retry limit"""
    db = SessionLocal()
    try:
        failed_tasks = db.query(Task).filter(
            Task.status == 'failed',
            Task.retry_count < Task.max_retries,
            Task.next_run_time <= datetime.utcnow()
        ).all()
        
        for task in failed_tasks:
            task.status = 'pending'
            task.retry_count += 1
            task.next_run_time = datetime.utcnow() + timedelta(minutes=5 * task.retry_count)
            db.commit()
            
            print(f"Task {task.task_id} queued for retry (attempt {task.retry_count})")
    
    finally:
        db.close()
