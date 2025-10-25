from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    
    # Primary Key
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key to Agent
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.agent_id'), nullable=False)
    
    # Task Type
    task_type = Column(String(50), nullable=False)
    # Possible values: scheduled, on_demand, retry, manual
    
    # Source and Destination
    source_path = Column(Text, nullable=False)
    destination_path = Column(Text, nullable=False)
    file_pattern = Column(String(255), nullable=True)
    # Example: "*.log", "data_*.csv"
    
    # Compression Settings
    compression_enabled = Column(Boolean, default=True)
    compression_type = Column(String(20), nullable=True)
    # Possible values: gzip, lz4, zip, bz2
    
    # Transfer Protocol
    protocol = Column(String(10), nullable=False)
    # Possible values: ftp, sftp, ftps
    
    # FTP Server Details (can be stored here or referenced from config)
    ftp_host = Column(String(255), nullable=True)
    ftp_port = Column(Integer, nullable=True)
    ftp_username = Column(String(100), nullable=True)
    ftp_password_encrypted = Column(Text, nullable=True)
    
    # Scheduling
    schedule_cron = Column(String(100), nullable=True)
    # Example: "0 */6 * * *" (every 6 hours)
    next_run_time = Column(DateTime, nullable=True)
    last_run_time = Column(DateTime, nullable=True)
    
    # Priority (1-10, higher = more important)
    priority = Column(Integer, default=5)
    
    # Retry Logic
    max_retries = Column(Integer, default=3)
    retry_count = Column(Integer, default=0)
    retry_delay_seconds = Column(Integer, default=300)  # 5 minutes
    
    # Status
    status = Column(String(30), default='pending', nullable=False)
    # Possible values: pending, assigned, in_progress, completed, failed, cancelled
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    metadata_json = Column(JSON, nullable=True)
    # Example: {"estimated_size": 2147483648, "expected_duration": 300}
    
    # Relationship
    # agent = relationship("Agent", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.task_id}, agent={self.agent_id}, status={self.status})>"
    
    def to_dict(self):
        return {
            'task_id': str(self.task_id),
            'agent_id': str(self.agent_id),
            'task_type': self.task_type,
            'source_path': self.source_path,
            'destination_path': self.destination_path,
            'file_pattern': self.file_pattern,
            'compression_enabled': self.compression_enabled,
            'compression_type': self.compression_type,
            'protocol': self.protocol,
            'schedule_cron': self.schedule_cron,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'priority': self.priority,
            'max_retries': self.max_retries,
            'retry_count': self.retry_count,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
