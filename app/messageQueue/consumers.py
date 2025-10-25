# app/messaging/consumers.py
import json
import pika
from sqlalchemy.orm import Session

from app.messaging.rabbitmq import rabbitmq_client
from app.messaging.queues import QueueNames, RoutingKeys
from app.database import SessionLocal
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.monitoring_service import MonitoringService
from app.services.alert_service import AlertService
from app.utils.logger import setup_logger

logger = setup_logger()


class TaskConsumer:
    """Consume and process task-related messages"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.task_service = TaskService(self.db)
    
    def start(self):
        """Start consuming task completion messages"""
        # Declare queues
        rabbitmq_client.declare_queue(
            QueueNames.TASK_COMPLETION.value,
            f"{RoutingKeys.TASK_COMPLETED.value}.#"
        )
        
        rabbitmq_client.declare_queue(
            QueueNames.RETRY_TASKS.value,
            RoutingKeys.RETRY_TASK.value
        )
        
        # Start consuming
        logger.info("Starting TaskConsumer...")
        rabbitmq_client.consume_messages(
            queue_name=QueueNames.TASK_COMPLETION.value,
            callback=self.process_task_completion
        )
    
    def process_task_completion(self, ch, method, properties, body):
        """Process task completion message"""
        try:
            message = json.loads(body)
            logger.info(f"Processing task completion: {message}")
            
            task_id = message['task_id']
            status = message['status']
            
            # Update task status in database
            self.task_service.update_task_status(task_id, status)
            
            # If failed, check if retry is needed
            if status == 'failed':
                task = self.task_service.get_task(task_id)
                if task and task.retry_count < task.max_retries:
                    self.task_service.reset_task_for_retry(task_id)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Task completion processed: {task_id}")
        
        except Exception as e:
            logger.error(f"Error processing task completion: {e}")
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


class AgentConsumer:
    """Consume and process agent-related messages"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.agent_service = AgentService(self.db)
    
    def start(self):
        """Start consuming agent messages"""
        # Declare queues
        rabbitmq_client.declare_queue(
            QueueNames.AGENT_REGISTRATION.value,
            RoutingKeys.AGENT_REGISTERED.value
        )
        
        rabbitmq_client.declare_queue(
            QueueNames.AGENT_HEARTBEAT.value,
            RoutingKeys.AGENT_HEARTBEAT.value
        )
        
        logger.info("Starting AgentConsumer...")
        rabbitmq_client.consume_messages(
            queue_name=QueueNames.AGENT_HEARTBEAT.value,
            callback=self.process_heartbeat
        )
    
    def process_heartbeat(self, ch, method, properties, body):
        """Process agent heartbeat message"""
        try:
            message = json.loads(body)
            agent_id = message['agent_id']
            status = message.get('status', 'active')
            
            # Update agent heartbeat in database
            agent = self.agent_service.get_agent(agent_id)
            if agent:
                agent.last_heartbeat = datetime.utcnow()
                agent.status = status
                self.db.commit()
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Heartbeat processed for agent: {agent_id}")
        
        except Exception as e:
            logger.error(f"Error processing heartbeat: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


class LogConsumer:
    """Consume and process transfer log messages"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.monitoring_service = MonitoringService(self.db)
    
    def start(self):
        """Start consuming log messages"""
        rabbitmq_client.declare_queue(
            QueueNames.TRANSFER_LOGS.value,
            RoutingKeys.LOG_TRANSFER.value
        )
        
        logger.info("Starting LogConsumer...")
        rabbitmq_client.consume_messages(
            queue_name=QueueNames.TRANSFER_LOGS.value,
            callback=self.process_transfer_log
        )
    
    def process_transfer_log(self, ch, method, properties, body):
        """Process transfer log message"""
        try:
            message = json.loads(body)
            log_data = message['log_data']
            
            # Save log to database
            self.monitoring_service.create_transfer_log(log_data)
            
            # Update statistics
            if log_data['status'] == 'success':
                self.monitoring_service.update_agent_stats(
                    log_data['agent_id'],
                    log_data['file_size_bytes']
                )
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Transfer log processed: {log_data['task_id']}")
        
        except Exception as e:
            logger.error(f"Error processing transfer log: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


class AlertConsumer:
    """Consume and process alert messages"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.alert_service = AlertService(self.db)
    
    def start(self):
        """Start consuming alert messages"""
        rabbitmq_client.declare_queue(
            QueueNames.ALERTS.value,
            f"{RoutingKeys.ALERT_CRITICAL.value}.#"
        )
        
        logger.info("Starting AlertConsumer...")
        rabbitmq_client.consume_messages(
            queue_name=QueueNames.ALERTS.value,
            callback=self.process_alert
        )
    
    def process_alert(self, ch, method, properties, body):
        """Process alert message"""
        try:
            message = json.loads(body)
            alert_data = message['alert_data']
            
            # Create alert in database
            self.alert_service.create_alert(**alert_data)
            
            # Send notifications (email, SMS, etc.)
            self.alert_service.send_notifications(alert_data)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Alert processed: {alert_data['alert_type']}")
        
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
