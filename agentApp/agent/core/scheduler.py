# agent/core/scheduler.py
from pathlib import Path
from datetime import datetime
from typing import Dict
import tempfile

from agent.core.transfer_engine import TransferEngine
from agent.core.compressor import FileCompressor
from agent.core.checksum import calculate_file_checksum
from agent.communication.api_client import CentralAPIClient
from agent.config import AgentConfig
from agent.utils.logger import setup_logger

logger = setup_logger()

class TaskScheduler:
    def __init__(self, api_client: CentralAPIClient, config: AgentConfig):
        self.api_client = api_client
        self.config = config
    
    def execute_task(self, task: Dict):
        """Execute a transfer task"""
        task_id = task['task_id']
        logger.info(f"Executing task: {task_id}")
        
        try:
            # Extract task parameters
            source_path = task['source_path']
            destination_path = task['destination_path']
            protocol = task['protocol']
            compression_enabled = task.get('compression_enabled', True)
            compression_type = task.get('compression_type', 'gzip')
            
            # Prepare file for transfer
            transfer_file = source_path
            compressed_size = 0
            
            # Compress if enabled
            if compression_enabled:
                logger.info(f"Compressing file: {source_path}")
                compressed_file = tempfile.mktemp(suffix=f'.{compression_type}')
                transfer_file = FileCompressor.compress_file(
                    source_path,
                    compressed_file,
                    compression_type
                )
                
                if not transfer_file:
                    raise Exception("Compression failed")
                
                compressed_size = Path(transfer_file).stat().st_size
            
            # Calculate checksum
            logger.info("Calculating checksum...")
            local_checksum = calculate_file_checksum(transfer_file)
            
            # Upload file
            logger.info(f"Uploading to {protocol.upper()} server...")
            transfer_engine = TransferEngine(protocol)
            
            # Connect to FTP server (credentials from task or config)
            ftp_host = task.get('ftp_host', 'ftp.example.com')
            ftp_port = task.get('ftp_port', 21)
            ftp_user = task.get('ftp_username', 'user')
            ftp_pass = task.get('ftp_password', 'pass')
            
            if not transfer_engine.connect(ftp_host, ftp_port, ftp_user, ftp_pass):
                raise Exception("Failed to connect to FTP server")
            
            # Upload
            success, bytes_transferred, duration = transfer_engine.upload_file(
                transfer_file,
                destination_path
            )
            
            transfer_engine.disconnect()
            
            # Prepare log data
            log_data = {
                'task_id': task_id,
                'agent_id': self.config.agent_id,
                'file_name': Path(source_path).name,
                'file_size_bytes': Path(source_path).stat().st_size,
                'compressed_size_bytes': compressed_size if compression_enabled else 0,
                'checksum_local': local_checksum,
                'checksum_remote': local_checksum,  # Simplified - should verify remotely
                'transfer_start': datetime.utcnow().isoformat(),
                'transfer_end': datetime.utcnow().isoformat(),
                'duration_seconds': int(duration),
                'transfer_speed_mbps': round((bytes_transferred / duration / 1024 / 1024) if duration > 0 else 0, 2),
                'status': 'success' if success else 'failed',
                'error_message': None if success else 'Upload failed',
                'retry_attempt': task.get('retry_count', 0)
            }
            
            # Submit log to central server
            self.api_client.submit_transfer_log(log_data)
            
            logger.info(f"Task {task_id} completed successfully")
            
            # Cleanup compressed file
            if compression_enabled and Path(transfer_file).exists():
                Path(transfer_file).unlink()
        
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            
            # Submit failure log
            log_data = {
                'task_id': task_id,
                'agent_id': self.config.agent_id,
                'file_name': Path(source_path).name if 'source_path' in task else 'unknown',
                'file_size_bytes': 0,
                'compressed_size_bytes': 0,
                'checksum_local': '',
                'checksum_remote': '',
                'transfer_start': datetime.utcnow().isoformat(),
                'transfer_end': datetime.utcnow().isoformat(),
                'duration_seconds': 0,
                'transfer_speed_mbps': 0,
                'status': 'failed',
                'error_message': str(e),
                'retry_attempt': task.get('retry_count', 0)
            }
            
            self.api_client.submit_transfer_log(log_data)
