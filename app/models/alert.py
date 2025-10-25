from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Alert(Base):
    __tablename__ = 'alerts'
    
    # Primary Key
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys (nullable to allow system-wide alerts)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.agent_id'), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.task_id'), nullable=True)
    
    # Alert Classification
    severity = Column(String(20), nullable=False)
    # Possible values: info, warning, error, critical
    
    alert_type = Column(String(50), nullable=False)
    # Possible values: agent_offline, agent_online, transfer_failed, 
    # checksum_mismatch, disk_full, high_cpu, network_issue, etc.
    
    # Alert Details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(String(100), nullable=True)  # User who resolved
    resolution_notes = Column(Text, nullable=True)
    
    # Notification Status
    notification_sent = Column(Boolean, default=False)
    notification_method = Column(String(50), nullable=True)
    # Possible values: email, sms, slack, webhook
    notification_recipients = Column(Text, nullable=True)
    # JSON array or comma-separated emails
    
    # Occurrence tracking
    occurrence_count = Column(Integer, default=1)
    first_occurrence = Column(DateTime, default=datetime.utcnow)
    last_occurrence = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    
    # Additional context
    context_json = Column(JSON, nullable=True)
    # Example: {"error_code": "ERR_CONNECTION_TIMEOUT", "retry_count": 3}
    
    def __repr__(self):
        return f"<Alert(id={self.alert_id}, type={self.alert_type}, severity={self.severity})>"
    
    def to_dict(self):
        return {
            'alert_id': str(self.alert_id),
            'agent_id': str(self.agent_id) if self.agent_id else None,
            'task_id': str(self.task_id) if self.task_id else None,
            'severity': self.severity,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'notification_sent': self.notification_sent,
            'notification_method': self.notification_method,
            'occurrence_count': self.occurrence_count,
            'first_occurrence': self.first_occurrence.isoformat(),
            'last_occurrence': self.last_occurrence.isoformat(),
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'context_json': self.context_json
        }
    
    def acknowledge(self, acknowledged_by: str):
        """Mark alert as acknowledged"""
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = acknowledged_by
    
    def resolve(self, resolved_by: str, notes: str = None):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by = resolved_by
        if notes:
            self.resolution_notes = notes
