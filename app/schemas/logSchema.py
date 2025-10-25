from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

class TransferLogCreate(BaseModel):
    """Schema for creating transfer log"""
    task_id: uuid.UUID
    agent_id: uuid.UUID
    file_name: str = Field(..., min_length=1)
    file_path: Optional[str] = None
    file_size_bytes: int = Field(..., ge=0)
    compressed_size_bytes: int = Field(0, ge=0)
    checksum_algorithm: str = Field('sha256', max_length=20)
    checksum_local: Optional[str] = None
    checksum_remote: Optional[str] = None
    transfer_start: datetime
    transfer_end: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    transfer_speed_mbps: Optional[Decimal] = None
    status: str = Field(..., regex='^(success|failed|partial|aborted)$')
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_attempt: int = Field(0, ge=0)
    compression_time_seconds: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None

class TransferLogResponse(BaseModel):
    """Schema for transfer log response"""
    log_id: uuid.UUID
    task_id: uuid.UUID
    agent_id: uuid.UUID
    file_name: str
    file_size_bytes: int
    compressed_size_bytes: int
    checksum_local: Optional[str]
    checksum_remote: Optional[str]
    checksum_match: Optional[bool]
    transfer_start: datetime
    transfer_end: Optional[datetime]
    duration_seconds: Optional[int]
    transfer_speed_mbps: Optional[Decimal]
    status: str
    error_message: Optional[str]
    retry_attempt: int
    compression_ratio: Optional[Decimal]
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True
