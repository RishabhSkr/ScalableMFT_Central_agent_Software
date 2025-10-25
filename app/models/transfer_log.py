from sqlalchemy import Column, String, DateTime, Integer, BigInteger, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TransferLog(Base):
    __tablename__ = 'transfer_logs'
    
    # Primary Key
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.task_id'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.agent_id'), nullable=False)
    
    # File Information
    file_name = Column(Text, nullable=False)
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=False)
    compressed_size_bytes = Column(BigInteger, default=0)
    
    # Checksums for verification
    checksum_algorithm = Column(String(20), default='sha256')
    checksum_local = Column(String(64), nullable=True)
    checksum_remote = Column(String(64), nullable=True)
    checksum_match = Column(Boolean, nullable=True)
    
    # Transfer Details
    transfer_start = Column(DateTime, nullable=False)
    transfer_end = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transfer_speed_mbps = Column(Numeric(10, 2), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False)
    # Possible values: success, failed, partial, aborted
    
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Retry Information
    retry_attempt = Column(Integer, default=0)
    
    # Network Information
    source_ip = Column(INET, nullable=True)
    destination_ip = Column(INET, nullable=True)
    
    # Compression Information
    compression_ratio = Column(Numeric(5, 2), nullable=True)  # Percentage
    compression_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional metadata
    metadata_json = Column(JSON, nullable=True)
    # Example: {"chunks_transferred": 50, "network_quality": "good"}
    
    def __repr__(self):
        return f"<TransferLog(id={self.log_id}, file={self.file_name}, status={self.status})>"
    
    def to_dict(self):
        return {
            'log_id': str(self.log_id),
            'task_id': str(self.task_id),
            'agent_id': str(self.agent_id),
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'compressed_size_bytes': self.compressed_size_bytes,
            'checksum_local': self.checksum_local,
            'checksum_remote': self.checksum_remote,
            'checksum_match': self.checksum_match,
            'transfer_start': self.transfer_start.isoformat() if self.transfer_start else None,
            'transfer_end': self.transfer_end.isoformat() if self.transfer_end else None,
            'duration_seconds': self.duration_seconds,
            'transfer_speed_mbps': float(self.transfer_speed_mbps) if self.transfer_speed_mbps else None,
            'status': self.status,
            'error_message': self.error_message,
            'retry_attempt': self.retry_attempt,
            'compression_ratio': float(self.compression_ratio) if self.compression_ratio else None,
            'created_at': self.created_at.isoformat()
        }
    
    def calculate_compression_ratio(self):
        """Calculate compression ratio percentage"""
        if self.file_size_bytes > 0 and self.compressed_size_bytes > 0:
            ratio = ((self.file_size_bytes - self.compressed_size_bytes) / self.file_size_bytes) * 100
            self.compression_ratio = round(ratio, 2)
            return self.compression_ratio
        return 0
    
    def calculate_transfer_speed(self):
        """Calculate transfer speed in Mbps"""
        if self.duration_seconds and self.duration_seconds > 0:
            # Convert bytes to megabits: bytes * 8 / 1,000,000
            megabits = (self.compressed_size_bytes or self.file_size_bytes) * 8 / 1_000_000
            speed = megabits / self.duration_seconds
            self.transfer_speed_mbps = round(speed, 2)
            return self.transfer_speed_mbps
        return 0
