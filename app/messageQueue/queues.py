# app/messaging/queues.py
from enum import Enum

class QueueNames(Enum):
    TASK_ASSIGNMENT = 'task_assignment_queue'
    TASK_COMPLETION = 'task_completion_queue'
    AGENT_HEARTBEAT = 'agent_heartbeat_queue'
    AGENT_REGISTRATION = 'agent_registration_queue'
    TRANSFER_LOGS = 'transfer_logs_queue'
    ALERTS = 'alerts_queue'
    RETRY_TASKS = 'retry_tasks_queue'

class RoutingKeys(Enum):    
    TASK_ASSIGNED = 'task.assigned'
    TASK_COMPLETED = 'task.completed'
    TASK_FAILED = 'task.failed'
    AGENT_ONLINE = 'agent.online'
    AGENT_OFFLINE = 'agent.offline'
    AGENT_HEARTBEAT = 'agent.heartbeat'
    AGENT_REGISTERED = 'agent.registered'
    LOG_TRANSFER = 'log.transfer'
    ALERT_CRITICAL = 'alert.critical'
    ALERT_WARNING = 'alert.warning'
    RETRY_TASK = 'task.retry'
