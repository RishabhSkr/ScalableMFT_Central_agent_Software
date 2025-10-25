from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AlertCreate(BaseModel):
    """Schema for creating alert"""
    agent_id: Optional[uuid.UUID] = None
    task_id: Optional[uuid.UUID] = None
    severity: str = Field(..., regex='^(info|warning|error|critical)$')
    alert_type: str = Field(..., max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_method: Optional[str] = None
    notification_recipients: Optional[str] = None
    context_json: Optional[Dict[str, Any]] = None

class AlertResponse(BaseModel):
    """Schema for alert response"""
    alert_id: uuid.UUID
    agent_id: Optional[uuid.UUID]
    task_id: Optional[uuid.UUID]
    severity: str
    alert_type: str
    title: str
    message: str
    is_resolved: bool
    resolved_by: Optional[str]
    notification_sent: bool
    notification_method: Optional[str]
    occurrence_count: int
    first_occurrence: datetime
    last_occurrence: datetime
    created_at: datetime
    resolved_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    
    class Config:
        orm_mode = True
        from_attributes = True

class AlertAcknowledge(BaseModel):
    """Schema for acknowledging alert"""
    acknowledged_by: str = Field(..., min_length=1)

class AlertResolve(BaseModel):
    """Schema for resolving alert"""
    resolved_by: str = Field(..., min_length=1)
    resolution_notes: Optional[str] = None
