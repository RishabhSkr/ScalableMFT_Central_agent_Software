# app/api/logs.py (Updated with RabbitMQ)
from app.messaging.producers import LogProducer, AlertProducer

@router.post("/", response_model=TransferLogResponse, status_code=201)
def submit_transfer_log(
    log_data: TransferLogCreate,
    db: Session = Depends(get_db),
    current_agent = Depends(get_current_agent)
):
    """Agent submits transfer log after completion"""
    
    # Publish log to RabbitMQ for async processing
    LogProducer.publish_transfer_log(log_data.dict())
    
    # Also process synchronously for immediate feedback
    monitoring_service = MonitoringService(db)
    
    # Validate checksum match
    checksum_valid = log_data.checksum_local == log_data.checksum_remote
    
    if not checksum_valid and log_data.status == 'success':
        log_data.status = 'failed'
        log_data.error_message = "Checksum mismatch detected"
    
    # Create log entry
    transfer_log = monitoring_service.create_transfer_log(log_data)
    
    # Publish task completion message
    TaskProducer.publish_task_completion(
        task_id=log_data.task_id,
        agent_id=log_data.agent_id,
        status=log_data.status
    )
    
    # Generate alert if failed
    if log_data.status == 'failed':
        AlertProducer.publish_alert({
            'agent_id': str(log_data.agent_id),
            'task_id': str(log_data.task_id),
            'severity': 'error',
            'alert_type': 'transfer_failed',
            'message': f"Transfer failed: {log_data.error_message}"
        })
    
    return transfer_log
