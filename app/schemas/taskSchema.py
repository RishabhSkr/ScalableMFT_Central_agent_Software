from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class TaskCreate(BaseModel):
    """Schema for creating a task"""
    agent_id: uuid.UUID
    task_type: str = Field(..., regex='^(scheduled|on_demand|retry|manual)$')
    source_path: str = Field(..., min_length=1)
    destination_path: str = Field(..., min_length=1)
    file_pattern: Optional[str] = None
    compression_enabled: bool = True
    compression_type: Optional[str] = Field('gzip', regex='^(gzip|lz4|zip|bz2)$')
    protocol: str = Field(..., regex='^(ftp|sftp|ftps)$')
    ftp_host: Optional[str] = None
    ftp_port: Optional[int] = Field(None, ge=1, le=65535)
    ftp_username: Optional[str] = None
    ftp_password: Optional[str] = None
    schedule_cron: Optional[str] = None
    next_run_time: Optional[datetime] = None
    priority: int = Field(5, ge=1, le=10)
    max_retries: int = Field(3, ge=0, le=10)

class TaskResponse(BaseModel):
    """Schema for task response"""
    task_id: uuid.UUID
    agent_id: uuid.UUID
    task_type: str
    source_path: str
    destination_path: str
    file_pattern: Optional[str]
    compression_enabled: bool
    compression_type: Optional[str]
    protocol: str
    schedule_cron: Optional[str]
    next_run_time: Optional[datetime]
    priority: int
    max_retries: int
    retry_count: int
    status: str
    created_at: datetime
    assigned_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        orm_mode = True
        from_attributes = True

class TaskUpdate(BaseModel):
    """Schema for updating task"""
    status: Optional[str]
    priority: Optional[int] = Field(None, ge=1, le=10)
    next_run_time: Optional[datetime]
    schedule_cron: Optional[str]
