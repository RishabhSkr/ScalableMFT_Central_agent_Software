"""
Database models initialization
"""
from app.models.agent import Agent, Base as AgentBase
from app.models.task import Task, Base as TaskBase
from app.models.transfer_log import TransferLog, Base as TransferLogBase
from app.models.alert import Alert, Base as AlertBase

# Combine all bases (they should be the same Base)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

__all__ = [
    'Agent',
    'Task',
    'TransferLog',
    'Alert',
    'Base'
]
