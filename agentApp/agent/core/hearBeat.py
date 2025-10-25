# agent/core/heartbeat.py
from datetime import datetime
from agent.communication.api_client import CentralAPIClient
from agent.config import AgentConfig
from agent.utils.system_info import get_system_info
from agent.utils.logger import setup_logger

logger = setup_logger()

class HeartbeatSender:
    def __init__(self, api_client: CentralAPIClient, config: AgentConfig):
        self.api_client = api_client
        self.config = config
    
    def send(self):
        """Send heartbeat with system status"""
        try:
            system_info = get_system_info()
            
            status = 'active'  # Could be dynamic based on agent state
            
            success = self.api_client.send_heartbeat(status, system_info)
            
            if success:
                logger.debug("Heartbeat sent successfully")
            else:
                logger.warning("Heartbeat failed")
        
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
