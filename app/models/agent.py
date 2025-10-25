from sqlalchemy import Column, String, DateTime, Integer, BigInteger, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    
    # Primary Key
    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    hostname = Column(String(255), nullable=False)
    ip_address = Column(INET, nullable=False)
    mac_address = Column(String(17), nullable=True)
    os_info = Column(String(100), nullable=True)
    agent_version = Column(String(20), nullable=True)
    
    # Status
    status = Column(String(20), default='inactive', nullable=False)
    # Possible values: active, inactive, error, maintenance
    
    # Timestamps
    last_heartbeat = Column(DateTime, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    total_data_transferred = Column(BigInteger, default=0)  # in bytes
    total_transfers = Column(Integer, default=0)
    successful_transfers = Column(Integer, default=0)
    failed_transfers = Column(Integer, default=0)
    
    # Configuration (JSON field for flexible config)
    config_json = Column(JSON, nullable=True)
    # Example: {"max_concurrent_transfers": 3, "compression_level": 6, "retry_delay": 300}
    
    # Unique constraint
    __table_args__ = (
        {'schema': None}  # Can specify schema if needed
    )
    
    def __repr__(self):
        return f"<Agent(id={self.agent_id}, hostname={self.hostname}, status={self.status})>"
    
    def to_dict(self):
        return {
            'agent_id': str(self.agent_id),
            'hostname': self.hostname,
            'ip_address': str(self.ip_address),
            'mac_address': self.mac_address,
            'os_info': self.os_info,
            'agent_version': self.agent_version,
            'status': self.status,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'registration_date': self.registration_date.isoformat(),
            'total_data_transferred': self.total_data_transferred,
            'total_transfers': self.total_transfers,
            'successful_transfers': self.successful_transfers,
            'failed_transfers': self.failed_transfers,
            'config_json': self.config_json
        }
