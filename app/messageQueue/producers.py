# app/messaging/producers.py
import uuid
from datetime import datetime
from typing import Dict, Any

from app.messaging.rabbitmq import rabbitmq_client
from app.messaging.queues import RoutingKeys
from app.utils.logger import setup_logger

logger = setup_logger()

class TaskProducer:
    """Publish task-related messages"""
    
    @staticmethod
    def publish_task_assignment(task_id: uuid.UUID, agent_id: uuid.UUID, task_data: Dict):
        """Notify agent about new task assignment"""
        message = {
            'task_id': str(task_id),
            'agent_id': str(agent_id),
            'task_data': task_data,
            'assigned_at': datetime.utcnow().isoformat(),
            'message_type': 'task_assignment'
        }
        
        rabbitmq_client.publish_message(
            routing_key=RoutingKeys.TASK_ASSIGNED.value,
            message=message
        )
        logger.info(f"Published task assignment: {task_id} -> Agent {agent_id}")
    
    @staticmethod
    def publish_task_completion(task_id: uuid.UUID, agent_id: uuid.UUID, status: str):
        """Notify about task completion"""
        message = {
            'task_id': str(task_id),
            'agent_id': str(agent_id),
            'status': status,
            'completed_at': datetime.utcnow().isoformat(),
            'message_type': 'task_completion'
        }
        
        routing_key = RoutingKeys.TASK_COMPLETED.value if status == 'success' else RoutingKeys.TASK_FAILED.value
        
        rabbitmq_client.publish_message(
            routing_key=routing_key,
            message=message
        )
        logger.info(f"Published task completion: {task_id} - Status: {status}")
    
    @staticmethod
    def publish_task_retry(task_id: uuid.UUID, agent_id: uuid.UUID, retry_count: int):
        """Queue task for retry"""
        message = {
            'task_id': str(task_id),
            'agent_id': str(agent_id),
            'retry_count': retry_count,
            'queued_at': datetime.utcnow().isoformat(),
            'message_type': 'task_retry'
        }
        
        rabbitmq_client.publish_message(
            routing_key=RoutingKeys.RETRY_TASK.value,
            message=message
        )
        logger.info(f"Published task retry: {task_id} (Attempt {retry_count})")


class AgentProducer:
    """Publish agent-related messages"""
    
    @staticmethod
    def publish_agent_registration(agent_id: uuid.UUID, agent_info: Dict):
        """Notify about new agent registration"""
        message = {
            'agent_id': str(agent_id),
            'agent_info': agent_info,
            'registered_at': datetime.utcnow().isoformat(),
            'message_type': 'agent_registration'
        }
        
        rabbitmq_client.publish_message(
            routing_key=RoutingKeys.AGENT_REGISTERED.value,
            message=message
        )
        logger.info(f"Published agent registration: {agent_id}")
    
    @staticmethod
    def publish_agent_status_change(agent_id: uuid.UUID, status: str, reason: str = None):
        """Notify about agent status change"""
        message = {
            'agent_id': str(agent_id),
            'status': status,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'message_type': 'agent_status_change'
        }
        
        routing_key = RoutingKeys.AGENT_ONLINE.value if status == 'active' else RoutingKeys.AGENT_OFFLINE.value
        
        rabbitmq_client.publish_message(
            routing_key=routing_key,
            message=message
        )
        logger.info(f"Published agent status change: {agent_id} -> {status}")


class LogProducer:
    """Publish log-related messages"""
    
    @staticmethod
    def publish_transfer_log(log_data: Dict):
        """Publish transfer log for async processing"""
        message = {
            'log_data': log_data,
            'received_at': datetime.utcnow().isoformat(),
            'message_type': 'transfer_log'
        }
        
        rabbitmq_client.publish_message(
            routing_key=RoutingKeys.LOG_TRANSFER.value,
            message=message
        )
        logger.debug("Published transfer log to queue")


class AlertProducer:
    """Publish alert messages"""
    
    @staticmethod
    def publish_alert(alert_data: Dict):
        """Publish alert for processing"""
        severity = alert_data.get('severity', 'info')
        
        message = {
            'alert_data': alert_data,
            'created_at': datetime.utcnow().isoformat(),
            'message_type': 'alert'
        }
        
        routing_key = RoutingKeys.ALERT_CRITICAL.value if severity == 'critical' else RoutingKeys.ALERT_WARNING.value
        
        rabbitmq_client.publish_message(
            routing_key=routing_key,
            message=message
        )
        logger.info(f"Published alert: {alert_data.get('alert_type')} - Severity: {severity}")
