from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AgentRegister(BaseModel):
    """Schema for agent registration"""
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str
    mac_address: Optional[str] = Field(None, regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    os_info: Optional[str] = Field(None, max_length=100)
    agent_version: str = Field(..., max_length=20)

class AgentHeartbeat(BaseModel):
    """Schema for agent heartbeat"""
    status: str = Field(..., regex='^(active|inactive|error|maintenance)$')
    system_info: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Schema for agent response"""
    agent_id: uuid.UUID
    hostname: str
    ip_address: str
    mac_address: Optional[str]
    os_info: Optional[str]
    agent_version: Optional[str]
    status: str
    last_heartbeat: Optional[datetime]
    registration_date: datetime
    total_data_transferred: int
    total_transfers: int
    successful_transfers: int
    failed_transfers: int
    
    class Config:
        orm_mode = True
        from_attributes = True

class AgentUpdate(BaseModel):
    """Schema for updating agent"""
    status: Optional[str]
    config_json: Optional[Dict[str, Any]]
