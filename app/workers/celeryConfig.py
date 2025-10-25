"""
Celery configuration using Redis as broker and backend
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery instance
celery_app = Celery(
    'ftp_transfer_workers',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        'app.workers.task_scheduler.*': {'queue': 'task_queue'},
        'app.workers.heartbeat_monitor.*': {'queue': 'monitoring_queue'},
        'app.workers.retry_handler.*': {'queue': 'retry_queue'},
    },
    
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'master_name': 'mymaster'},
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    
    # Task acknowledgment
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        'assign-pending-tasks': {
            'task': 'app.workers.task_scheduler.assign_pending_tasks',
            'schedule': 30.0,  # Every 30 seconds
        },
        'check-agent-heartbeats': {
            'task': 'app.workers.heartbeat_monitor.check_agent_heartbeats',
            'schedule': 60.0,  # Every minute
        },
        'retry-failed-tasks': {
            'task': 'app.workers.retry_handler.retry_failed_tasks',
            'schedule': 300.0,  # Every 5 minutes
        },
        'cleanup-old-cache': {
            'task': 'app.workers.maintenance.cleanup_old_cache',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'generate-daily-report': {
            'task': 'app.workers.reporting.generate_daily_report',
            'schedule': crontab(hour=23, minute=55),  # Daily at 23:55
        },
    },
)

# Task decorators
@celery_app.task(bind=True, max_retries=3)
def example_task(self, arg):
    try:
        # Task logic here
        pass
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
