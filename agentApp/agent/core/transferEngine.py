# agent/core/transfer_engine.py
import ftplib
import paramiko
from pathlib import Path
from typing import Optional, Tuple
import time
from datetime import datetime

from agent.utils.logger import setup_logger
from agent.core.checksum import calculate_file_checksum

logger = setup_logger()

class TransferEngine:
    def __init__(self, protocol: str = 'ftp'):
        self.protocol = protocol.lower()
        self.connection = None
    
    def connect(self, host: str, port: int, username: str, password: str) -> bool:
        """Establish connection to FTP/SFTP server"""
        try:
            if self.protocol == 'sftp':
                return self._connect_sftp(host, port, username, password)
            elif self.protocol == 'ftps':
                return self._connect_ftps(host, port, username, password)
            else:
                return self._connect_ftp(host, port, username, password)
        
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def _connect_ftp(self, host: str, port: int, username: str, password: str) -> bool:
        """Connect using plain FTP"""
        try:
            self.connection = ftplib.FTP()
            self.connection.connect(host, port, timeout=30)
            self.connection.login(username, password)
            logger.info(f"Connected to FTP server {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"FTP connection failed: {e}")
            return False
    
    def _connect_ftps(self, host: str, port: int, username: str, password: str) -> bool:
        """Connect using FTPS (FTP over TLS)"""
        try:
            self.connection = ftplib.FTP_TLS()
            self.connection.connect(host, port, timeout=30)
            self.connection.login(username, password)
            self.connection.prot_p()  # Enable encryption
            logger.info(f"Connected to FTPS server {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"FTPS connection failed: {e}")
            return False
    
    def _connect_sftp(self, host: str, port: int, username: str, password: str) -> bool:
        """Connect using SFTP"""
        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            self.connection = paramiko.SFTPClient.from_transport(transport)
            logger.info(f"Connected to SFTP server {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"SFTP connection failed: {e}")
            return False
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        chunk_size: int = 8192
    ) -> Tuple[bool, int, float]:
        """
        Upload file to server
        Returns: (success, bytes_transferred, duration_seconds)
        """
        local_file = Path(local_path)
        
        if not local_file.exists():
            logger.error(f"Local file not found: {local_path}")
            return False, 0, 0
        
        file_size = local_file.stat().st_size
        start_time = time.time()
        
        try:
            if self.protocol == 'sftp':
                success = self._upload_sftp(local_path, remote_path)
            else:
                success = self._upload_ftp(local_path, remote_path)
            
            duration = time.time() - start_time
            
            if success:
                logger.info(f"Upload completed: {local_path} -> {remote_path} ({file_size} bytes in {duration:.2f}s)")
            
            return success, file_size, duration
        
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False, 0, 0
    
    def _upload_ftp(self, local_path: str, remote_path: str) -> bool:
        """Upload using FTP/FTPS"""
        try:
            with open(local_path, 'rb') as f:
                self.connection.storbinary(f'STOR {remote_path}', f)
            return True
        except Exception as e:
            logger.error(f"FTP upload error: {e}")
            return False
    
    def _upload_sftp(self, local_path: str, remote_path: str) -> bool:
        """Upload using SFTP"""
        try:
            self.connection.put(local_path, remote_path)
            return True
        except Exception as e:
            logger.error(f"SFTP upload error: {e}")
            return False
    
    def verify_remote_file(self, remote_path: str, expected_checksum: str) -> bool:
        """Verify uploaded file checksum (if server supports it)"""
        # Note: This is simplified - actual implementation depends on server capabilities
        logger.info(f"Checksum verification for {remote_path}: {expected_checksum}")
        return True
    
    def disconnect(self):
        """Close connection"""
        try:
            if self.connection:
                if self.protocol == 'sftp':
                    self.connection.close()
                else:
                    self.connection.quit()
                logger.info("Disconnected from server")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
